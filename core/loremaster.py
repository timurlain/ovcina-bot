"""LoreMaster — Claude API integration for lore queries with tool_use."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import anthropic

from .access import parse_frontmatter, can_access, load_roles
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
    LOREMASTER_TOOLS,
    run_agent_loop,
    handle_search_files,
    format_hra_results,
    format_detail,
)


def _load_prompt(skills_path: Path, filename: str) -> str:
    """Load a loremaster bot prompt from .skills/ directory."""
    prompt_file = skills_path / "ovcina-loremaster" / filename
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    raise FileNotFoundError(f"LoreMaster prompt not found at {prompt_file}")


class LoreMaster:
    """Claude API-backed lore guide with role-based access and tool_use."""

    def __init__(
        self, api_key: str, model: str, brain_path: Path,
        kb_public_path: Path, game_path: Path = None,
        skills_path: Path = None,
        hra_api_url: str = None, hra_api_token: str = None, hra_game_id: int = None,
        registrace_client: RegistraceClient = None,
        hra_schedule_client: HraScheduleClient = None,
        baca_client: BacaTasksClient = None,
        max_history: int = 20,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.brain_path = brain_path
        self.kb_public_path = kb_public_path
        self.game_path = game_path
        self.hra_api_url = hra_api_url
        self.hra_api_token = hra_api_token
        self.hra_game_id = hra_game_id
        self.registrace = registrace_client
        self.hra_schedule = hra_schedule_client
        self.baca = baca_client
        self.max_history = max_history
        self._conversations: dict[str, list[dict]] = defaultdict(list)
        self._roles = load_roles(brain_path / "_roles.yaml")
        # Tokens consumed during the most recent query() call (sum across the
        # tool-use loop). Read by the consult-API blueprint.
        self.last_tokens_used: int = 0
        self._file_index = self._load_curated_index()
        self._prompt_player = _load_prompt(skills_path, "BOT_PROMPT_PLAYER.md") if skills_path else None
        self._prompt_gm = _load_prompt(skills_path, "BOT_PROMPT_GM.md") if skills_path else None
        self._ovcina_path = skills_path.parent if skills_path else None

    def _load_curated_index(self) -> str:
        """Load curated index from _loremaster-index.md."""
        index_path = self.brain_path / "_loremaster-index.md"
        if index_path.exists():
            try:
                return index_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                pass
        return "(Index nenalezen)"

    # Czech <-> English synonyms for common lore terms
    _SYNONYMS = {
        "lokac": "location", "lokál": "location", "míst": "location",
        "location": "lokac",
        "postav": "character", "character": "postav",
        "frakc": "faction", "faction": "frakc",
        "příšer": "creature", "creature": "příšer", "nestvůr": "creature",
        "příběh": "story", "story": "příběh",
        "histori": "history", "history": "histori", "dějin": "history",
        "mapa": "map", "map": "mapa",
        "dungeon": "dungeon", "jeskyň": "dungeon",
        "quest": "quest", "úkol": "quest",
        "zbran": "weapon", "weapon": "zbran",
        "kouzl": "spell", "spell": "kouzl", "magi": "magic",
        "game": "hra", "hra": "game", "her": "game",
    }

    def _expand_terms(self, terms: set[str]) -> set[str]:
        """Expand query terms with Czech/English synonyms."""
        expanded = set(terms)
        for term in terms:
            for prefix, synonym in self._SYNONYMS.items():
                if term.startswith(prefix) or prefix.startswith(term[:4]):
                    expanded.add(synonym)
        return expanded

    def _find_lore_files(self, query: str, user: dict) -> str:
        """Find and load lore files relevant to query, filtered by access."""
        results = []
        query_terms = self._expand_terms(set(re.findall(r'\w+', query.lower())))

        # Search brain/ files
        for md_file in self.brain_path.rglob("*.md"):
            if md_file.name.startswith("_"):
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            meta, body = parse_frontmatter(content)

            if meta.get("přístup") and not can_access(meta, user):
                continue

            file_text = (md_file.stem + " " + body[:500]).lower()
            if any(term in file_text for term in query_terms if len(term) > 2):
                source = str(md_file.relative_to(self.brain_path))
                results.append(f"--- {source} ---\n{body[:8000]}")

        # Search game/ files
        game_summaries = []
        game_details = []
        if self.game_path and self.game_path.exists():
            for md_file in self.game_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                rel = str(md_file.relative_to(self.game_path)).replace("\\", "/")
                file_text = (md_file.stem + " " + rel + " " + content[:500]).lower()
                if any(term in file_text for term in query_terms if len(term) > 2):
                    entry = f"--- game/{rel} ---\n{content[:8000]}"
                    if "/" in rel:
                        game_details.append(entry)
                    else:
                        game_summaries.append(entry)
            results.extend(game_summaries)
            results.extend(game_details[:5])

        # Search knowledge-base/public/ files
        if self.kb_public_path.exists():
            for md_file in self.kb_public_path.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                file_text = (md_file.stem + " " + content[:500]).lower()
                if any(term in file_text for term in query_terms if len(term) > 2):
                    results.append(f"--- kb/{md_file.name} ---\n{content[:8000]}")

        return "\n\n".join(results[:12])

    def _get_role_info(self, user: dict) -> tuple[str, str, str]:
        """Get postava, frakce, popis from user profile + roles yaml."""
        postava = user.get("postava") or "neznámý"
        frakce = user.get("frakce") or "neznámá"
        popis = ""
        if postava in self._roles:
            role_data = self._roles[postava]
            if not user.get("frakce"):
                frakce = role_data.get("frakce", frakce)
            popis = role_data.get("popis", "")
        return postava, frakce, popis

    # ----------------------------------------------------------------
    # Tool handlers
    # ----------------------------------------------------------------

    def _make_tool_handlers(self, user: dict) -> dict:
        """Create tool handler dict with closures over instance state."""
        user_email = user.get("email") if user else None

        async def search_lore(inp: dict) -> str:
            query = inp["query"]
            local = self._find_lore_files(query, user)
            if local:
                return local
            return f"Nic nenalezeno v lokálních souborech.\n\nINDEX ZDROJŮ:\n{self._file_index}"

        async def search_hra_api(inp: dict) -> str:
            if not self.hra_api_url:
                return "API není nakonfigurováno."
            results = await hra_search(
                self.hra_api_url, self.hra_api_token, inp["query"], self.hra_game_id,
            )
            if results:
                return format_hra_results(results)
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

        async def get_location_detail(inp: dict) -> str:
            if not self.hra_api_url:
                return "API není nakonfigurováno."
            detail = await hra_get_detail(
                self.hra_api_url, self.hra_api_token, "Location", inp["location_id"],
            )
            return format_detail(detail, "Lokace", inp["location_id"])

        async def search_files(inp: dict) -> str:
            if not self._ovcina_path:
                return "Cesta k souborům není nakonfigurována."
            return await handle_search_files(
                self._ovcina_path, inp["query"], inp["directory"],
            )

        # Logistics handlers
        async def get_event_info(inp: dict) -> str:
            if not self.registrace:
                return "Registrace API není nakonfigurováno."
            info = await self.registrace.get_game_info()
            return format_game_info(info)

        async def get_my_registration(inp: dict) -> str:
            if not self.registrace or not user_email:
                return "Nemohu získat tvé údaje."
            info = await self.registrace.get_user_game_info(user_email)
            return format_user_game_info(info)

        async def get_my_lodging(inp: dict) -> str:
            if not self.registrace or not user_email:
                return "Nemohu získat tvé ubytování."
            lodging = await self.registrace.get_user_lodging(user_email)
            return format_lodging(lodging)

        async def get_my_tasks(inp: dict) -> str:
            if not self.baca or not user_email:
                return "Nemohu získat tvé úkoly."
            if inp.get("overdue_only"):
                tasks = await self.baca.get_overdue_tasks(user_email)
                return format_tasks(tasks, label="PO TERMÍNU")
            status = inp.get("status", "Open")
            tasks = await self.baca.get_user_tasks(user_email, status=status)
            return format_tasks(tasks, label=f"ÚKOLY ({status})")

        async def get_my_schedule(inp: dict) -> str:
            if not self.registrace or not self.hra_schedule or not user_email:
                return "Nemohu získat rozpis."
            person_id = await self.registrace.get_person_id(user_email)
            if person_id is None:
                return "Tvůj účet není propojen s osobou — rozpis nedostupný."
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

        return {
            "search_lore": search_lore,
            "search_hra_api": search_hra_api,
            "get_item_detail": get_item_detail,
            "get_location_detail": get_location_detail,
            "search_files": search_files,
            "get_event_info": get_event_info,
            "get_my_registration": get_my_registration,
            "get_my_lodging": get_my_lodging,
            "get_my_tasks": get_my_tasks,
            "get_my_schedule": get_my_schedule,
            "get_current_event": get_current_event,
            "get_next_events": get_next_events,
        }

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def get_history(self, user_key: str) -> list[dict]:
        return self._conversations[user_key]

    def clear_history(self, user_key: str):
        self._conversations[user_key] = []

    async def query(self, user_key: str, message: str, user: dict, send_status=None) -> str:
        """Send a lore query using tool_use agent loop."""
        is_gm = user.get("role") in ("organizátor", "gm")

        if is_gm:
            system = self._prompt_gm
        else:
            postava, frakce, popis = self._get_role_info(user)
            system = self._prompt_player.format(
                postava=postava,
                frakce=frakce,
                postava_popis=popis or f"{postava} z frakce {frakce}",
            )

        # Hotfixes — Osud-written overrides; highest priority, prepended to system prompt.
        from core.hotfixes import format_hotfixes_for_prompt
        hotfix_block = format_hotfixes_for_prompt()
        if hotfix_block:
            system = hotfix_block + "\n\n---\n\n" + system

        history = self._conversations[user_key]
        history.append({"role": "user", "content": message})
        if len(history) > self.max_history:
            history[:] = history[-self.max_history:]

        handlers = self._make_tool_handlers(user)

        response_text, tokens_used = await run_agent_loop(
            client=self.client,
            model=self.model,
            system=system,
            history=history,
            tools=LOREMASTER_TOOLS,
            tool_handlers=handlers,
            on_progress=send_status,
        )
        self.last_tokens_used = tokens_used

        history.append({"role": "assistant", "content": response_text})
        return response_text
