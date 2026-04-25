"""Organizer notes — append-only markdown inbox for later processing."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

NOTES_FILE = Path(__file__).parent.parent / "data" / "notes.md"

# Triggers for free-text note detection (case-insensitive)
# Handles háček variants (zapiš/zapis), "si"/"že"/colon, and common phrasings
_NOTE_TRIGGERS = [
    re.compile(r"^zapi[sš]\s+si\s+", re.IGNORECASE),
    re.compile(r"^zapi[sš]\s+[žz]e\s+", re.IGNORECASE),
    re.compile(r"^zapi[sš]:\s*", re.IGNORECASE),
    re.compile(r"^pozn[aá]mka:\s*", re.IGNORECASE),
    re.compile(r"^take\s+a\s+note\s+", re.IGNORECASE),
    re.compile(r"^note:\s*", re.IGNORECASE),
]


def detect_note(text: str) -> str | None:
    """If text starts with a note trigger, return the note body. Otherwise None."""
    for pattern in _NOTE_TRIGGERS:
        m = pattern.match(text)
        if m:
            body = text[m.end():].strip()
            return body if body else None
    return None


def save_note(email: str, text: str, source: str = "telegram") -> str:
    """Append a note to the markdown file. Returns confirmation message."""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Create file with header if it doesn't exist
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text(
            "# Poznámky organizátorů\n\n"
            "Inbox pro poznámky z Telegram/WhatsApp botů.\n"
            "Zpracuj později: vytvoř úkol v Bači, přidej do brain/, nebo jen archivuj.\n\n",
            encoding="utf-8",
        )

    entry = (
        f"---\n\n"
        f"## {timestamp} — {email} ({source})\n\n"
        f"{text}\n\n"
    )

    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    return f"Zapsáno ({timestamp})."


def list_notes(limit: int = 5) -> str:
    """Return the last N notes as formatted text."""
    if not NOTES_FILE.exists():
        return "Zatím žádné poznámky."

    content = NOTES_FILE.read_text(encoding="utf-8")
    # Split by --- separator, filter out header
    sections = [s.strip() for s in content.split("---") if s.strip().startswith("##")]

    if not sections:
        return "Zatím žádné poznámky."

    recent = sections[-limit:]
    total = len(sections)
    header = f"*Poznámky ({total} celkem, posledních {len(recent)}):*\n\n"
    return header + "\n\n---\n\n".join(recent)
