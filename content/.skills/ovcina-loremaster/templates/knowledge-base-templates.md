# Knowledge Base Templates

These are starter templates for the Ovčina knowledge base. Copy them into
`knowledge-base/` next to the SKILL.md and fill them with your content.

Run `ovcina-researcher` on your existing materials first, then organize the
extracted content into these templates.

---

## world-bible.md

```markdown
# Svět Ovčiny — World Bible

> Last updated: [date]
> Maintainer: [name]

## Éra a kontext
[When does the current story take place? What year, what age? What is the
state of the world — peace, war, twilight between? What are the major
tensions driving the current era?]

## Základní pravidla světa (World Ground Rules)
Things that are ALWAYS true:
- [e.g., Evil cannot create, only corrupt]
- [e.g., Magic is rare and costly]
- [e.g., The world has a moral order]

Things that are NEVER true:
- [e.g., No character is irredeemably evil from birth]
- [e.g., No instant teleportation — travel always takes time]
- [e.g., No resurrection without profound cost]

## Tone Boundaries
- Maximum darkness: [describe the darkest a scene can get]
- Always present: [hope, fellowship, courage — even in the worst moments]
- Never present: [graphic violence, cruelty for entertainment, despair
  without any light]

## Geografie (přehled)
[High-level map description. Reference the physical map file if one exists.
List major regions with 1-2 sentence descriptions. Detailed entries go in
locations.md.]

## Národy a frakce (přehled)
[List all factions with a one-line description and allegiance status.
Detailed entries go in factions.md.]

## Zasazené semínka (Planted Seeds)
Track hints, prophecies, and unresolved threads across games:

| Seed | Planted in | Status | Notes |
|------|-----------|--------|-------|
| [mystery/hint] | Game N | open / resolved | [context] |
```

---

## characters.md

```markdown
# Postavy Ovčiny — Character Registry

> Canon characters only. Organize by faction, then alphabetically.

## [Faction Name]

### [Character Name]
- **Skloňování:** [Nom] / [Gen] / [Dat] / [Acc] / [Voc] / [Loc] / [Ins]
- **Role:** [quest-giver / ally / antagonist / neutral / wild card]
- **Location:** [where they're usually found]
- **First appeared:** Game [N]
- **Status:** [alive / dead / missing / unknown]
- **What they love:** [core motivation]
- **What they fear:** [vulnerability]
- **Appearance:** [2-3 sentences for costuming reference]
- **Voice:** [speech register, verbal tics, signature phrases]
- **Key relationships:** [allies, enemies, complicated ties]
- **Known to players:** [what the players know about them]
- **Secret:** [what the players don't know yet]

[Repeat for each character]
```

---

## locations.md

```markdown
# Místa Ovčiny — Geography & Locations

> Organize by region. Include travel times between major locations.

## [Region Name]

### [Place Name]
- **Přídavné jméno:** [adjectival form, e.g., hůrecký]
- **Type:** [settlement / wilderness / ruin / dungeon / sacred site]
- **Region:** [parent region]
- **Description:** [what it looks like, what it feels like]
- **History:** [why it exists, who built it, what happened here]
- **Current state:** [inhabited / abandoned / contested / hidden]
- **Notable features:** [landmarks, resources, dangers]
- **Connected to:** [nearby locations with approximate travel times]
- **Used in:** Game [N] — [brief note on how]

## Travel Times

| From | To | On foot | Mounted | Notes |
|------|----|---------|---------|-------|
| [A] | [B] | [hours] | [hours] | [terrain notes] |
```

---

## creatures.md

```markdown
# Bestiář Ovčiny — Bestiary

> Organize by habitat, then by threat level.

## [Habitat: e.g., Hory / Lesy / Podzemí / Bažiny]

### [Czech Creature Name] / [Common Name]
- **Origin:** [corrupted from what? created by whom? natural?]
- **Habitat:** [specific locations where found]
- **Behavior:** [hunting patterns, social structure, intelligence]
- **Appearance:** [description for LARP costuming]
- **Weakness:** [how to defeat — not just "damage" but story weakness]
- **Lore:** [what this creature tells us about the world]
- **Game stats:** [FOR RULEMASTER]
- **First appeared:** Game [N]
- **Encounter notes:** [best used as ambush/boss/puzzle/etc.]
```

---

## history.md

```markdown
# Historie Ovčiny — Timeline

> Chronological. Mark events that players witnessed vs. backstory.

## [Era / Age Name]

### [Year or Period]
- **Event:** [what happened]
- **Participants:** [who was involved]
- **Consequences:** [what changed in the world]
- **Player-witnessed:** yes / no (Game [N]) / backstory only
- **Sources:** [which documents establish this]
```

---

## factions.md

```markdown
# Frakce Ovčiny — Factions & Allegiances

## [Faction Name]
- **Territory:** [where they control or inhabit]
- **Culture:** [values, customs, aesthetic]
- **Government:** [how they're organized, who leads]
- **Current leader:** [link to characters.md]
- **Military strength:** [rough sense of power]
- **Playable:** yes / no [can LARP players join this faction?]
- **Relationships:**
  - [Faction X]: [ally / enemy / neutral / complicated] — [why]
  - [Faction Y]: [ally / enemy / neutral / complicated] — [why]
- **Current goals:** [what they're trying to achieve]
- **Internal tensions:** [fractures, dissent, competing agendas]
```

---

## glossary.md

```markdown
# Slovníček Ovčiny — Glossary & Declensions

> Every proper noun in the Ovčina canon. Keep alphabetical.
> This is the CANONICAL spelling reference. If it's not here, it's not canon.

## Osoby (People)

| Nominativ | Genitiv | Dativ | Akuzativ | Vokativ | Lokál | Instrumentál | Notes |
|-----------|---------|-------|----------|---------|-------|--------------|-------|
| [Name] | [Gen] | [Dat] | [Acc] | [Voc] | [Loc] | [Ins] | [role/faction] |

## Místa (Places)

| Nominativ | Přídavné jméno | Genitiv | Lokál | Notes |
|-----------|---------------|---------|-------|-------|
| Hůrecko | hůrecký | Hůrecka | v Hůrecku | [main region] |
| Větrné hory | větrnohorský | Větrných hor | ve Větrných horách | [mountain range] |

## Bytosti (Creatures)

| Nominativ sg. | Nominativ pl. | Přídavné jméno | Notes |
|--------------|---------------|---------------|-------|
| troll | trollové | trollí | [double-l preserved] |

## Předměty a pojmy (Items & Concepts)

| Czech term | Meaning | Context |
|-----------|---------|---------|
| [term] | [what it means] | [where it appears] |
```
