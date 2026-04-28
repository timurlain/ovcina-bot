"""Rulemaster — Claude API integration for rule queries with tool_use."""

from __future__ import annotations

import datetime
import json
import re
from collections import defaultdict
from pathlib import Path

import anthropic

from .hra_search import search as hra_search, get_detail as hra_get_detail
from .logistics import (
    RegistraceClient,
    HraScheduleClient,
    BacaTasksClient,
    format_game_info,
    format_user_game_info,
    format_lodging,
    format_tasks,
    format_schedule,
    format_game_event,
    format_next_events,
)
from .tools import (
    RULEMASTER_TOOLS,
    RULEMASTER_WRITE_TOOLS,
    run_agent_loop,
    handle_search_files,
    format_hra_results,
    format_detail,
    log_changelog,
)


# Theme file mapping for query routing
_THEME_MAP = {
    "souboj": "souboj.md", "boj": "souboj.md", "útok": "souboj.md", "obrana": "souboj.md", "pvp": "souboj.md",
    "magie": "magie.md", "mana": "magie.md", "kouzl": "magie.md", "svitek": "magie.md",
    "peníze": "ekonomika.md", "obchod": "ekonomika.md", "produkce": "ekonomika.md", "trh": "ekonomika.md", "mince": "ekonomika.md",
    "povolání": "povolani.md", "třída": "povolani.md", "válečník": "povolani.md", "lovec": "povolani.md", "zloděj": "povolani.md", "mág": "povolani.md",
    "quest": "questy.md", "úkol": "questy.md", "odměna": "questy.md",
    "příšer": "prisery.md", "monster": "prisery.md", "loot": "prisery.md",
    "artefakt": "artefakty-a-lektvary.md", "runa": "artefakty-a-lektvary.md", "lektvar": "artefakty-a-lektvary.md", "alchymi": "artefakty-a-lektvary.md",
    "město": "mesta-a-kralovstvi.md", "král": "mesta-a-kralovstvi.md", "vesnice": "mesta-a-kralovstvi.md", "rozvoj": "mesta-a-kralovstvi.md",
}


def _load_prompt_template(skills_path: Path) -> str:
    """Load the rulemaster bot prompt from .skills/ directory."""
    prompt_file = skills_path / "ovcina-rulemaster" / "BOT_PROMPT.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Rulemaster prompt not found at {prompt_file}")


class Rulemaster:
    """Claude API-backed rules referee with tool_use."""

    def __init__(self, api_key: str, model: str, pravidla_path: Path,
                 skills_path: Path = None,
                 hra_api_url: str = None, hra_api_token: str = None, hra_game_id: int = None,
                 registrace_client: RegistraceClient = None,
                 hra_schedule_client: HraScheduleClient = None,
                 baca_client: BacaTasksClient = None,
                 max_history: int = 20):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.pravidla_path = pravidla_path
        self.hra_api_url = hra_api_url
        self.hra_api_token = hra_api_token
        self.hra_game_id = hra_game_id
        self.registrace = registrace_client
        self.hra_schedule = hra_schedule_client
        self.baca = baca_client
        self.max_history = max_history
        self._conversations: dict[int, list[dict]] = defaultdict(list)
        self._prompt_template = _load_prompt_template(skills_path) if skills_path else None
        self._ovcina_path = skills_path.parent if skills_path else None
        self._index = self._load_index()
        self._rule_editors: set[str] = set()
        self._handouts_cache: dict | None = None
        # Tokens consumed during the most recent query() call (sum across the
        # tool-use loop). Read by the consult-API blueprint.
        self.last_tokens_used: int = 0

    def set_rule_editors(self, editors: list[str]):
        """Set the list of emails allowed to edit rules."""
        self._rule_editors = {e.lower() for e in editors}

    # ----------------------------------------------------------------
    # File loaders (used by tool handlers)
    # ----------------------------------------------------------------

    def _load_index(self) -> str:
        """Load the rules index file."""
        index_path = self.pravidla_path / "_index.md"
        if index_path.exists():
            return index_path.read_text(encoding="utf-8")
        return "(Rejstřík pravidel není dostupný)"

    def _load_rule_file(self, relative_path: str) -> str:
        """Load a specific rule file by relative path."""
        full_path = self.pravidla_path / relative_path
        if full_path.exists():
            return full_path.read_text(encoding="utf-8")
        return ""

    def _load_handouts(self) -> dict:
        """Load the handouts manifest (pravidla/_handouts.json), cached after first read."""
        if self._handouts_cache is not None:
            return self._handouts_cache
        path = self.pravidla_path / "_handouts.json"
        if not path.exists():
            self._handouts_cache = {}
            return self._handouts_cache
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._handouts_cache = data.get("handouts", {}) if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            self._handouts_cache = {}
        return self._handouts_cache

    def _lookup_handout(self, name: str) -> str:
        """Resolve a handout name to a 'title — URL' string (or a 'not found' message)."""
        key = (name or "").strip().lower()
        handouts = self._load_handouts()
        entry = handouts.get(key)
        if not entry:
            available = ", ".join(sorted(handouts.keys())) or "(žádné)"
            return f"Handout '{name}' nenalezen. Dostupné: {available}."
        url = entry.get("url", "")
        title = entry.get("title", key)
        desc = entry.get("description", "")
        if desc:
            return f"{title} — {desc}\n\n{url}"
        return f"{title}\n\n{url}"

    def _find_theme(self, query: str) -> str:
        """Find and load the best matching theme file from _témata/."""
        query_lower = query.lower()
        themes_dir = self.pravidla_path / "_témata"
        if not themes_dir.exists():
            return ""

        matched_files = set()
        for keyword, filename in _THEME_MAP.items():
            if keyword in query_lower:
                matched_files.add(filename)

        results = []
        for filename in matched_files:
            path = themes_dir / filename
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")
                    results.append(f"--- Téma: {filename} ---\n{content}")
                except (OSError, UnicodeDecodeError):
                    pass
        return "\n\n".join(results)

    def _find_relevant_rules(self, query: str, user_role: str) -> str:
        """Find and load rule files relevant to a query based on keywords."""
        index = self._index
        relevant_files = []

        for line in index.split("\n"):
            if "|" not in line or line.startswith("|--") or line.startswith("| ID"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 6:
                continue

            rule_id, name, level, status, visibility, file_path = parts[:6]

            if user_role == "hráč" and visibility == "organizátor":
                continue

            query_lower = query.lower()
            if any(term in name.lower() or term in rule_id.lower()
                   for term in re.findall(r'\w+', query_lower) if len(term) > 2):
                content = self._load_rule_file(file_path)
                if content:
                    relevant_files.append(f"--- {rule_id}: {name} ---\n{content}")

        return "\n\n".join(relevant_files[:10])

    # ----------------------------------------------------------------
    # Tool handlers (closures bound to this instance)
    # ----------------------------------------------------------------

    def _make_tool_handlers(self, user_role: str, user_email: str = None) -> dict:
        """Create tool handler dict with closures over instance state."""

        async def search_rules(inp: dict) -> str:
            query = inp["query"]
            parts = []
            theme = self._find_theme(query)
            if theme:
                parts.append(f"TÉMATICKÝ SOUHRN:\n{theme}")
            rules = self._find_relevant_rules(query, user_role)
            if rules:
                parts.append(f"KONKRÉTNÍ PRAVIDLA:\n{rules}")
            if not parts:
                parts.append(f"INDEX PRAVIDEL (hledej zde ID souborů k načtení):\n{self._index}")
            return "\n\n".join(parts)

        async def get_rule_file(inp: dict) -> str:
            rule_id = inp["rule_id"].upper().replace(" ", "-")
            matches = list(self.pravidla_path.rglob(f"*{rule_id}*"))
            md_matches = [m for m in matches if m.suffix == ".md" and m.is_file()]
            if not md_matches:
                return f"Pravidlo '{rule_id}' nenalezeno."
            content = md_matches[0].read_text(encoding="utf-8")
            rel = md_matches[0].relative_to(self.pravidla_path)
            return f"--- {rel} ---\n{content}"[:8000]

        async def search_hra_api(inp: dict) -> str:
            if not self.hra_api_url:
                return "API není nakonfigurováno."
            # Search with gameId first
            results = await hra_search(
                self.hra_api_url, self.hra_api_token, inp["query"], self.hra_game_id,
            )
            if results:
                return format_hra_results(results)
            # Fallback: search without gameId
            results = await hra_search(
                self.hra_api_url, self.hra_api_token, inp["query"], None,
            )
            if results:
                return "⚠️ Výsledky NEJSOU v aktuální hře, ale existují v globální databázi:\n\n" + format_hra_results(results)
            return "Nic nenalezeno v databázi."

        async def get_item_detail(inp: dict) -> str:
            if not self.hra_api_url:
                return "API není nakonfigurováno."
            detail = await hra_get_detail(
                self.hra_api_url, self.hra_api_token, "Item", inp["item_id"],
            )
            return format_detail(detail, "Předmět", inp["item_id"])

        async def search_files(inp: dict) -> str:
            if not self._ovcina_path:
                return "Cesta k souborům není nakonfigurována."
            return await handle_search_files(
                self._ovcina_path, inp["query"], inp["directory"],
            )

        async def get_handout_link(inp: dict) -> str:
            return self._lookup_handout(inp.get("name", ""))

        # Logistics handlers — auto-fill email from auth context
        async def get_event_info(inp: dict) -> str:
            if not self.registrace:
                return "Registrace API není nakonfigurováno."
            info = await self.registrace.get_game_info()
            return format_game_info(info)

        async def get_my_registration(inp: dict) -> str:
            if not self.registrace:
                return "Registrace API není nakonfigurováno."
            if not user_email:
                return "Neznám tvůj email — nemohu ověřit registraci."
            info = await self.registrace.get_user_game_info(user_email)
            return format_user_game_info(info)

        async def get_my_lodging(inp: dict) -> str:
            if not self.registrace:
                return "Registrace API není nakonfigurováno."
            if not user_email:
                return "Neznám tvůj email."
            lodging = await self.registrace.get_user_lodging(user_email)
            return format_lodging(lodging)

        async def get_my_tasks(inp: dict) -> str:
            if not self.baca:
                return "Bača API není nakonfigurováno."
            if not user_email:
                return "Neznám tvůj email."
            if inp.get("overdue_only"):
                tasks = await self.baca.get_overdue_tasks(user_email)
                return format_tasks(tasks, label="PO TERMÍNU")
            status = inp.get("status", "Open")
            tasks = await self.baca.get_user_tasks(user_email, status=status)
            return format_tasks(tasks, label=f"ÚKOLY ({status})")

        async def get_my_schedule(inp: dict) -> str:
            if not self.registrace or not self.hra_schedule:
                return "API není nakonfigurováno."
            if not user_email:
                return "Neznám tvůj email."
            person_id = await self.registrace.get_person_id(user_email)
            if person_id is None:
                return "Tvůj účet není propojen s osobou v registraci — rozpis nedostupný."
            schedule = await self.hra_schedule.get_user_schedule(person_id)
            return format_schedule(schedule)

        async def get_current_event(inp: dict) -> str:
            if not self.hra_schedule:
                return "Hra API není nakonfigurováno."
            event = await self.hra_schedule.get_current_event()
            return format_game_event(event, label="TEĎ PROBÍHÁ")

        async def get_next_events(inp: dict) -> str:
            if not self.hra_schedule:
                return "Hra API není nakonfigurováno."
            count = inp.get("count", 3)
            events = await self.hra_schedule.get_next_events(count=count)
            return format_next_events(events)

        handlers = {
            "search_rules": search_rules,
            "get_rule_file": get_rule_file,
            "search_hra_api": search_hra_api,
            "get_item_detail": get_item_detail,
            "search_files": search_files,
            "get_handout_link": get_handout_link,
            "get_event_info": get_event_info,
            "get_my_registration": get_my_registration,
            "get_my_lodging": get_my_lodging,
            "get_my_tasks": get_my_tasks,
            "get_my_schedule": get_my_schedule,
            "get_current_event": get_current_event,
            "get_next_events": get_next_events,
        }

        # Write tools — only for rule editors
        if user_email and user_email.lower() in self._rule_editors:
            async def write_rule_file(inp: dict) -> str:
                rule_id = inp["rule_id"].upper().replace(" ", "-")
                matches = list(self.pravidla_path.rglob(f"*{rule_id}*"))
                md_matches = [m for m in matches if m.suffix == ".md" and m.is_file()]
                if not md_matches:
                    return f"Pravidlo '{rule_id}' nenalezeno — nelze zapsat."
                target = md_matches[0]
                target.write_text(inp["content"], encoding="utf-8")
                log_changelog(self.pravidla_path, user_email, rule_id, inp["change_summary"])
                rel = target.relative_to(self.pravidla_path)
                return f"✅ Soubor {rel} uložen. Změna zaznamenána v changelog."

            async def create_decision(inp: dict) -> str:
                import datetime
                roz_dir = self.pravidla_path / "rozhodnuti"
                roz_dir.mkdir(exist_ok=True)
                existing = list(roz_dir.glob("ROZ-*.md"))
                max_num = 0
                for f in existing:
                    match = re.search(r"ROZ-(\d+)", f.name)
                    if match:
                        max_num = max(max_num, int(match.group(1)))
                new_id = f"ROZ-{max_num + 1:03d}"
                slug = re.sub(r'[^\w\s-]', '', inp["title"][:50]).strip().replace(' ', '-').lower()
                filename = f"{new_id}-{slug}.md"
                today = datetime.date.today().isoformat()
                content = f"""---
id: {new_id}
název: "{inp['title']}"
úroveň: rozhodnutí
kategorie: [rozhodnutí]
stav: schváleno
viditelnost: hráč
závisí-na: []
nahrazuje: []
poslední-změna: {today}
---

# {inp['title']}

**Rozhodl/a:** {user_email}
**Datum:** {today}

{inp['content']}
"""
                (roz_dir / filename).write_text(content, encoding="utf-8")
                log_changelog(self.pravidla_path, user_email, new_id, inp["title"])
                return f"✅ Rozhodnutí {new_id} vytvořeno jako {filename}."

            handlers["write_rule_file"] = write_rule_file
            handlers["create_decision"] = create_decision

        return handlers

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def get_history(self, user_id: int) -> list[dict]:
        return self._conversations[user_id]

    def clear_history(self, user_id: int):
        self._conversations[user_id] = []

    async def query(self, user_id: int, message: str, user_role: str = "hráč",
                    user_email: str = None, on_progress=None) -> str:
        """Send a query using tool_use agent loop."""
        system = self._prompt_template.format(user_role=user_role)

        # Hotfixes — Osud-written overrides; highest priority, prepended to system prompt.
        from core.hotfixes import format_hotfixes_for_prompt
        hotfix_block = format_hotfixes_for_prompt()
        if hotfix_block:
            system = hotfix_block + "\n\n---\n\n" + system

        history = self._conversations[user_id]
        history.append({"role": "user", "content": message})
        if len(history) > self.max_history:
            history[:] = history[-self.max_history:]

        handlers = self._make_tool_handlers(user_role, user_email)

        # Add write tools for rule editors
        is_editor = user_email and user_email.lower() in self._rule_editors
        tools = RULEMASTER_TOOLS + RULEMASTER_WRITE_TOOLS if is_editor else RULEMASTER_TOOLS

        response_text, tokens_used = await run_agent_loop(
            client=self.client,
            model=self.model,
            system=system,
            history=history,
            tools=tools,
            tool_handlers=handlers,
            on_progress=on_progress,
        )
        self.last_tokens_used = tokens_used

        history.append({"role": "assistant", "content": response_text})
        return response_text

    async def add_proposal(self, user_id: int, proposal_text: str, user_email: str) -> str:
        """Create a new rule proposal file in _navrhy/."""
        navrhy_dir = self.pravidla_path / "_navrhy"
        existing = list(navrhy_dir.glob("NAV-*.md"))
        max_num = 0
        for f in existing:
            match = re.search(r"NAV-(\d+)", f.name)
            if match:
                max_num = max(max_num, int(match.group(1)))

        new_id = f"NAV-{max_num + 1:03d}"
        slug = re.sub(r'[^\w\s-]', '', proposal_text[:50]).strip().replace(' ', '-').lower()
        filename = f"{new_id}-{slug}.md"
        today = datetime.date.today().isoformat()

        content = f"""---
id: {new_id}
název: "Návrh: {proposal_text[:80]}"
úroveň: systémová
kategorie: [návrh]
stav: návrh
viditelnost: organizátor
závisí-na: []
nahrazuje: []
poslední-změna: {today}
---

# Návrh: {proposal_text[:80]}

**Navrhl/a:** {user_email}
**Datum:** {today}

## Popis návrhu

{proposal_text}

## Stav

Čeká na posouzení organizátory.
"""

        filepath = navrhy_dir / filename
        filepath.write_text(content, encoding="utf-8")

        return f"Návrh uložen jako {new_id}. Organizátoři ho posoudí."
