"""Sync content from OneDrive working copy → this repo's content/ folder.

Run via `sync.bat` at the repo root (which then commits + pushes).

Mirror rules:
- pravidla, .skills, brain, knowledge-base — full copy of all files
- games/<active-game>/ — text files only (.md/.txt/.yaml/.json) — skips Stashes,
  Tisky, big PDFs, Excel sheets, JPEGs which are organizer-only printouts.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
SRC = Path(r"C:\Users\TomášPajonk\OneDrive - SolverTech s.r.o\Bridge\Ovčina")

ACTIVE_GAME = "2026 05 01 Balinova pozvánka"
TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json"}
IGNORE_DIRS = {"__pycache__", ".git"}


def wipe_dir(p: Path):
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)
    p.mkdir(parents=True, exist_ok=True)


def copy_full(name: str):
    src = SRC / name
    dst = CONTENT / name
    if not src.exists():
        print(f"  ⚠ {name}: source missing at {src}")
        return
    wipe_dir(dst)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        rel = Path(root).relative_to(src)
        target_dir = dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(Path(root) / f, target_dir / f)
    print(f"  ✓ {name}")


def copy_active_game_text_only():
    src = SRC / "games" / ACTIVE_GAME
    dst = CONTENT / "games" / ACTIVE_GAME
    if not src.exists():
        print(f"  ⚠ active game missing at {src}")
        return
    wipe_dir(dst)
    count = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        rel = Path(root).relative_to(src)
        for f in files:
            if Path(f).suffix.lower() not in TEXT_EXTS:
                continue
            target_dir = dst / rel
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(root) / f, target_dir / f)
            count += 1
    print(f"  ✓ games/{ACTIVE_GAME} ({count} text files)")


def main():
    print(f"Syncing OneDrive → {CONTENT}\n")
    CONTENT.mkdir(exist_ok=True)
    for name in ("pravidla", ".skills", "brain", "knowledge-base"):
        copy_full(name)
    copy_active_game_text_only()
    print("\nDone. Commit + push happens next.")


if __name__ == "__main__":
    main()
