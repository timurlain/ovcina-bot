"""Backfill missing postava on existing user records.

Reads users.json from the bot's persistent storage (Azure Files share or local
file), looks up each hráč's character from registrace via game-info, writes the
result back. Organizer records are skipped (they route to the GM prompt and
don't read postava).

Usage (against a local copy):

    python scripts/backfill-postava.py users.json

Usage (against Azure Files — download, run, upload):

    STORAGE_KEY=$(az storage account keys list -g ovcina -n ovcinahrastorage \\
        --query "[0].value" -o tsv)
    az storage file download -s bot-data --account-name ovcinahrastorage \\
        --account-key "$STORAGE_KEY" --path users.json --dest /tmp/users.json
    python scripts/backfill-postava.py /tmp/users.json
    az storage file upload -s bot-data --account-name ovcinahrastorage \\
        --account-key "$STORAGE_KEY" --source /tmp/users.json

Reads `REGISTRACE_API_URL`, `REGISTRACE_INTEGRATION_KEY`, `REGISTRACE_GAME_ID`
from environment, falling back to the values in config.yaml.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# Make `core` importable when run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.auth import lookup_user_character  # noqa: E402


def _load_config_defaults() -> dict:
    """Pull api_url + game_id from config.yaml so the script is one-arg."""
    try:
        import yaml
    except ImportError:
        return {}
    cfg_path = Path(__file__).resolve().parent.parent / "config.yaml"
    if not cfg_path.exists():
        return {}
    with cfg_path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    reg = cfg.get("registrace", {}) or {}
    return {
        "api_url": reg.get("api_url"),
        "game_id": reg.get("game_id"),
    }


async def backfill(users_path: Path, api_url: str, integration_key: str, game_id) -> int:
    data = json.loads(users_path.read_text(encoding="utf-8"))

    candidates = [
        (key, rec) for key, rec in data.items()
        if rec.get("role") == "hráč" and not rec.get("postava")
    ]
    print(f"Found {len(candidates)} hráč records with no postava (out of {len(data)} total).")

    updated = 0
    for key, rec in candidates:
        email = rec.get("email")
        if not email:
            print(f"  skip {key}: no email")
            continue
        postava = await lookup_user_character(api_url, integration_key, email, game_id)
        if postava:
            rec["postava"] = postava
            updated += 1
            print(f"  ✓ {email} → {postava}")
        else:
            print(f"  ✗ {email} → no character found")

    if updated:
        # Atomic write — same pattern as UserStore._atomic_write.
        tmp = users_path.with_suffix(users_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, users_path)
        print(f"\nUpdated {updated} record(s); wrote {users_path}.")
    else:
        print("\nNo updates to write.")
    return updated


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/backfill-postava.py <users.json>")
        sys.exit(2)
    users_path = Path(sys.argv[1])
    if not users_path.exists():
        print(f"Not found: {users_path}")
        sys.exit(2)

    defaults = _load_config_defaults()
    api_url = os.environ.get("REGISTRACE_API_URL") or defaults.get("api_url")
    integration_key = os.environ.get("REGISTRACE_INTEGRATION_KEY")
    game_id = os.environ.get("REGISTRACE_GAME_ID") or defaults.get("game_id")

    if not api_url or not integration_key or not game_id:
        print("Missing config. Set REGISTRACE_API_URL / REGISTRACE_INTEGRATION_KEY / REGISTRACE_GAME_ID")
        print("(api_url + game_id can also come from config.yaml; integration key MUST be in env).")
        sys.exit(2)

    asyncio.run(backfill(users_path, api_url, integration_key, game_id))


if __name__ == "__main__":
    main()
