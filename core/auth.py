"""Authentication — email verification and user store (multi-channel).

JSON-file backed storage (compatible with Azure Files / SMB, where SQLite
locking semantics don't work reliably).
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import time
from pathlib import Path

import aiohttp
from azure.communication.email import EmailClient


class UserStore:
    """JSON-file store for channel user <-> email mapping.

    File layout: dict keyed by "{channel_type}:{channel_id}" with user records
    as values. Atomic writes via tempfile + rename.
    """

    def __init__(self, db_path: Path):
        # Accept legacy .db path; transparently use .json next to it.
        db_path = Path(db_path)
        self.json_path = db_path.with_suffix(".json") if db_path.suffix == ".db" else db_path
        self.legacy_db_path = db_path if db_path.suffix == ".db" else None
        self._pending_codes: dict[str, tuple[str, str, float]] = {}
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

    def generate_code(self, channel_type: str, channel_id: str, email: str) -> str:
        key = self._key(channel_type, channel_id)
        code = f"{random.randint(100000, 999999)}"
        self._pending_codes[key] = (email, code, time.time())
        return code

    def verify_code(self, channel_type: str, channel_id: str, code: str, expiry_minutes: int = 10) -> str | None:
        key = self._key(channel_type, channel_id)
        pending = self._pending_codes.get(key)
        if not pending:
            return None
        email, stored_code, timestamp = pending
        if time.time() - timestamp > expiry_minutes * 60:
            del self._pending_codes[key]
            return None
        if code.strip() == stored_code:
            del self._pending_codes[key]
            return email
        return None


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
