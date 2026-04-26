"""Authentication — email verification and user store (multi-channel)."""

from __future__ import annotations

import random
import time
from pathlib import Path

import aiosqlite
import aiohttp
from azure.communication.email import EmailClient


class UserStore:
    """SQLite store for channel user <-> email mapping."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._pending_codes: dict[str, tuple[str, str, float]] = {}

    async def init(self):
        """Create tables if needed."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            # Azure Files / SMB doesn't support SQLite WAL locking — use rollback journal.
            # Setting is persisted in the DB file header so future connections inherit it.
            await db.execute("PRAGMA journal_mode = DELETE")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    channel_type TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'hráč',
                    postava TEXT,
                    frakce TEXT,
                    verified_at REAL NOT NULL,
                    PRIMARY KEY (channel_type, channel_id)
                )
            """)
            await db.commit()

    def _key(self, channel_type: str, channel_id: str) -> str:
        return f"{channel_type}:{channel_id}"

    async def get_user(self, channel_type: str, channel_id: str) -> dict | None:
        """Get user by channel type and ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE channel_type = ? AND channel_id = ?",
                (channel_type, channel_id),
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def save_user(
        self, channel_type: str, channel_id: str, email: str,
        role: str = "hráč", postava: str | None = None, frakce: str | None = None,
    ):
        """Save or update a verified user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO users (channel_type, channel_id, email, role, postava, frakce, verified_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(channel_type, channel_id)
                   DO UPDATE SET email=?, role=?, postava=?, frakce=?, verified_at=?""",
                (channel_type, channel_id, email, role, postava, frakce, time.time(),
                 email, role, postava, frakce, time.time()),
            )
            await db.commit()

    async def list_users(self) -> list[dict]:
        """List all verified users."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users ORDER BY verified_at DESC") as cursor:
                return [dict(row) async for row in cursor]

    def generate_code(self, channel_type: str, channel_id: str, email: str) -> str:
        """Generate a 6-digit verification code."""
        key = self._key(channel_type, channel_id)
        code = f"{random.randint(100000, 999999)}"
        self._pending_codes[key] = (email, code, time.time())
        return code

    def verify_code(self, channel_type: str, channel_id: str, code: str, expiry_minutes: int = 10) -> str | None:
        """Verify a code. Returns email if valid, None if not."""
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
