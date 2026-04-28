"""TIFF/JPG -> WebP starter pack for the bookish player rulebook.

Run from this directory:
    py -3 convert_cards_starter.py

Outputs into ./hrac/cards-starter/ — 11 cards used by the kid-facing
rules (weapons, materials, soul). Re-run any time; output is overwritten.
"""

import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KARTICKY = Path(
    r"C:\Users\TomášPajonk\OneDrive - SolverTech s.r.o\Bridge\Ovčina\games\karticky"
)
OUT = Path(__file__).parent / "hrac" / "cards-starter"

# (source relative to KARTICKY, output stem)
CARDS = [
    ("zbrane/zbrane/tiff/dyka.tif",        "dyka"),
    ("zbrane/zbrane/tiff/kratky mec.tif",  "kratky-mec"),
    ("zbrane/zbrane/tiff/bastard.tif",     "bastard"),
    ("zbrane/zbrane/tiff/hul.tif",         "hul"),
    ("zbrane/zbrane/tiff/stit.tif",        "stit"),
    ("predmety/zlato.tif",                 "zlato"),
    ("predmety/stribro.tif",               "stribro"),
    ("predmety/drahokamy.jpg",             "drahokamy"),
    ("predmety/zivoty.tif",                "zivoty"),
    ("predmety/krystaly.tif",              "krystaly"),
    ("predmety/biliny.tif",                "byliny"),  # source filename is misspelled
]

MAX_LONG_EDGE = 800
QUALITY = 85


def convert_one(src: Path, dst: Path) -> tuple[int, int, int]:
    with Image.open(src) as im:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.mode else "RGB")
        w, h = im.size
        long_edge = max(w, h)
        if long_edge > MAX_LONG_EDGE:
            scale = MAX_LONG_EDGE / long_edge
            im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        im.save(dst, format="WEBP", quality=QUALITY, method=6)
    return w, h, dst.stat().st_size


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Output: {OUT}")
    print(f"Source root: {KARTICKY}\n")

    missing: list[str] = []
    for rel, stem in CARDS:
        src = KARTICKY / rel
        dst = OUT / f"{stem}.webp"
        if not src.exists():
            missing.append(rel)
            print(f"  MISS  {rel}")
            continue
        w, h, size = convert_one(src, dst)
        print(f"  OK    {stem:<14} {w}x{h} -> {dst.name} ({size // 1024} kB)")

    print()
    if missing:
        print(f"WARN: {len(missing)} source(s) missing — see above.")
    else:
        print(f"hotovo. {len(CARDS)} cards in {OUT}")


if __name__ == "__main__":
    main()
