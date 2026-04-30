"""Telegram webhook — Flask blueprint mounted on the existing port-8080 app.

Telegram pushes Update JSON to:
    POST /webhook/telegram/<persona>     (persona ∈ {rulemaster, loremaster})

Each route validates the X-Telegram-Bot-Api-Secret-Token header (when a secret
was registered with Telegram), parses the body via Update.de_json, and
schedules application.process_update onto the Telegram event loop running on
a different thread via asyncio.run_coroutine_threadsafe.

The runtime registry (loop + Application instances + secrets) is owned by
``channels.telegram`` and updated when start_telegram_bots() finishes its
webhook setup. We import the getter lazily to avoid a circular dep at module
load time and to keep the test surface narrow.
"""

from __future__ import annotations

import asyncio
import json
import logging

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

bp = Blueprint("telegram_webhook", __name__, url_prefix="/webhook/telegram")

VALID_PERSONAS = {"rulemaster", "loremaster"}


def _get_runtime():
    """Lazy import of the runtime registry from channels.telegram."""
    from channels.telegram import get_webhook_runtime
    return get_webhook_runtime()


def _telegram_update_class():
    """Lazy import of telegram.Update — keeps blueprint importable in tests
    without requiring python-telegram-bot at module load time."""
    from telegram import Update
    return Update


@bp.post("/<persona>")
def telegram_webhook(persona: str):
    if persona not in VALID_PERSONAS:
        return jsonify({"error": "invalid_persona"}), 400

    rt = _get_runtime()
    loop, rm_app, lm_app, rm_secret, lm_secret = rt.snapshot()
    if loop is None:
        # Telegram applications haven't finished starting yet (cold-start race
        # with the Flask thread). Return 503 so Telegram retries instead of
        # dropping the update.
        return jsonify({"status": "not_ready"}), 503

    target_app = rm_app if persona == "rulemaster" else lm_app
    expected_secret = rm_secret if persona == "rulemaster" else lm_secret

    if target_app is None:
        return jsonify({"status": "not_ready"}), 503

    if expected_secret:
        provided = request.headers.get("X-Telegram-Bot-Api-Secret-Token") or ""
        if provided != expected_secret:
            logger.warning("Telegram %s webhook secret mismatch", persona)
            return jsonify({"error": "unauthorized"}), 401

    # Distinguish empty body from malformed JSON. request.get_json(silent=True)
    # collapses both to None, which would let invalid payloads reply 200 ignored
    # and Telegram would stop retrying — a real update could be silently dropped.
    raw = request.get_data(as_text=True) or ""
    if not raw.strip():
        return jsonify({"status": "ignored"}), 200
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Telegram %s webhook: malformed JSON body: %s", persona, e)
        return jsonify({"error": "bad_payload"}), 400
    if not isinstance(payload, dict) or not payload:
        return jsonify({"error": "bad_payload"}), 400

    Update = _telegram_update_class()
    try:
        update = Update.de_json(payload, target_app.bot)
    except Exception as e:
        logger.exception("Failed to parse Telegram %s update: %s", persona, e)
        return jsonify({"error": "bad_payload"}), 400

    # Schedule processing on the Telegram thread's loop — fire-and-forget.
    # We want a fast 200 back so Telegram doesn't retry on slow handlers.
    try:
        asyncio.run_coroutine_threadsafe(target_app.process_update(update), loop)
    except Exception as e:
        logger.exception("Failed to dispatch Telegram %s update: %s", persona, e)
        return jsonify({"error": "dispatch_failed"}), 500

    return jsonify({"status": "ok"}), 200
