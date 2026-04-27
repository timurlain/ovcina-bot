"""Tests for channels/api.py — the in-app consult Flask blueprint.

Engines are stubbed so the suite has no Anthropic / filesystem / config
dependency. The blueprint is mounted on a freshly-built Flask app per test
to keep state isolated.
"""

from __future__ import annotations

import os
from typing import Optional
from unittest.mock import patch

import pytest
from flask import Flask

from channels.api import bp as consult_bp


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeEngine:
    """Minimal stand-in for Rulemaster / LoreMaster.

    Records the args of the most recent .query()/.clear_history() call so tests
    can assert the blueprint mapped userEmail/userRole correctly. Async query
    matches both engine signatures (rulemaster: kwargs; loremaster: positional
    user dict).
    """

    def __init__(self, answer: str = "fake answer", tokens: int = 123):
        self._answer = answer
        self.last_tokens_used = tokens
        self.calls: list[dict] = []
        self.cleared: list[str] = []
        self._raise: Optional[Exception] = None

    def set_raise(self, exc: Exception):
        self._raise = exc

    async def query(self, user_key, message, *args, **kwargs):
        if self._raise is not None:
            raise self._raise
        self.calls.append({
            "user_key": user_key,
            "message": message,
            "args": args,
            "kwargs": kwargs,
        })
        return self._answer

    def clear_history(self, user_key):
        self.cleared.append(user_key)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_key():
    return "test-secret-123"


@pytest.fixture
def rulemaster():
    return FakeEngine(answer="rulemaster says foo", tokens=42)


@pytest.fixture
def loremaster():
    return FakeEngine(answer="loremaster says bar", tokens=99)


@pytest.fixture
def app(api_key, rulemaster, loremaster):
    flask_app = Flask("test_consult_api")
    flask_app.config["RULEMASTER"] = rulemaster
    flask_app.config["LOREMASTER"] = loremaster
    flask_app.register_blueprint(consult_bp)
    with patch.dict(os.environ, {"BOT_CONSULT_API_KEY": api_key}):
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def _auth_headers(api_key: str) -> dict:
    return {
        "X-Bot-Api-Key": api_key,
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_consult_rejects_request_without_api_key(client):
    resp = client.post(
        "/api/consult/rulemaster",
        json={"message": "x", "userEmail": "a@b", "userRole": "hráč"},
    )
    assert resp.status_code == 401
    assert resp.get_json() == {"error": "unauthorized"}


def test_consult_rejects_wrong_api_key(client, api_key):
    resp = client.post(
        "/api/consult/rulemaster",
        headers={"X-Bot-Api-Key": api_key + "-WRONG", "Content-Type": "application/json"},
        json={"message": "x", "userEmail": "a@b", "userRole": "hráč"},
    )
    assert resp.status_code == 401


def test_consult_rejects_when_env_unset(rulemaster, loremaster):
    flask_app = Flask("no_env")
    flask_app.config["RULEMASTER"] = rulemaster
    flask_app.config["LOREMASTER"] = loremaster
    flask_app.register_blueprint(consult_bp)
    with patch.dict(os.environ, {}, clear=True):
        c = flask_app.test_client()
        resp = c.post(
            "/api/consult/rulemaster",
            headers={"X-Bot-Api-Key": "anything", "Content-Type": "application/json"},
            json={"message": "x", "userEmail": "a@b", "userRole": "hráč"},
        )
    assert resp.status_code == 401


def test_reset_rejects_request_without_api_key(client):
    resp = client.post("/api/consult/rulemaster/reset", json={"userEmail": "a@b"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_consult_rejects_unknown_persona(client, api_key):
    resp = client.post(
        "/api/consult/wizard",
        headers=_auth_headers(api_key),
        json={"message": "x", "userEmail": "a@b", "userRole": "hráč"},
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "invalid_persona"}


def test_consult_rejects_missing_message(client, api_key):
    resp = client.post(
        "/api/consult/rulemaster",
        headers=_auth_headers(api_key),
        json={"userEmail": "a@b", "userRole": "hráč"},
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "missing_message"}


def test_consult_rejects_blank_message(client, api_key):
    resp = client.post(
        "/api/consult/rulemaster",
        headers=_auth_headers(api_key),
        json={"message": "   ", "userEmail": "a@b", "userRole": "hráč"},
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "missing_message"}


def test_consult_rejects_missing_user_email(client, api_key):
    resp = client.post(
        "/api/consult/rulemaster",
        headers=_auth_headers(api_key),
        json={"message": "x", "userRole": "hráč"},
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "missing_user_email"}


def test_reset_rejects_missing_user_email(client, api_key):
    resp = client.post(
        "/api/consult/rulemaster/reset",
        headers=_auth_headers(api_key),
        json={},
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "missing_user_email"}


def test_reset_rejects_unknown_persona(client, api_key):
    resp = client.post(
        "/api/consult/wizard/reset",
        headers=_auth_headers(api_key),
        json={"userEmail": "a@b"},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_consult_rulemaster_happy_path(client, api_key, rulemaster):
    resp = client.post(
        "/api/consult/rulemaster",
        headers=_auth_headers(api_key),
        json={
            "message": "Co dělá Drozd?",
            "userEmail": "TEST@example.com",
            "userRole": "hráč",
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"answer": "rulemaster says foo", "tokensUsed": 42}

    assert len(rulemaster.calls) == 1
    call = rulemaster.calls[0]
    # email is lowercased into the conversation key
    assert call["user_key"] == "api:test@example.com"
    assert call["message"] == "Co dělá Drozd?"
    # rulemaster signature uses kwargs
    assert call["kwargs"]["user_role"] == "hráč"
    assert call["kwargs"]["user_email"] == "TEST@example.com"


def test_consult_loremaster_happy_path(client, api_key, loremaster):
    resp = client.post(
        "/api/consult/loremaster",
        headers=_auth_headers(api_key),
        json={
            "message": "Kdo je Balin?",
            "userEmail": "u@x",
            "userRole": "hráč",
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"answer": "loremaster says bar", "tokensUsed": 99}

    call = loremaster.calls[0]
    # loremaster passes a user dict positionally
    assert call["args"] and call["args"][0] == {"email": "u@x", "role": "hráč"}


@pytest.mark.parametrize(
    "raw_role,expected_role",
    [
        ("admin", "organizátor"),
        ("organizator", "organizátor"),
        ("organizátor", "organizátor"),
        ("gm", "organizátor"),
        ("hráč", "hráč"),
        ("player", "hráč"),
        ("", "hráč"),  # empty / missing falls back to hráč
        ("garbage-value", "hráč"),  # unknown also falls back
    ],
)
def test_consult_normalizes_user_role(client, api_key, rulemaster, raw_role, expected_role):
    resp = client.post(
        "/api/consult/rulemaster",
        headers=_auth_headers(api_key),
        json={
            "message": "x",
            "userEmail": "a@b",
            "userRole": raw_role,
        },
    )
    assert resp.status_code == 200
    assert rulemaster.calls[-1]["kwargs"]["user_role"] == expected_role


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def test_reset_clears_history_with_correct_user_key(client, api_key, rulemaster):
    resp = client.post(
        "/api/consult/rulemaster/reset",
        headers=_auth_headers(api_key),
        json={"userEmail": "USER@example.com"},
    )
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}
    assert rulemaster.cleared == ["api:user@example.com"]


def test_reset_loremaster(client, api_key, loremaster):
    resp = client.post(
        "/api/consult/loremaster/reset",
        headers=_auth_headers(api_key),
        json={"userEmail": "u@x"},
    )
    assert resp.status_code == 200
    assert loremaster.cleared == ["api:u@x"]


# ---------------------------------------------------------------------------
# Upstream failure
# ---------------------------------------------------------------------------


def test_consult_returns_502_on_engine_exception(client, api_key, rulemaster):
    rulemaster.set_raise(RuntimeError("anthropic boom"))
    resp = client.post(
        "/api/consult/rulemaster",
        headers=_auth_headers(api_key),
        json={"message": "x", "userEmail": "a@b", "userRole": "hráč"},
    )
    assert resp.status_code == 502
    body = resp.get_json()
    assert body["error"] == "upstream_failure"
    assert "anthropic boom" in body["detail"]


def test_consult_returns_502_when_engine_unavailable(api_key, loremaster):
    """If the bootstrap forgot to wire RULEMASTER, surface a clean 502."""
    flask_app = Flask("missing_engine")
    # only loremaster set
    flask_app.config["LOREMASTER"] = loremaster
    flask_app.register_blueprint(consult_bp)
    with patch.dict(os.environ, {"BOT_CONSULT_API_KEY": api_key}):
        c = flask_app.test_client()
        resp = c.post(
            "/api/consult/rulemaster",
            headers=_auth_headers(api_key),
            json={"message": "x", "userEmail": "a@b", "userRole": "hráč"},
        )
    assert resp.status_code == 502
    assert resp.get_json() == {"error": "engine_unavailable"}
