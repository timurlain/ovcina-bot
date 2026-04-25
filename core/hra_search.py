"""OvčinaHra search API client — full-text search across locations, items, monsters, quests."""

from __future__ import annotations

import logging

import aiohttp

logger = logging.getLogger(__name__)


async def search(api_url: str, token: str, query: str, game_id: int | None = None, limit: int = 20) -> list[dict]:
    """Search hra.ovcina.cz for entities matching query."""
    url = f"{api_url}/api/search"
    params = {"q": query, "limit": limit}
    if game_id:
        params["gameId"] = game_id
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", [])
                logger.error(f"hra search failed: {resp.status}")
    except Exception as e:
        logger.error(f"hra search error: {e}")
    return []


async def get_detail(api_url: str, token: str, entity_type: str, entity_id: int) -> dict | None:
    """Fetch full detail for a specific entity."""
    # Entity type to endpoint mapping
    endpoints = {
        "Location": "locations",
        "Item": "items",
        "Monster": "monsters",
        "Quest": "quests",
    }
    endpoint = endpoints.get(entity_type)
    if not endpoint:
        return None

    url = f"{api_url}/api/{endpoint}/{entity_id}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.error(f"hra detail failed: {resp.status}")
    except Exception as e:
        logger.error(f"hra detail error: {e}")
    return None


async def search_and_detail(api_url: str, token: str, query: str, game_id: int | None = None, max_details: int = 5) -> str:
    """Search and fetch details for top results. Returns formatted context string."""
    results = await search(api_url, token, query, game_id)
    if not results:
        return ""

    sections = []
    detail_count = 0

    for r in results:
        if detail_count >= max_details:
            # Just list remaining without detail
            sections.append(f"- {r['entityType']}: {r['name']} — {(r.get('description') or '')[:200]}")
            continue

        detail = await get_detail(api_url, token, r["entityType"], r["id"])
        if detail:
            detail_count += 1
            lines = [f"### {r['entityType']}: {detail.get('name', r['name'])}"]
            for key in ("description", "details", "region", "npcInfo", "effect", "abilities"):
                val = detail.get(key)
                if val:
                    lines.append(f"**{key}:** {val}")
            sections.append("\n".join(lines))
        else:
            sections.append(f"- {r['entityType']}: {r['name']} — {(r.get('description') or '')[:200]}")

    header = f"**Výsledky z hra.ovcina.cz ({len(results)} nalezeno):**\n"
    return header + "\n\n".join(sections)
