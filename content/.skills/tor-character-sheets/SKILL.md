---
name: tor-character-sheets
description: "Generate printable PDF character sheets for The One Ring 2e RPG campaign. Use this skill whenever the user asks to regenerate, update, or create character sheets, or after completing an episode and needing to update XP/stories. Triggers: character sheets, charsheets, listy postav, regenerate sheets, update sheets, XP update."
---

# TOR Character Sheet Generator

Generate 4-page-per-hero printable PDF character sheets for the TOR 2e campaign. All output is in Czech, no English text.

## When to Use

- After completing a session/episode — update XP earned, add story paragraphs for new events
- When character stats change (new skills, virtues, equipment)
- When the user says "regenerate character sheets" or "update sheets"

## Page Layout (per hero)

Each hero gets exactly 4 pages:

1. **Stats page** — Attributes, skills (3 columns), combat proficiencies, weapons & armor, useful items, keywords, relationships
2. **XP page** — XP earned table, skill cost reference, combat/valour/wisdom cost reference, personalized spending recommendations, Hobbit virtues list
3. **Story page** — Character backstory in flowing Czech prose
4. **Notes/overflow** — Continuation of story if needed, or lined notes page

## Critical Rules

1. **No future events.** Stories must only include episodes that have been PLAYED (check `Brain/TOR_project_memory.md` section 7 for episode status). Never add events from unplayed episodes.
2. **Czech only.** No English text anywhere — no parenthetical translations, no English subtitles.
3. **Header spacing.** Use 7mm header bars with 2mm+ gap before first content line.
4. **Dots for ratings.** Filled red dots for current rank, empty circles for remaining. Place dots right-aligned with `3.2mm` gap between them.
5. **DejaVu fonts** for Czech diacritics support (DV, DVB, DVI, DVC, DVCB, DVCI variants).

## Data Sources

Read these Brain files to get current character data:

- `Brain/sedrik_dobromysl.md` — Sedrik's full stats, skills, story
- `Brain/geralt_rychlonozka.md` — Geralt's full stats, skills, story
- `Brain/borek_hbitoprsty.md` — Borek's full stats, skills, story
- `Brain/TOR_project_memory.md` — Episode status, campaign state
- `Brain/rules_reference.md` — XP costs, advancement rules
- `Brain/czech_terminology_reference.md` — Czech game terms

## Generation Process

1. Read all Brain files for current character state
2. Read `references/sheet_template.md` for the data structure format
3. Build hero data dicts with all fields (see template)
4. Run the generator script: `python scripts/generate_sheets.py`
5. Copy output to `Produced adventures/Character_Sheets_v2.pdf`

If the generator script doesn't exist yet or needs updating, use `references/generator_guide.md` for the full reportlab implementation pattern.

## After Each Episode

When updating after a new episode:

1. Update `Brain/TOR_project_memory.md` — mark episode as played
2. Update each hero's Brain file — new XP, any stat changes, new story paragraphs
3. Update hero data in the generator script
4. Regenerate the PDF

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| DARK | #2C1810 | Body text |
| MID | #8B4513 | Secondary text |
| ACCENT | #B22222 | Numbers, dots, highlights |
| GRID | #D4C4B0 | Lines, empty dots |
| LIGHT | #FFF8F0 | Box backgrounds |
| HDR_BG | #3C2415 | Header bars |
| SECTION_BG | #F5EDE3 | Section backgrounds |
