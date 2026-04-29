"""Tests for lookup_user_character — the registrace-side postava lookup."""

from __future__ import annotations

import asyncio
from unittest.mock import patch, MagicMock

import pytest

from core.auth import lookup_user_character


class _FakeResponse:
    def __init__(self, status: int, payload: dict | None):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    def __init__(self, response: _FakeResponse):
        self._response = response
        self.calls: list[tuple[str, dict, dict]] = []

    def get(self, url, params=None, headers=None, ssl=None):
        self.calls.append((url, params or {}, headers or {}))
        return self._response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def _patch_session(session: _FakeSession):
    return patch("core.auth.aiohttp.ClientSession", return_value=session)


def test_returns_first_non_null_character_name():
    payload = {
        "registered": True,
        "attendees": [
            {"firstName": "Petr", "lastName": "Marek", "characterName": None},
            {"firstName": "Drozd", "lastName": "Marek", "characterName": "Drozd"},
            {"firstName": "Sova", "lastName": "Marek", "characterName": "Sova"},
        ],
    }
    session = _FakeSession(_FakeResponse(200, payload))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result == "Drozd"

    # URL + headers + params shape
    url, params, headers = session.calls[0]
    assert url == "https://registrace.test/api/v1/users/petr@example.cz/game-info"
    assert params == {"gameId": 1}
    assert headers == {"X-Api-Key": "k123"}


def test_returns_none_when_no_attendees_have_characters():
    payload = {
        "registered": True,
        "attendees": [
            {"firstName": "Petr", "lastName": "Marek", "characterName": None},
            {"firstName": "Eva",  "lastName": "Marek", "characterName": None},
        ],
    }
    session = _FakeSession(_FakeResponse(200, payload))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result is None


def test_returns_none_when_attendees_missing():
    payload = {"registered": True}
    session = _FakeSession(_FakeResponse(200, payload))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result is None


def test_returns_none_when_user_not_registered():
    """Endpoint may return null body on unregistered users — code must tolerate that."""
    session = _FakeSession(_FakeResponse(200, None))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "stranger@example.cz", 1,
        ))
    assert result is None


def test_returns_none_on_404():
    session = _FakeSession(_FakeResponse(404, None))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result is None


def test_returns_none_on_500():
    session = _FakeSession(_FakeResponse(500, None))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result is None


def test_returns_none_on_network_error():
    """Connection failure must not blow up the verify flow."""
    bad_session = MagicMock()
    bad_session.__aenter__ = MagicMock(side_effect=ConnectionError("boom"))
    with patch("core.auth.aiohttp.ClientSession", return_value=bad_session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result is None


def test_skips_attendees_with_empty_string_character_name():
    """characterName == '' should be treated the same as None."""
    payload = {
        "attendees": [
            {"characterName": ""},
            {"characterName": "Drozd"},
        ],
    }
    session = _FakeSession(_FakeResponse(200, payload))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result == "Drozd"


def test_handles_attendee_being_none():
    """Defensive: a None entry in the attendees list shouldn't crash."""
    payload = {
        "attendees": [None, {"characterName": "Drozd"}],
    }
    session = _FakeSession(_FakeResponse(200, payload))
    with _patch_session(session):
        result = asyncio.run(lookup_user_character(
            "https://registrace.test", "k123", "petr@example.cz", 1,
        ))
    assert result == "Drozd"
