"""Question logger — records user queries for review and improvement.

JSONL file backed (append-only), works on Azure Files / SMB.
"""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

# Stored alongside users.json on the same data volume.
LOG_PATH = Path(__file__).parent.parent / "data" / "questions.jsonl"
LEGACY_DB_PATH = Path(__file__).parent.parent / "data" / "users.db"

_write_lock = threading.Lock()


def _migrate_from_sqlite():
    """One-time migration: import questions table from legacy users.db."""
    if not LEGACY_DB_PATH.exists() or LOG_PATH.exists():
        return
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(LEGACY_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = list(conn.execute("SELECT * FROM questions ORDER BY id"))
        except sqlite3.OperationalError:
            return
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for r in rows:
            d = {k: r[k] for k in r.keys() if k != "id"}
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


async def init_question_log():
    """Ensure log file exists. Migrate from SQLite if legacy db is present."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(_migrate_from_sqlite)
    if not LOG_PATH.exists():
        LOG_PATH.touch()


def _append_sync(record: dict):
    with _write_lock:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())


async def log_question(email: str, bot: str, question: str, answer: str | None = None):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email": email,
        "bot": bot,
        "question": question,
        "answer": answer,
    }
    await asyncio.to_thread(_append_sync, record)


def _read_all_sync() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    out = []
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


async def get_recent_questions(limit: int = 10, bot: str | None = None) -> str:
    rows = await asyncio.to_thread(_read_all_sync)
    if bot:
        rows = [r for r in rows if r.get("bot") == bot]
    rows = rows[-limit:]

    if not rows:
        return "Zatím žádné dotazy."

    lines = [f"*Posledních {len(rows)} dotazů:*\n"]
    for r in rows:
        ts = (r.get("timestamp") or "")[5:16]  # MM-DD HH:MM
        email_short = (r.get("email") or "").split("@")[0]
        bot_tag = "📖" if r.get("bot") == "Rulemaster" else "🌍"
        q = r.get("question", "")
        q = q[:80] + ("..." if len(q) > 80 else "")
        lines.append(f"{bot_tag} `{ts}` *{email_short}*: {q}")

    return "\n".join(lines)
