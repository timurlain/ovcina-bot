"""Logistics — organizational knowledge integration.

Provides client wrappers for:
- registrace.ovcina.cz (game info, user registration, lodging, person-id resolver)
- api.hra.ovcina.cz (user schedule, game events)
- baca.ovcina.cz (user tasks)

All clients use email as the primary identifier. The registrace person-id
endpoint resolves email -> personId for hra integration (hra uses int personId).

Times are UTC in all API responses; formatters convert to Europe/Prague for display.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import aiohttp

logger = logging.getLogger(__name__)

PRAGUE = ZoneInfo("Europe/Prague")
UTC = ZoneInfo("UTC")


def _parse_utc(iso: str) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp, treating naive as UTC."""
    if not iso:
        return None
    try:
        s = iso.rstrip("Z")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, TypeError):
        return None


def _format_prague(iso: str, fmt: str = "%d.%m.%Y %H:%M") -> str:
    """Format a UTC ISO timestamp as Prague local time."""
    dt = _parse_utc(iso)
    if not dt:
        return iso or ""
    return dt.astimezone(PRAGUE).strftime(fmt)


# ============================================================
# Registrace client
# ============================================================

class RegistraceClient:
    """Async client for registrace.ovcina.cz integration API (v1)."""

    def __init__(self, api_url: str, integration_api_key: str, game_id: int):
        self.base_url = api_url.rstrip("/") + "/api/v1"
        self.api_key = integration_api_key
        self.game_id = game_id
        self._person_id_cache: dict[str, Optional[int]] = {}

    @property
    def _headers(self) -> dict:
        return {"X-Api-Key": self.api_key}

    async def _get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        url = f"{self.base_url}{path}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=self._headers, params=params, ssl=False) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    if resp.status == 404:
                        return None
                    logger.error("registrace GET %s failed: %s", path, resp.status)
                    return None
        except Exception as e:
            logger.error("registrace GET %s error: %s", path, e)
            return None

    async def get_game_info(self, game_id: Optional[int] = None) -> Optional[dict]:
        """GET /api/v1/games/{id}/info"""
        gid = game_id or self.game_id
        return await self._get(f"/games/{gid}/info")

    async def get_user_game_info(self, email: str) -> Optional[dict]:
        """GET /api/v1/users/{email}/game-info?gameId=Y"""
        return await self._get(
            f"/users/{email}/game-info",
            params={"gameId": self.game_id},
        )

    async def get_user_lodging(self, email: str) -> Optional[dict]:
        """GET /api/v1/users/{email}/lodging?gameId=Y — may return null body"""
        return await self._get(
            f"/users/{email}/lodging",
            params={"gameId": self.game_id},
        )

    async def get_person_id(self, email: str) -> Optional[int]:
        """GET /api/v1/users/{email}/person-id — with in-memory cache."""
        if email in self._person_id_cache:
            return self._person_id_cache[email]
        result = await self._get(f"/users/{email}/person-id")
        person_id = result.get("personId") if result else None
        self._person_id_cache[email] = person_id
        return person_id


# ============================================================
# Hra schedule client
# ============================================================

class HraScheduleClient:
    """Async client for api.hra.ovcina.cz GameEvent + schedule endpoints."""

    def __init__(self, api_url: str, token: str, game_id: int):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.game_id = game_id

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    async def _get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        url = f"{self.api_url}{path}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=self._headers, params=params, ssl=False) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    if resp.status == 404:
                        return None
                    logger.error("hra GET %s failed: %s", path, resp.status)
                    return None
        except Exception as e:
            logger.error("hra GET %s error: %s", path, e)
            return None

    async def get_user_schedule(self, person_id: int) -> Optional[dict]:
        """GET /api/users/{personId}/schedule?gameId=X"""
        return await self._get(
            f"/api/users/{person_id}/schedule",
            params={"gameId": self.game_id},
        )

    async def get_current_event(self) -> Optional[dict]:
        """GET /api/games/{gameId}/events/current"""
        return await self._get(f"/api/games/{self.game_id}/events/current")

    async def get_next_events(self, count: int = 3) -> list[dict]:
        """GET /api/games/{gameId}/events/next?count=N"""
        result = await self._get(
            f"/api/games/{self.game_id}/events/next",
            params={"count": count},
        )
        return result if isinstance(result, list) else []


# ============================================================
# Bača tasks client
# ============================================================

class BacaTasksClient:
    """Async client for baca.ovcina.cz tasks API."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    @property
    def _headers(self) -> dict:
        return {"X-Api-Key": self.api_key}

    async def _get(self, path: str, params: Optional[dict] = None) -> list[dict]:
        url = f"{self.api_url}{path}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=self._headers, params=params, ssl=False) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data if isinstance(data, list) else []
                    logger.error("baca GET %s failed: %s", path, resp.status)
                    return []
        except Exception as e:
            logger.error("baca GET %s error: %s", path, e)
            return []

    async def get_user_tasks(self, email: str, status: Optional[str] = "Open") -> list[dict]:
        params = {"assigneeEmail": email}
        if status and status != "All":
            params["status"] = status
        return await self._get("/api/tasks", params=params)

    async def get_overdue_tasks(self, email: str) -> list[dict]:
        return await self._get(
            "/api/tasks",
            params={"assigneeEmail": email, "overdue": "true"},
        )


# ============================================================
# Formatters — DTO -> human-readable Czech strings
# ============================================================

_PAYMENT_STATUS_CZ = {
    "paid": "Zaplaceno",
    "partial": "Částečně zaplaceno",
    "unpaid": "Nezaplaceno",
}

_PRIORITY_ICON = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}


def format_game_info(info: Optional[dict]) -> str:
    """Format game metadata."""
    if not info:
        return "Informace o hře nenalezeny."

    parts = [f"HRA: {info.get('name', '?')}"]

    if info.get("description"):
        parts.append(f"POPIS: {info['description']}")

    if starts := info.get("startsAtUtc"):
        parts.append(f"ZAČÁTEK: {_format_prague(starts)}")
    if ends := info.get("endsAtUtc"):
        parts.append(f"KONEC: {_format_prague(ends)}")

    if reg_closes := info.get("registrationClosesAtUtc"):
        parts.append(f"UZÁVĚRKA REGISTRACE: {_format_prague(reg_closes)}")

    total = info.get("totalRegistered", 0)
    target = info.get("targetPlayerCountTotal", 0)
    if target:
        parts.append(f"REGISTROVÁNO: {total}/{target}")

    # organizationInfo is arbitrary JSON from organizer — pass through as JSON string
    if org := info.get("organizationInfo"):
        import json
        parts.append(f"ORGANIZAČNÍ INFO:\n{json.dumps(org, ensure_ascii=False, indent=2)}")

    return "\n".join(parts)


def format_user_game_info(info: Optional[dict]) -> str:
    """Format user's personal registration info (the big one)."""
    if not info:
        return "Informace nenalezeny."

    if not info.get("registered"):
        return "❌ Nejsi registrovaný/á na tuto hru."

    parts = ["✅ REGISTROVÁN/A"]

    if name := info.get("groupName"):
        parts.append(f"SKUPINA: {name}")

    # Payment
    status = info.get("paymentStatus", "")
    status_cz = _PAYMENT_STATUS_CZ.get(status, status or "neznámo")
    expected = info.get("expectedAmount")
    paid = info.get("paidAmount")
    if expected is not None:
        parts.append(f"PLATBA: {status_cz} ({paid or 0}/{expected} Kč)")
    else:
        parts.append(f"PLATBA: {status_cz}")

    # Attendees
    attendees = info.get("attendees", [])
    if attendees:
        lines = [f"ÚČASTNÍCI ({len(attendees)}):"]
        for a in attendees:
            full_name = f"{a.get('firstName', '')} {a.get('lastName', '')}".strip() or "?"
            att_type = a.get("attendeeType", "")
            char_name = a.get("characterName")
            extras = []
            if att_type:
                extras.append(att_type)
            if char_name:
                extras.append(f"jako {char_name}")
            extras_str = f" ({', '.join(extras)})" if extras else ""
            lines.append(f"- {full_name}{extras_str}")
        parts.append("\n".join(lines))

    # Lodging
    lodging = info.get("lodging")
    if lodging:
        parts.append("UBYTOVÁNÍ:\n" + _format_lodging_body(lodging))
    else:
        parts.append("UBYTOVÁNÍ: Zatím nepřiděleno.")

    # Game roles
    if roles := info.get("gameRoles"):
        parts.append(f"HERNÍ ROLE: {', '.join(roles)}")

    return "\n\n".join(parts)


def _format_lodging_body(lodging: dict) -> str:
    lines = []
    if room := lodging.get("roomName"):
        lines.append(f"- Pokoj: {room}")
    if ltype := lodging.get("lodgingType"):
        lines.append(f"- Typ: {ltype}")
    if cap := lodging.get("roomCapacity"):
        lines.append(f"- Kapacita: {cap}")
    if roommates := lodging.get("roommates"):
        lines.append(f"- Spolubydlící: {', '.join(roommates)}")
    return "\n".join(lines) if lines else "(bez detailů)"


def format_lodging(lodging: Optional[dict]) -> str:
    """Format lodging info (null-safe)."""
    if not lodging:
        return "Ubytování zatím nepřiděleno."
    return "UBYTOVÁNÍ:\n" + _format_lodging_body(lodging)


def format_tasks(tasks: list[dict], label: str = "ÚKOLY") -> str:
    """Format Bača task list."""
    if not tasks:
        return "Žádné úkoly nenalezeny."

    lines = [f"{label} ({len(tasks)}):"]
    for t in tasks:
        title = t.get("title", "?")
        priority = t.get("priority", "")
        icon = _PRIORITY_ICON.get(priority, "•")
        status = t.get("status", "")
        due_info = ""
        if due := t.get("dueDate"):
            due_info = f" — termín {_format_prague(due, '%d.%m.')}"
        category = t.get("categoryName")
        cat_info = f" [{category}]" if category else ""
        tid = t.get("id")
        url = f"https://baca.ovcina.cz/tasks/{tid}" if tid else ""
        lines.append(f"{icon} **{title}**{cat_info}{due_info} [{status}]\n   {url}")

    return "\n".join(lines)


def format_schedule(schedule: Optional[dict]) -> str:
    """Format user's NPC schedule from hra."""
    if not schedule:
        return "Žádný rozpis nenalezen."

    events = schedule.get("events", [])
    if not events:
        return "Nemáš přiřazené žádné NPC role na tuto hru."

    parts = [f"TVŮJ ROZPIS ({len(events)} událostí):"]
    for ev in events:
        block = [f"━━━ {ev.get('eventName', '?')} ━━━"]

        if npc := ev.get("npcName"):
            role_in = ev.get("npcRoleInEvent")
            role_type = ev.get("npcRole")
            npc_line = f"Hraješ: **{npc}**"
            if role_type:
                npc_line += f" ({role_type})"
            if role_in:
                npc_line += f" — {role_in}"
            block.append(npc_line)

        for ts in ev.get("timeSlots", []):
            start = ts.get("startTime")
            duration = ts.get("durationHours", 0)
            if start:
                block.append(f"⏰ {_format_prague(start)} ({duration}h)")

        if locs := ev.get("locationNames"):
            block.append(f"📍 {', '.join(locs)}")
        if quests := ev.get("questNames"):
            block.append(f"🎯 Questy: {', '.join(quests)}")
        if desc := ev.get("description"):
            block.append(f"ℹ️ {desc}")

        parts.append("\n".join(block))

    return "\n\n".join(parts)


def format_game_event(event: Optional[dict], label: str = "UDÁLOST") -> str:
    """Format a single game event (current or upcoming)."""
    if not event:
        return f"Žádná {label.lower()} nenalezena."

    parts = [f"{label}: {event.get('name', '?')}"]
    if desc := event.get("description"):
        parts.append(desc)

    for ts in event.get("timeSlots", []):
        start = ts.get("startTime")
        duration = ts.get("durationHours", 0)
        if start:
            parts.append(f"⏰ {_format_prague(start)} ({duration}h)")

    if locs := event.get("locationNames"):
        parts.append(f"📍 {', '.join(locs)}")
    if npcs := event.get("npcNames"):
        parts.append(f"👥 NPC: {', '.join(npcs)}")
    if quests := event.get("questNames"):
        parts.append(f"🎯 Questy: {', '.join(quests)}")

    return "\n".join(parts)


def format_next_events(events: list[dict]) -> str:
    """Format list of upcoming events."""
    if not events:
        return "Žádné nadcházející události."
    parts = [f"NADCHÁZEJÍCÍ UDÁLOSTI ({len(events)}):"]
    for ev in events:
        parts.append(format_game_event(ev, label="›"))
    return "\n\n".join(parts)
