"""Router — classifies messages as rules or lore queries."""

from __future__ import annotations

import re
import anthropic


RULES_KEYWORDS = {
    "pravidlo", "pravidla", "souboj", "souboje", "soubojový",
    "útok", "útoku", "obrana", "obrany",
    "mana", "many", "kouzlo", "kouzla", "kouzel",
    "zloděj", "zlodej", "zloděje",
    "válečník", "valecnik", "válečníka",
    "lovec", "lovce", "lučištník", "lucistnik",
    "mág", "mag", "mága",
    "pvp", "šerpa", "serpa", "šerpy",
    "quest", "questy", "questů", "questu",
    "ekonomika", "mince", "mincí", "zlato",
    "lektvar", "lektvary", "lektvarů",
    "obchodník", "obchodnik",
    "artefakt", "artefakty",
    "svitky", "svitek", "svitků",
    "koncentrace", "zdraví", "zdravi", "životy",
    "zkušenost", "zkusenost", "zkušenosti", "xp",
    "úroveň", "uroven", "level",
    "třída", "trida", "povolání", "povolani",
    "dovednost", "dovednosti",
    "navrh", "návrh",
}

LORE_KEYWORDS = {
    "příběh", "pribeh", "příběhy",
    "historie", "historii", "dějiny",
    "kronika", "kroniky", "letopisy",
    "frakce", "frakci", "klan", "rod", "národ", "narod",
    "nekromancer", "nekromancera", "sauron", "gandalf",
    "temný", "temny", "temná", "temnota",
    "hvozd", "hvozdu", "mirkwood",
    "erebor", "ereboru", "dale", "gondor", "rohan",
    "elfové", "elfove", "elfů", "elf",
    "trpaslíci", "trpaslici", "trpaslík", "trpaslik",
    "orkové", "orkove", "orků", "ork",
    "lidé", "lide", "člověk", "clovek",
    "lokace", "lokaci", "místo", "misto",
    "město", "mesto", "města", "les", "hora", "řeka", "reka",
    "postava", "postavy", "postav", "npc",
    "královna", "kralovna", "král", "kral",
    "dol guldur", "strayhold", "rhovanion",
    "lore", "svět", "svet", "světa",
    "mapa", "mapy", "území", "uzemi",
    "kde", "odkud",
}


def _normalize(text: str) -> set[str]:
    """Lowercase and split into words."""
    return set(re.findall(r'\w+', text.lower()))


def _score(words: set[str], keywords: set[str]) -> int:
    """Count keyword matches."""
    return len(words & keywords)


def route_by_keywords(message: str) -> str | None:
    """Route by keyword matching.

    Returns 'rulemaster', 'loremaster', or None if ambiguous.
    """
    words = _normalize(message)
    rules = _score(words, RULES_KEYWORDS)
    lore = _score(words, LORE_KEYWORDS)

    if rules > 0 and lore == 0:
        return "rulemaster"
    if lore > 0 and rules == 0:
        return "loremaster"
    if rules == 0 and lore == 0:
        return "loremaster"  # default for general questions
    return None  # ambiguous — needs Claude


async def route_by_claude(client: anthropic.Anthropic, model: str, message: str) -> str:
    """Use Claude to classify an ambiguous message.

    Returns 'rulemaster' or 'loremaster'.
    """
    response = client.messages.create(
        model=model,
        max_tokens=10,
        system=(
            "Classify the user's Czech message as either RULES (game mechanics, combat, "
            "classes, spells, economy, quests) or LORE (world history, locations, characters, "
            "factions, stories). Reply with exactly one word: RULES or LORE."
        ),
        messages=[{"role": "user", "content": message}],
    )
    text = response.content[0].text.strip().upper()
    return "rulemaster" if "RULES" in text else "loremaster"


async def route(client: anthropic.Anthropic, model: str, message: str) -> str:
    """Route a message to the appropriate engine.

    Keyword-first, Claude fallback for ambiguous.
    """
    result = route_by_keywords(message)
    if result:
        return result
    return await route_by_claude(client, model, message)
