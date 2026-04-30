"""Tests for channels/telegram_webhook.py — the Telegram webhook blueprint.

Mounted on its own Flask app per test so there is no engine / config /
anthropic / python-telegram-bot dependency. The runtime registry, the
Update parser and the cross-thread scheduler are all stubbed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from channels.telegram_webhook import bp as telegram_bp


def _make_app():
    app = Flask("test_telegram_webhook")
    app.register_blueprint(telegram_bp)
    return app


def _runtime(loop=None, rm_app=None, lm_app=None, rm_secret=None, lm_secret=None):
    rt = MagicMock()
    rt.snapshot.return_value = (loop, rm_app, lm_app, rm_secret, lm_secret)
    return rt


@pytest.fixture
def app():
    return _make_app()


@pytest.fixture
def client(app):
    return app.test_client()


def _post(client, persona, headers=None, body=None):
    headers = headers or {}
    headers.setdefault("Content-Type", "application/json")
    return client.post(f"/webhook/telegram/{persona}", json=body or {}, headers=headers)


def test_invalid_persona_returns_400(client):
    """Persona check is the first gate, runs before runtime lookup."""
    resp = _post(client, "wizard", headers={"X-Telegram-Bot-Api-Secret-Token": "x"})
    assert resp.status_code == 400


def test_runtime_not_ready_returns_503(client):
    """No loop yet → Telegram should retry, not lose the update."""
    rt = _runtime(loop=None)
    with patch("channels.telegram_webhook._get_runtime", return_value=rt):
        resp = _post(client, "rulemaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret"})
    assert resp.status_code == 503


def test_target_app_missing_returns_503(client):
    """Loop is up but rulemaster app didn't initialize → 503, no crash."""
    loop = MagicMock()
    rt = _runtime(loop=loop, rm_app=None, lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")
    with patch("channels.telegram_webhook._get_runtime", return_value=rt):
        resp = _post(client, "rulemaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret"})
    assert resp.status_code == 503


def test_missing_secret_token_returns_401(client):
    rt = _runtime(loop=MagicMock(), rm_app=MagicMock(), lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")
    with patch("channels.telegram_webhook._get_runtime", return_value=rt):
        resp = _post(client, "rulemaster")
    assert resp.status_code == 401


def test_wrong_secret_token_returns_401(client):
    rt = _runtime(loop=MagicMock(), rm_app=MagicMock(), lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")
    with patch("channels.telegram_webhook._get_runtime", return_value=rt):
        resp = _post(client, "rulemaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "WRONG"})
    assert resp.status_code == 401


def test_secret_isolation_between_personas(client):
    """rulemaster's secret must not pass loremaster's auth (or vice versa)."""
    rt = _runtime(loop=MagicMock(), rm_app=MagicMock(), lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")
    with patch("channels.telegram_webhook._get_runtime", return_value=rt):
        resp = _post(client, "loremaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret"})
    assert resp.status_code == 401


def test_no_secret_required_when_runtime_secret_is_none(client):
    """If a bot was registered without a secret token (dev), accept any
    request without an X-Telegram-Bot-Api-Secret-Token header."""
    rt = _runtime(loop=MagicMock(), rm_app=MagicMock(), lm_app=MagicMock(),
                  rm_secret=None, lm_secret=None)
    with patch("channels.telegram_webhook._get_runtime", return_value=rt), \
         patch("channels.telegram_webhook._telegram_update_class") as cls_factory, \
         patch("channels.telegram_webhook.asyncio.run_coroutine_threadsafe") as sched:
        cls_factory.return_value.de_json.return_value = MagicMock()
        resp = _post(client, "rulemaster", body={"update_id": 1})
    assert resp.status_code == 200
    sched.assert_called_once()


def test_empty_payload_returns_200_ignored(client):
    rt = _runtime(loop=MagicMock(), rm_app=MagicMock(), lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")
    with patch("channels.telegram_webhook._get_runtime", return_value=rt):
        resp = client.post(
            "/webhook/telegram/rulemaster",
            data="",
            headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret",
                     "Content-Type": "application/json"},
        )
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ignored"}


def test_malformed_payload_returns_400(client):
    """Update.de_json raising should produce a 400, not propagate."""
    rt = _runtime(loop=MagicMock(), rm_app=MagicMock(), lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")
    with patch("channels.telegram_webhook._get_runtime", return_value=rt), \
         patch("channels.telegram_webhook._telegram_update_class") as cls_factory:
        cls_factory.return_value.de_json.side_effect = ValueError("bad shape")
        resp = _post(client, "rulemaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret"},
                     body={"some": "junk"})
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "bad_payload"}


def test_happy_path_dispatches_to_rulemaster_app(client):
    loop = MagicMock(name="loop")
    rm_app = MagicMock(name="rm_app")
    lm_app = MagicMock(name="lm_app")
    rt = _runtime(loop=loop, rm_app=rm_app, lm_app=lm_app,
                  rm_secret="rm-secret", lm_secret="lm-secret")
    fake_update = MagicMock(name="update")

    with patch("channels.telegram_webhook._get_runtime", return_value=rt), \
         patch("channels.telegram_webhook._telegram_update_class") as cls_factory, \
         patch("channels.telegram_webhook.asyncio.run_coroutine_threadsafe") as sched:
        cls_factory.return_value.de_json.return_value = fake_update
        resp = _post(client, "rulemaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret"},
                     body={"update_id": 1, "message": {"text": "hi"}})

    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
    assert sched.call_count == 1
    coro_arg, loop_arg = sched.call_args.args
    assert loop_arg is loop
    rm_app.process_update.assert_called_once_with(fake_update)
    lm_app.process_update.assert_not_called()


def test_loremaster_route_dispatches_to_loremaster_app(client):
    loop = MagicMock(name="loop")
    rm_app = MagicMock(name="rm_app")
    lm_app = MagicMock(name="lm_app")
    rt = _runtime(loop=loop, rm_app=rm_app, lm_app=lm_app,
                  rm_secret="rm-secret", lm_secret="lm-secret")

    with patch("channels.telegram_webhook._get_runtime", return_value=rt), \
         patch("channels.telegram_webhook._telegram_update_class") as cls_factory, \
         patch("channels.telegram_webhook.asyncio.run_coroutine_threadsafe") as sched:
        cls_factory.return_value.de_json.return_value = MagicMock()
        resp = _post(client, "loremaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "lm-secret"},
                     body={"update_id": 1})

    assert resp.status_code == 200
    rm_app.process_update.assert_not_called()
    lm_app.process_update.assert_called_once()
    sched.assert_called_once()


def test_dispatch_failure_returns_500(client):
    """If run_coroutine_threadsafe raises (loop closed, e.g.) we surface a
    500 instead of leaking the exception."""
    loop = MagicMock(name="loop")
    rm_app = MagicMock(name="rm_app")
    rt = _runtime(loop=loop, rm_app=rm_app, lm_app=MagicMock(),
                  rm_secret="rm-secret", lm_secret="lm-secret")

    with patch("channels.telegram_webhook._get_runtime", return_value=rt), \
         patch("channels.telegram_webhook._telegram_update_class") as cls_factory, \
         patch("channels.telegram_webhook.asyncio.run_coroutine_threadsafe",
               side_effect=RuntimeError("loop closed")):
        cls_factory.return_value.de_json.return_value = MagicMock()
        resp = _post(client, "rulemaster",
                     headers={"X-Telegram-Bot-Api-Secret-Token": "rm-secret"},
                     body={"update_id": 1})

    assert resp.status_code == 500
    assert resp.get_json() == {"error": "dispatch_failed"}
