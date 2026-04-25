"""Anthropic tool_use definitions and agent loop for bot engines."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 8


# ============================================================
# Tool Definitions (Anthropic API format)
# ============================================================

TOOL_SEARCH_RULES = {
    "name": "search_rules",
    "description": (
        "Vyhledej v pravidlech Ovčiny. Prohledá tématické souhrnné soubory "
        "a index jednotlivých pravidel podle klíčových slov."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Hledané výrazy (např. 'válečník zbraně', 'kouzla úrovně 2')",
            }
        },
        "required": ["query"],
    },
}

TOOL_GET_RULE_FILE = {
    "name": "get_rule_file",
    "description": (
        "Přečti kompletní soubor pravidel podle ID. Použij poté, co search_rules "
        "ukáže, ve kterém souboru je odpověď. Příklady: ZAK-003, MAG-006, EKO-001."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "ID pravidla (např. 'ZAK-003', 'MAG-006')",
            }
        },
        "required": ["rule_id"],
    },
}

TOOL_SEARCH_HRA_API = {
    "name": "search_hra_api",
    "description": (
        "Vyhledej v online databázi hra.ovcina.cz — předměty, příšery, lokace a questy. "
        "Vrací název, typ a krátký popis nalezených záznamů s jejich ID."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Hledaný výraz v češtině (např. 'luk', 'troll', 'lektvar')",
            }
        },
        "required": ["query"],
    },
}

TOOL_GET_ITEM_DETAIL = {
    "name": "get_item_detail",
    "description": (
        "Získej kompletní detail předmětu z databáze hra.ovcina.cz včetně "
        "požadavků na povolání, úrovně a efektů."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "integer",
                "description": "ID předmětu (získáš z výsledků search_hra_api)",
            }
        },
        "required": ["item_id"],
    },
}

TOOL_GET_LOCATION_DETAIL = {
    "name": "get_location_detail",
    "description": (
        "Získej kompletní detail lokace z databáze hra.ovcina.cz "
        "včetně popisu, podrobností a herního potenciálu."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "location_id": {
                "type": "integer",
                "description": "ID lokace z databáze",
            }
        },
        "required": ["location_id"],
    },
}

TOOL_SEARCH_LORE = {
    "name": "search_lore",
    "description": (
        "Vyhledej v lore souborech Ovčiny (brain/, games/, knowledge-base/). "
        "Vrací relevantní úryvky s názvy zdrojových souborů."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Hledané výrazy (např. 'Kamenár historie', 'trollí jeskyně')",
            }
        },
        "required": ["query"],
    },
}

TOOL_SEARCH_FILES = {
    "name": "search_files",
    "description": (
        "Fulltextové vyhledávání ve všech Markdown souborech Ovčiny. "
        "Použij jako zálohu, když jiné nástroje nenajdou odpověď."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text k vyhledání",
            },
            "directory": {
                "type": "string",
                "enum": ["pravidla", "brain", "knowledge-base", "games"],
                "description": "Ve kterém adresáři hledat",
            },
        },
        "required": ["query", "directory"],
    },
}


# Write tools (only for rule editors)
TOOL_WRITE_RULE_FILE = {
    "name": "write_rule_file",
    "description": (
        "Zapiš aktualizovaný obsah pravidlového souboru. Nejdřív VŽDY přečti "
        "aktuální obsah přes get_rule_file, uprav ho, a zapiš celý nový obsah zpět."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "ID pravidla (např. 'MAG-006', 'ZAK-003')",
            },
            "content": {
                "type": "string",
                "description": "Nový kompletní obsah souboru (včetně YAML frontmatter)",
            },
            "change_summary": {
                "type": "string",
                "description": "Stručný popis změny pro changelog (česky)",
            },
        },
        "required": ["rule_id", "content", "change_summary"],
    },
}

TOOL_CREATE_DECISION = {
    "name": "create_decision",
    "description": (
        "Vytvoř nové rozhodnutí (ROZ-xxx) — jednorázové pravidlové rozhodnutí "
        "ze schůzky nebo hry. Automaticky přidělí další číslo."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Název rozhodnutí (česky)",
            },
            "content": {
                "type": "string",
                "description": "Obsah rozhodnutí — co bylo rozhodnuto a proč",
            },
        },
        "required": ["title", "content"],
    },
}


# Pre-built tool sets for each engine (logistics appended below)
RULEMASTER_TOOLS_BASE = [
    TOOL_SEARCH_RULES,
    TOOL_GET_RULE_FILE,
    TOOL_SEARCH_HRA_API,
    TOOL_GET_ITEM_DETAIL,
    TOOL_SEARCH_FILES,
]

RULEMASTER_WRITE_TOOLS = [
    TOOL_WRITE_RULE_FILE,
    TOOL_CREATE_DECISION,
]

# ============================================================
# Logistics tools (shared by both engines)
# ============================================================

TOOL_GET_EVENT_INFO = {
    "name": "get_event_info",
    "description": (
        "Získej informace o aktuální hře — název, data, místo, počet registrovaných, "
        "uzávěrka registrace a organizační informace. Použij pro otázky 'kdy je hra?', "
        "'kde se sejdeme?', 'co si mám přinést?'."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_GET_MY_REGISTRATION = {
    "name": "get_my_registration",
    "description": (
        "Získej osobní informace uživatele o hře — registrační status, kdo jede s ním "
        "(rodina), ubytování, platba, herní role. Používá email z autentizace. "
        "Odpovídá na 'jsem zaregistrovaný?', 'kdo se mnou jede?', 'kde spím?', 'zaplatil jsem?'."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_GET_MY_LODGING = {
    "name": "get_my_lodging",
    "description": (
        "Získej jen detail ubytování uživatele — pokoj, kapacita, spolubydlící. "
        "Lehčí verze get_my_registration pro specifické dotazy."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_GET_MY_TASKS = {
    "name": "get_my_tasks",
    "description": (
        "Získej úkoly uživatele z Bači. Defaultně vrací otevřené úkoly. "
        "Odpovídá na 'co mám dnes dělat?', 'jaké mám úkoly?'. "
        "Každý úkol má deep link na baca.ovcina.cz."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["Open", "InProgress", "ForReview", "Done", "Idea", "All"],
                "description": "Status filtr (default: Open)",
            },
            "overdue_only": {
                "type": "boolean",
                "description": "Vrátit jen úkoly po termínu",
            },
        },
        "required": [],
    },
}

TOOL_GET_MY_SCHEDULE = {
    "name": "get_my_schedule",
    "description": (
        "Získej NPC rozpis uživatele na hru — jaké postavy hraje, kdy a kde. "
        "Primárně pro organizátory hrající NPC postavy. "
        "Odpovídá na 'co dneska hraju?', 'jakou NPC mám dneska?', 'kdy a kde mám být?'."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_GET_CURRENT_EVENT = {
    "name": "get_current_event",
    "description": (
        "Získej informace o aktuálně probíhající herní události (GameEvent). "
        "Odpovídá na 'co se děje teď?', 'co právě probíhá?'."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_GET_NEXT_EVENTS = {
    "name": "get_next_events",
    "description": (
        "Získej seznam nadcházejících herních událostí. Defaultně dalších 3. "
        "Odpovídá na 'co bude dál?', 'co bude večer?'."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "description": "Počet událostí (default: 3)",
            },
        },
        "required": [],
    },
}

LOGISTICS_TOOLS = [
    TOOL_GET_EVENT_INFO,
    TOOL_GET_MY_REGISTRATION,
    TOOL_GET_MY_LODGING,
    TOOL_GET_MY_TASKS,
    TOOL_GET_MY_SCHEDULE,
    TOOL_GET_CURRENT_EVENT,
    TOOL_GET_NEXT_EVENTS,
]

LOREMASTER_TOOLS_BASE = [
    TOOL_SEARCH_LORE,
    TOOL_SEARCH_HRA_API,
    TOOL_GET_ITEM_DETAIL,
    TOOL_GET_LOCATION_DETAIL,
    TOOL_SEARCH_FILES,
]

# Final tool sets = base + logistics
RULEMASTER_TOOLS = RULEMASTER_TOOLS_BASE + LOGISTICS_TOOLS
LOREMASTER_TOOLS = LOREMASTER_TOOLS_BASE + LOGISTICS_TOOLS


# ============================================================
# Shared Tool Handlers
# ============================================================

async def handle_search_files(base_path: Path, query: str, directory: str) -> str:
    """Full-text search across Ovčina markdown files. Read-only, sandboxed."""
    search_dir = base_path / directory
    if not search_dir.exists():
        return f"Adresář '{directory}' neexistuje."

    # Security: stay within base_path
    try:
        search_dir.resolve().relative_to(base_path.resolve())
    except ValueError:
        return "Přístup odmítnut."

    terms = {t for t in re.findall(r'\w+', query.lower()) if len(t) > 2}
    if not terms:
        return "Příliš krátké hledané výrazy."

    results = []
    for md_file in search_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        content_lower = content.lower()
        matched = sum(1 for t in terms if t in content_lower)
        if matched:
            rel = md_file.relative_to(base_path)
            results.append((matched, f"--- {rel} ---\n{content[:2000]}"))

    results.sort(key=lambda x: -x[0])
    top = [r[1] for r in results[:8]]
    return "\n\n".join(top) if top else "Nic nenalezeno."


def log_changelog(pravidla_path: Path, editor_email: str, rule_id: str, summary: str):
    """Append an entry to _changelog.md."""
    import datetime
    changelog = pravidla_path / "_changelog.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- **{timestamp}** — {editor_email} — **{rule_id}**: {summary}\n"
    if changelog.exists():
        content = changelog.read_text(encoding="utf-8")
    else:
        content = "# Changelog pravidel\n\n"
    content += entry
    changelog.write_text(content, encoding="utf-8")


def format_hra_results(results: list[dict]) -> str:
    """Format hra.ovcina.cz search results into a readable string."""
    if not results:
        return "Nic nenalezeno v databázi."
    lines = []
    items_found = []
    for r in results[:10]:
        desc = r.get("description", "") or ""
        lines.append(f"{r['entityType']} #{r['id']}: {r['name']} — {desc[:200]}")
        if r["entityType"] == "Item":
            items_found.append(r["id"])
    text = "\n".join(lines)
    if items_found:
        ids = ", ".join(str(i) for i in items_found)
        text += (
            f"\n\n⚠️ Nalezeny předměty (ID: {ids}). "
            "Použij get_item_detail pro každý relevantní předmět — "
            "obsahuje požadavky na povolání a úroveň!"
        )
    return text


def format_detail(detail: dict | None, entity_type: str, entity_id: int) -> str:
    """Format a detail response into a readable string."""
    if not detail:
        return f"{entity_type} #{entity_id} nenalezen/a."
    return json.dumps(detail, ensure_ascii=False, indent=2)[:6000]


# ============================================================
# Agent Loop
# ============================================================

ToolHandler = Callable[[dict], Awaitable[str]]
StatusCallback = Callable[[str], Awaitable[None]]

# Human-friendly tool descriptions for progress messages
_TOOL_STATUS = {
    "search_rules": "📖 Prohledávám pravidla...",
    "get_rule_file": "📖 Čtu pravidlo {rule_id}...",
    "search_hra_api": "🗄️ Hledám v databázi: {query}...",
    "get_item_detail": "📋 Kontroluji detail předmětu #{item_id}...",
    "get_location_detail": "🗺️ Kontroluji detail lokace #{location_id}...",
    "search_lore": "📜 Prohledávám lore...",
    "search_files": "🔍 Hledám v souborech ({directory})...",
    "write_rule_file": "✍️ Zapisuji změnu pravidla {rule_id}...",
    "create_decision": "📝 Vytvářím rozhodnutí...",
    "get_event_info": "🎪 Načítám informace o hře...",
    "get_my_registration": "📋 Kontroluji tvou registraci...",
    "get_my_lodging": "🏕️ Hledám tvé ubytování...",
    "get_my_tasks": "✅ Hledám tvé úkoly v Bači...",
    "get_my_schedule": "🗓️ Načítám tvůj NPC rozpis...",
    "get_current_event": "⏰ Co se právě děje...",
    "get_next_events": "⏭️ Nadcházející události...",
}


def _tool_status_text(tool_name: str, tool_input: dict) -> str:
    """Generate a human-readable status message for a tool call."""
    template = _TOOL_STATUS.get(tool_name, f"🔧 {tool_name}...")
    try:
        return template.format(**tool_input)
    except (KeyError, IndexError):
        return template.split("{")[0] + "..."


async def run_agent_loop(
    client,
    model: str,
    system: str,
    history: list[dict],
    tools: list[dict],
    tool_handlers: dict[str, ToolHandler],
    max_rounds: int = MAX_TOOL_ROUNDS,
    on_progress: StatusCallback | None = None,
) -> str:
    """Run a tool-using agent loop. Returns the final text response.

    History should contain only text messages (user/assistant pairs from
    prior turns). Tool interactions within the current turn are ephemeral
    and not persisted in history.

    on_progress: optional async callback to report tool activity to the user.
    """
    messages = list(history)  # work on a copy

    for round_num in range(max_rounds):
        logger.info("Agent loop round %d/%d (%d messages)",
                     round_num + 1, max_rounds, len(messages))

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=messages,
            tools=tools,
        )

        # If Claude is done (no tool use), extract text
        if response.stop_reason == "end_turn":
            text_parts = [b.text for b in response.content if b.type == "text"]
            return "".join(text_parts)

        # Claude wants to use tools
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            logger.info("Tool call: %s(%s)", block.name,
                        json.dumps(block.input, ensure_ascii=False)[:200])

            # Report progress to user
            if on_progress:
                try:
                    await on_progress(_tool_status_text(block.name, block.input))
                except Exception:
                    pass  # don't let status updates break the loop

            handler = tool_handlers.get(block.name)
            if not handler:
                result = f"Neznámý nástroj: {block.name}"
            else:
                try:
                    result = await handler(block.input)
                except Exception as e:
                    logger.error("Tool %s failed: %s", block.name, e)
                    result = f"Chyba při volání {block.name}: {e}"

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result)[:8000],
            })

        messages.append({"role": "user", "content": tool_results})

    # Exhausted rounds — try one final call without tools to force a text answer
    logger.warning("Agent loop exhausted %d rounds, forcing final answer", max_rounds)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system + "\n\nNEMÁŠ DALŠÍ NÁSTROJE. Odpověz na základě informací, které jsi již získal.",
            messages=messages,
        )
        text_parts = [b.text for b in response.content if b.type == "text"]
        if text_parts:
            return "".join(text_parts)
    except Exception as e:
        logger.error("Final answer attempt failed: %s", e)
    return "Omlouvám se, nedokázal jsem najít odpověď. Zkus dotaz přeformulovat."
