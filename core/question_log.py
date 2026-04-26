"""Question logger — records user queries for review and improvement."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


async def init_question_log():
    """Create the questions table if needed."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Azure Files / SMB compatibility: no WAL, wait on transient locks.
        await db.execute("PRAGMA journal_mode = DELETE")
        await db.execute("PRAGMA busy_timeout = 5000")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                email TEXT NOT NULL,
                bot TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT
            )
        """)
        await db.commit()


async def log_question(email: str, bot: str, question: str, answer: str | None = None):
    """Log a user question."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO questions (timestamp, email, bot, question, answer) VALUES (?, ?, ?, ?, ?)",
            (timestamp, email, bot, question, answer),
        )
        await db.commit()


async def get_recent_questions(limit: int = 10, bot: str | None = None) -> str:
    """Return recent questions as formatted text."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if bot:
            query = "SELECT * FROM questions WHERE bot = ? ORDER BY id DESC LIMIT ?"
            params = (bot, limit)
        else:
            query = "SELECT * FROM questions ORDER BY id DESC LIMIT ?"
            params = (limit,)
        async with db.execute(query, params) as cursor:
            rows = [dict(row) async for row in cursor]

    if not rows:
        return "Zatím žádné dotazy."

    lines = [f"*Posledních {len(rows)} dotazů:*\n"]
    for r in reversed(rows):
        ts = r["timestamp"][5:16]  # MM-DD HH:MM
        email_short = r["email"].split("@")[0]
        bot_tag = "📖" if r["bot"] == "Rulemaster" else "🌍"
        q = r["question"][:80] + ("..." if len(r["question"]) > 80 else "")
        lines.append(f"{bot_tag} `{ts}` *{email_short}*: {q}")

    return "\n".join(lines)
