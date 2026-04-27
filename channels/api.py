"""Consult API — Flask blueprint for in-app consult from ovcinahra.

Mounts on the existing port-8080 Flask app. Two endpoints per persona
(rulemaster, loremaster):

    POST /api/consult/<persona>
        body: {"message": str, "userEmail": str, "userRole": str}
        200:  {"answer": str, "tokensUsed": int}

    POST /api/consult/<persona>/reset
        body: {"userEmail": str}
        200:  {"ok": true}

Auth: X-Bot-Api-Key header must match BOT_CONSULT_API_KEY env var.
If env is not set, the API rejects all requests (closed by default).

Engine handles are looked up via app.config["RULEMASTER"] / app.config["LOREMASTER"];
the WhatsApp channel attaches them at construction time.
"""

from __future__ import annotations

import asyncio
import logging
import os

from flask import Blueprint, current_app, jsonify, request

logger = logging.getLogger(__name__)

bp = Blueprint("consult_api", __name__, url_prefix="/api/consult")

VALID_PERSONAS = {"rulemaster", "loremaster"}

# JWT roles arrive in English-ish form ("organizator", "admin"). Engines expect
# Czech "organizátor" (with diacritic) — mapped here at the boundary so the
# wire contract stays language-neutral.
_ROLE_MAP = {
    "admin": "organizátor",
    "organizator": "organizátor",
    "organizátor": "organizátor",
    "gm": "organizátor",
    "hráč": "hráč",
    "hrac": "hráč",
    "player": "hráč",
}


def _normalize_role(raw: str) -> str:
    """Normalize an inbound userRole string to the Czech form engines expect."""
    return _ROLE_MAP.get((raw or "").strip().lower(), "hráč")


def _expected_api_key() -> str:
    return (os.environ.get("BOT_CONSULT_API_KEY") or "").strip()


def _require_api_key() -> bool:
    expected = _expected_api_key()
    if not expected:
        # Closed by default if env not set — no static fallback.
        return False
    provided = (request.headers.get("X-Bot-Api-Key") or "").strip()
    return provided == expected


@bp.before_request
def _auth():
    if not _require_api_key():
        return jsonify({"error": "unauthorized"}), 401
    return None


def _engine_for(persona: str):
    key = "RULEMASTER" if persona == "rulemaster" else "LOREMASTER"
    return current_app.config.get(key)


def _user_key(email: str) -> str:
    return f"api:{email.lower()}"


def _run_async(coro):
    """Drive an async coroutine to completion from the sync Flask thread."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@bp.post("/<persona>")
def consult(persona: str):
    if persona not in VALID_PERSONAS:
        return jsonify({"error": "invalid_persona"}), 400

    body = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    user_email = (body.get("userEmail") or "").strip()
    raw_role = body.get("userRole") or ""

    if not message:
        return jsonify({"error": "missing_message"}), 400
    if not user_email:
        return jsonify({"error": "missing_user_email"}), 400

    user_role = _normalize_role(raw_role)
    user_key = _user_key(user_email)
    engine = _engine_for(persona)

    if engine is None:
        logger.error("Consult API: no engine wired for persona=%s", persona)
        return jsonify({"error": "engine_unavailable"}), 502

    async def _call():
        if persona == "rulemaster":
            return await engine.query(
                user_key,
                message,
                user_role=user_role,
                user_email=user_email,
            )
        # loremaster expects a user dict; postava/frakce stay defaulted.
        user_dict = {"email": user_email, "role": user_role}
        return await engine.query(user_key, message, user_dict)

    try:
        answer = _run_async(_call())
    except Exception as exc:
        logger.exception("Consult API: upstream failure for persona=%s", persona)
        return jsonify({"error": "upstream_failure", "detail": str(exc)}), 502

    tokens_used = int(getattr(engine, "last_tokens_used", 0) or 0)
    return jsonify({"answer": answer, "tokensUsed": tokens_used}), 200


@bp.post("/<persona>/reset")
def reset(persona: str):
    if persona not in VALID_PERSONAS:
        return jsonify({"error": "invalid_persona"}), 400

    body = request.get_json(silent=True) or {}
    user_email = (body.get("userEmail") or "").strip()
    if not user_email:
        return jsonify({"error": "missing_user_email"}), 400

    engine = _engine_for(persona)
    if engine is None:
        return jsonify({"error": "engine_unavailable"}), 502

    engine.clear_history(_user_key(user_email))
    return jsonify({"ok": True}), 200
