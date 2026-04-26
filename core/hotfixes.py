"""Hotfix rules — overrides written by Osud (Fate) during the event.

Hotfixes live on the persistent Azure File Share at /app/data/hotfixes/.
They survive restarts and redeploys. Higher priority than ALL pravidla
(axiomy, základní, systémová, situační, rozhodnutí).

Format: HOT-NNN-<slug>.md with YAML frontmatter (id, autor, autor_role,
zapsano, nahrazuje) followed by the rule text.
"""

from __future__ import annotations

import os
import re
import threading
from datetime import datetime
from pathlib import Path

HOTFIX_DIR = Path(__file__).parent.parent / "data" / "hotfixes"

_write_lock = threading.Lock()
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str, max_len: int = 40) -> str:
    """Czech-friendly slug — strip diacritics, lowercase, dash-separated."""
    import unicodedata
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = _SLUG_RE.sub("-", norm.lower()).strip("-")
    return slug[:max_len] or "hotfix"


def _ensure_dir():
    HOTFIX_DIR.mkdir(parents=True, exist_ok=True)


def next_id() -> str:
    """Scan existing files, return next HOT-NNN id."""
    _ensure_dir()
    max_n = 0
    for f in HOTFIX_DIR.glob("HOT-*.md"):
        m = re.match(r"HOT-(\d+)", f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"HOT-{max_n + 1:03d}"


def add_hotfix(
    author_email: str,
    author_role: str,
    text: str,
    nahrazuje: str = "vše",
) -> dict:
    """Append a new hotfix file. Returns {id, path, frontmatter, text}."""
    with _write_lock:
        hot_id = next_id()
        slug = _slugify(text)
        filename = f"{hot_id}-{slug}.md"
        path = HOTFIX_DIR / filename

        zapsano = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        frontmatter = {
            "id": hot_id,
            "autor": author_email,
            "autor_role": author_role,
            "zapsano": zapsano,
            "nahrazuje": nahrazuje,
        }
        body = (
            "---\n"
            + "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
            + "\n---\n\n"
            + text.strip()
            + "\n"
        )
        # Atomic-ish: write to .tmp then rename
        tmp = path.with_suffix(".md.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(body)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    return {"id": hot_id, "path": str(path), "frontmatter": frontmatter, "text": text}


def read_all_hotfixes() -> list[dict]:
    """Return all hotfixes ordered by id, parsed into {id, autor, zapsano, nahrazuje, text}."""
    _ensure_dir()
    out = []
    for path in sorted(HOTFIX_DIR.glob("HOT-*.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        # Parse frontmatter
        m = re.match(r"---\n(.*?)\n---\n+(.*)", content, re.DOTALL)
        if not m:
            continue
        meta_block, text = m.group(1), m.group(2).strip()
        meta = {}
        for line in meta_block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        meta["text"] = text
        out.append(meta)
    return out


def format_hotfixes_for_prompt() -> str:
    """Return a markdown block to inject into the system prompt, or empty string if none."""
    rows = read_all_hotfixes()
    if not rows:
        return ""
    lines = [
        "## ⚠️ HOTFIXY — nejvyšší priorita, přepisují VŠECHNA ostatní pravidla",
        "",
        "Tyto hotfixy zapsali během hry Osudové. Pokud jakákoliv otázka spadá pod hotfix,",
        "ŘIĎ SE HOTFIXEM. Vždy uveď, že odpovídáš podle hotfixu (např. „Podle hotfixu HOT-003…").",
        "",
    ]
    for h in rows:
        lines.append(f"### {h.get('id','?')} (zapsal {h.get('autor','?')} dne {h.get('zapsano','?')})")
        nahr = h.get("nahrazuje", "vše")
        lines.append(f"*Nahrazuje:* {nahr}")
        lines.append("")
        lines.append(h.get("text", ""))
        lines.append("")
    return "\n".join(lines)
