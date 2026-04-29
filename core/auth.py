"""Authentication — email verification and user store (multi-channel).

JSON-file backed storage (compatible with Azure Files / SMB, where SQLite
locking semantics don't work reliably).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
import tempfile
import time
from pathlib import Path

import aiohttp
from azure.communication.email import EmailClient

logger = logging.getLogger(__name__)


class UserStore:
    """JSON-file store for channel user <-> email mapping.

    File layout: dict keyed by "{channel_type}:{channel_id}" with user records
    as values. Atomic writes via tempfile + rename.

    Pending verification codes are persisted as one file per user under a
    sibling ``pending_codes/`` directory so they survive restarts AND remain
    valid across multiple replicas — webhook delivery for the same user can
    land on a different replica than the one that generated the code.

    Per-file storage avoids the read-modify-write races a single shared map
    would otherwise have: replicas A and B writing for two different users
    never touch the same file, so neither can clobber the other's update.
    Azure Files SMB also handles per-file ops cleanly while struggling with
    shared-file locking — same reason SQLite was retired here.
    """

    def __init__(self, db_path: Path):
        # Accept legacy .db path; transparently use .json next to it.
        db_path = Path(db_path)
        self.json_path = db_path.with_suffix(".json") if db_path.suffix == ".db" else db_path
        self.legacy_db_path = db_path if db_path.suffix == ".db" else None
        self.pending_codes_dir = self.json_path.parent / "pending_codes"
        self._lock = asyncio.Lock()

    async def init(self):
        """Ensure the JSON file exists. One-time migrate from .db if present."""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        if self.json_path.exists():
            return
        # First run: try migrating from legacy SQLite .db if it's there.
        if self.legacy_db_path and self.legacy_db_path.exists():
            await asyncio.to_thread(self._migrate_from_sqlite)
        else:
            await asyncio.to_thread(self._atomic_write, {})

    def _migrate_from_sqlite(self):
        import sqlite3
        users = {}
        try:
            with sqlite3.connect(self.legacy_db_path) as conn:
                conn.row_factory = sqlite3.Row
                for row in conn.execute("SELECT * FROM users"):
                    key = f"{row['channel_type']}:{row['channel_id']}"
                    users[key] = dict(row)
        except sqlite3.OperationalError:
            # Legacy db exists but has no users table (e.g. a leftover empty file).
            pass
        self._atomic_write(users)

    def _atomic_write(self, data: dict):
        tmp = self.json_path.with_suffix(self.json_path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.json_path)

    def _read_sync(self) -> dict:
        if not self.json_path.exists():
            return {}
        with open(self.json_path, encoding="utf-8") as f:
            return json.load(f)

    def _key(self, channel_type: str, channel_id: str) -> str:
        return f"{channel_type}:{channel_id}"

    async def get_user(self, channel_type: str, channel_id: str) -> dict | None:
        async with self._lock:
            data = await asyncio.to_thread(self._read_sync)
        return data.get(self._key(channel_type, channel_id))

    async def save_user(
        self, channel_type: str, channel_id: str, email: str,
        role: str = "hráč", postava: str | None = None, frakce: str | None = None,
    ):
        async with self._lock:
            data = await asyncio.to_thread(self._read_sync)
            data[self._key(channel_type, channel_id)] = {
                "channel_type": channel_type,
                "channel_id": channel_id,
                "email": email,
                "role": role,
                "postava": postava,
                "frakce": frakce,
                "verified_at": time.time(),
            }
            await asyncio.to_thread(self._atomic_write, data)

    async def list_users(self) -> list[dict]:
        async with self._lock:
            data = await asyncio.to_thread(self._read_sync)
        return sorted(data.values(), key=lambda u: u.get("verified_at", 0), reverse=True)

    # ----------------------------------------------------------------
    # Pending verification codes — persisted on disk as one file per
    # user under pending_codes/. Per-file storage means concurrent
    # writers for different users never touch the same file, so two
    # replicas can't clobber each other's pending records.
    # ----------------------------------------------------------------

    # Channel type and channel id are alphanumeric in practice (telegram tg_id
    # is digits, whatsapp uses a phone number). The key separator ':' is the
    # one character that's not safe in a filename, so we substitute. The full
    # filter strips anything else outside [A-Za-z0-9._-] as a defensive measure.
    _SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]")

    def _pending_file_for(self, channel_type: str, channel_id: str) -> Path:
        raw_key = self._key(channel_type, channel_id)
        safe = self._SAFE_FILENAME_RE.sub("_", raw_key)
        return self.pending_codes_dir / f"{safe}.json"

    def _read_pending_record_sync(self, path: Path) -> dict | None:
        """Read one pending-code file. Returns None if missing/corrupt/invalid.

        Invalid records (wrong types, missing fields) are deleted as a
        defensive cleanup so the dir doesn't accumulate junk.
        """
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                record = json.load(f)
        except (OSError, json.JSONDecodeError):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            return None
        if not isinstance(record, dict):
            return None
        code = record.get("code")
        email = record.get("email")
        created_at = record.get("created_at")
        if not (isinstance(code, str) and code and isinstance(email, str) and email):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            return None
        try:
            float(created_at)
        except (TypeError, ValueError):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            return None
        return record

    def _atomic_write_pending_record_sync(self, path: Path, record: dict):
        """Atomic write via a unique tempfile in the same directory + os.replace.

        The temp filename includes a random suffix so concurrent writers (even
        for the same user — unlikely but possible) don't trash each other's
        in-progress files before the rename.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=path.name + ".", suffix=".tmp", dir=str(path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            os.replace(tmp_name, path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

    def _delete_pending_sync(self, path: Path):
        try:
            path.unlink(missing_ok=True)
        except OSError as e:
            logger.warning("Could not delete pending code file %s: %s", path, e)

    async def generate_code(self, channel_type: str, channel_id: str, email: str) -> str:
        path = self._pending_file_for(channel_type, channel_id)
        code = f"{random.randint(100000, 999999)}"
        record = {
            "email": email,
            "code": code,
            "created_at": time.time(),
        }
        await asyncio.to_thread(self._atomic_write_pending_record_sync, path, record)
        return code

    async def verify_code(
        self, channel_type: str, channel_id: str, code: str, expiry_minutes: int = 10,
    ) -> str | None:
        path = self._pending_file_for(channel_type, channel_id)
        record = await asyncio.to_thread(self._read_pending_record_sync, path)
        if record is None:
            return None
        stored_code = record["code"]
        stored_email = record["email"]
        timestamp = float(record["created_at"])
        expired = time.time() - timestamp > expiry_minutes * 60
        matched = code.strip() == stored_code
        # Consume on successful match OR on expiry. Keep on simple mismatch
        # so the user can retry within the expiry window.
        if expired or matched:
            await asyncio.to_thread(self._delete_pending_sync, path)
        if expired or not matched:
            return None
        return stored_email


def send_verification_email(
    connection_string: str,
    sender_address: str,
    to_email: str,
    code: str,
):
    """Send verification code via Azure Communication Email."""
    client = EmailClient.from_connection_string(connection_string)

    message = {
        "senderAddress": sender_address,
        "recipients": {
            "to": [{"address": to_email}],
        },
        "content": {
            "subject": "Ovčina Bot — ověřovací kód",
            "plainText": (
                f"Ahoj!\n\n"
                f"Tvůj ověřovací kód je: {code}\n\n"
                f"Kód je platný 10 minut.\n\n"
                f"— Ovčina Bot"
            ),
        },
    }

    poller = client.begin_send(message)
    poller.result()


async def check_registration(api_url: str, api_key: str, email: str, game_id: str) -> bool:
    """Check if email is registered via registrace API."""
    url = f"{api_url}/api/v1/registrations/check"
    params = {"email": email, "gameId": game_id}
    headers = {"X-Api-Key": api_key}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("isRegistered", False)
    except Exception:
        pass
    return False


async def lookup_user_character(
    api_url: str, integration_api_key: str, email: str, game_id,
) -> str | None:
    """Look up the player's character name from registrace's game-info endpoint.

    Returns the first non-null `characterName` found among the email's attendees
    for the given game, or None if nothing matches. Uses the integration API key
    (the same one RegistraceClient uses), not the public api_key.

    Heuristic: families register multiple attendees under one email (parent
    registers kids); we take the first attendee with a `characterName` set.
    Imperfect for multi-kid families — better than 'neznámý z frakce neznámé'.
    """
    url = f"{api_url}/api/v1/users/{email}/game-info"
    params = {"gameId": game_id}
    headers = {"X-Api-Key": integration_api_key}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, ssl=False) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
    except Exception:
        return None

    if not data:
        return None
    for attendee in data.get("attendees") or []:
        name = (attendee or {}).get("characterName")
        if name:
            return name
    return None
