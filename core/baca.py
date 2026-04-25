"""Bača task creation — POST to baca.ovcina.cz API."""

from __future__ import annotations

import aiohttp


async def create_task(api_url: str, api_key: str, title: str, source: str = "ovcina-bot") -> dict | None:
    """Create a task in Bača. Returns {"id", "title", "url"} or None on failure."""
    url = f"{api_url}/api/tasks"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "title": title,
        "source": source,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, ssl=False) as resp:
                if resp.status in (200, 201):
                    data = await resp.json()
                    task_id = data.get("id")
                    return {
                        "id": task_id,
                        "title": data.get("title"),
                        "url": data.get("url") or f"{api_url}/tasks/{task_id}",
                    }
                return None
    except Exception:
        return None
