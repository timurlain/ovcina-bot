"""WhatsApp channel — via WAHA (WhatsApp HTTP API) Docker container."""

from __future__ import annotations

import asyncio
import logging
import re

from flask import Flask, request, jsonify
import aiohttp

from channels.api import bp as consult_bp
from core.auth import UserStore, send_verification_email, check_registration
from core.router import route
from core.notes import detect_note, save_note
from core.question_log import log_question
from core.baca import create_task

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from sync Flask context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _waha_send(waha_url: str, api_key: str, chat_id: str, text: str, session: str = "default"):
    """Send a text message via WAHA API."""
    url = f"{waha_url}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": session,
    }
    headers = {"X-Api-Key": api_key} if api_key else {}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, json=payload, headers=headers) as resp:
                if resp.status not in (200, 201):
                    body = await resp.text()
                    logger.error(f"WAHA sendText failed: {resp.status} body={body[:200]}")
    except Exception as e:
        logger.error(f"WAHA sendText error: {e}")


class WhatsAppChannel:
    """Flask app handling WAHA webhook for WhatsApp messages."""

    def __init__(self, config, user_store, rulemaster, loremaster):
        self.config = config
        self.user_store = user_store
        self.rulemaster = rulemaster
        self.loremaster = loremaster
        self.waha_url = config.waha.url
        self.waha_api_key = getattr(config.waha, 'api_key', '')
        self.app = Flask(__name__)
        # Dedupe webhook deliveries — WAHA/cloudflared can fire the same message twice
        from collections import deque
        import threading
        self._seen_ids = deque(maxlen=512)
        self._seen_lock = threading.Lock()
        self._bot_jid_cache = None
        self._register_routes()
        # Mount the in-app consult API on the same Flask app so it lives behind
        # the existing port-8080 ingress. Engines are exposed via app.config so
        # the blueprint can dispatch by persona without import cycles.
        self.app.config["RULEMASTER"] = rulemaster
        self.app.config["LOREMASTER"] = loremaster
        self.app.register_blueprint(consult_bp)

    def _bot_jid(self):
        """Bot's own WhatsApp JID (e.g. '420735907567@c.us'), cached."""
        if self._bot_jid_cache:
            return self._bot_jid_cache
        try:
            import urllib.request, json
            req = urllib.request.Request(
                f"{self.waha_url}/api/sessions/default",
                headers={"X-Api-Key": self.waha_api_key} if self.waha_api_key else {},
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
                me = data.get("me") or {}
                self._bot_jid_cache = me.get("id")
        except Exception as e:
            logger.warning(f"Failed to fetch bot JID from WAHA: {e}")
        return self._bot_jid_cache

    def _register_routes(self):
        @self.app.route("/webhook/whatsapp", methods=["POST"])
        def whatsapp_webhook():
            return self._handle_webhook()

        @self.app.route("/health", methods=["GET"])
        def health():
            return "OK", 200

    def _handle_webhook(self):
        """Handle incoming WhatsApp message from WAHA."""
        data = request.json
        if not data:
            return jsonify({"status": "ignored"}), 200

        event = data.get("event")
        if event != "message":
            return jsonify({"status": "ignored"}), 200

        payload = data.get("payload", {})

        msg_id = payload.get("id")
        if msg_id:
            with self._seen_lock:
                if msg_id in self._seen_ids:
                    return jsonify({"status": "duplicate"}), 200
                self._seen_ids.append(msg_id)

        # Skip messages sent by us
        if payload.get("fromMe"):
            return jsonify({"status": "ignored"}), 200

        chat_id = payload.get("from", "")
        body = payload.get("body", "").strip()

        if not body or not chat_id:
            return jsonify({"status": "ignored"}), 200

        # Group chat filtering — only respond to explicit @mention of the bot
        # or a quoted-reply to a bot message. Keyword matching is too loose
        # (any mention of "bot" or "Ovčina" in conversation triggers false replies).
        is_group = chat_id.endswith("@g.us")
        if is_group:
            bot_jid = self._bot_jid()
            is_command = body.startswith("/")

            mentioned = (
                payload.get("mentionedIds")
                or payload.get("_data", {}).get("mentionedIds")
                or []
            )
            is_mention = bot_jid and any(
                bot_jid == m or (isinstance(m, dict) and m.get("_serialized") == bot_jid)
                for m in mentioned
            )

            quoted_participant = (
                payload.get("_data", {}).get("quotedParticipant")
                or payload.get("quotedParticipant")
                or ""
            )
            is_quoted_reply = bot_jid and bot_jid.split("@")[0] in str(quoted_participant)

            if not (is_command or is_mention or is_quoted_reply):
                return jsonify({"status": "ignored_group"}), 200

        # Extract phone number from chat_id
        phone = chat_id.replace("@c.us", "").replace("@s.whatsapp.net", "").replace("@g.us", "")

        response = _run_async(self._process_message(phone, chat_id, body))

        # Send response via WAHA API
        _run_async(_waha_send(self.waha_url, self.waha_api_key, chat_id, response))

        return jsonify({"status": "ok"}), 200

    async def _process_message(self, phone: str, chat_id: str, body: str) -> str:
        """Process a message — auth check, then route."""
        user = await self.user_store.get_user("whatsapp", phone)

        if not user:
            return await self._handle_unverified(phone, body)
        return await self._handle_verified(phone, chat_id, body, user)

    async def _handle_unverified(self, phone: str, body: str) -> str:
        """Handle messages from unverified users."""
        config = self.config

        # Check for 6-digit verification code
        if re.match(r"^\d{6}$", body):
            email = self.user_store.verify_code("whatsapp", phone, body, config.auth.code_expiry_minutes)
            if email:
                role = "organizátor" if self._is_organizer(email) else "hráč"
                await self.user_store.save_user("whatsapp", phone, email, role)
                return (
                    f"Ověřeno! Jsi přihlášen/a jako {email} (role: {role}).\n\n"
                    "Teď se můžeš ptát:\n"
                    "• Na pravidla — napiš /pravidlo <dotaz>\n"
                    "• Na svět — napiš /lore <dotaz>\n"
                    "• Nebo prostě napiš otázku a já ji nasměruji správně."
                )
            return "Neplatný nebo prošlý kód. Zkus to znovu nebo pošli email."

        # Check for email
        if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", body):
            email = body.lower()
            is_registered = await check_registration(
                config.registrace.api_url, config.registrace.api_key,
                email, config.registrace.game_id,
            )
            if not is_registered and not self._is_organizer(email):
                return (
                    f"Email {email} není registrován na Ovčinu. "
                    "Zkontroluj email nebo se nejdřív zaregistruj."
                )
            code = self.user_store.generate_code("whatsapp", phone, email)
            try:
                send_verification_email(
                    config.azure_email.connection_string,
                    config.azure_email.sender_address, email, code,
                )
                return f"📧 Poslal jsem ti kód na {email}. Napiš mi ho."
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                return "Nepodařilo se odeslat email. Zkus to za chvíli znovu."

        # Unknown — prompt for email
        return (
            "Ahoj! Jsem Ovčina Bot — rozhodčí pravidel a průvodce světem. 🐑\n\n"
            "Pro ověření mi pošli svůj email, pod kterým jsi registrován/a na Ovčinu."
        )

    async def _handle_verified(self, phone: str, chat_id: str, body: str, user: dict) -> str:
        """Route verified user's message to appropriate engine."""
        user_key = f"whatsapp:{phone}"

        # Commands
        if body.lower().startswith("/pravidlo "):
            query = body[10:].strip()
            if not query:
                return "Napiš dotaz: /pravidlo <tvůj dotaz>"
            await _waha_send(self.waha_url, self.waha_api_key, chat_id, "🔍 Hledám v pravidlech...")
            try:
                role = "organizátor" if self._is_organizer(user["email"]) else user["role"]
                answer = await self.rulemaster.query(user_key, query, role, user_email=user["email"])
                await log_question(user["email"], "Rulemaster-WA", query, answer)
                return answer
            except Exception as e:
                logger.error("Rulemaster query failed (WA): %s", e, exc_info=True)
                return "Omlouvám se, něco se pokazilo při hledání odpovědi. Zkus to prosím znovu."

        if body.lower().startswith("/lore "):
            query = body[6:].strip()
            if not query:
                return "Napiš dotaz: /lore <tvůj dotaz>"
            await _waha_send(self.waha_url, self.waha_api_key, chat_id, "🔍 Prozkoumávám svět...")
            try:
                answer = await self.loremaster.query(user_key, query, user)
                await log_question(user["email"], "LoreMaster-WA", query, answer)
                return answer
            except Exception as e:
                logger.error("LoreMaster query failed (WA): %s", e, exc_info=True)
                return "Omlouvám se, něco se pokazilo při hledání odpovědi. Zkus to prosím znovu."

        if body.lower() == "/help":
            return self._help_text(user)

        if body.lower() == "/reset":
            self.rulemaster.clear_history(user_key)
            self.loremaster.clear_history(user_key)
            return "Historie konverzace vymazána (pravidla i lore)."

        if body.lower() == "/postava":
            return self._postava_text(user)

        # Fate-only command — hotfix rule
        if self._is_fate(user["email"]):
            if body.lower().startswith("/hotfix "):
                hf_text = body[8:].strip()
                if not hf_text:
                    return (
                        "Napiš hotfix takto: /hotfix <text pravidla>\n\n"
                        "Hotfix přepíše všechna ostatní pravidla a začne platit okamžitě."
                    )
                from core.hotfixes import add_hotfix
                result = add_hotfix(author_email=user["email"], author_role="Osud", text=hf_text)
                hot_id = result["id"]
                # Notify other Fate verified on WhatsApp
                await self._notify_other_fate_whatsapp(user["email"], hot_id, hf_text)
                return (
                    f"✅ *{hot_id}* zapsán\n\n"
                    f"_Autor:_ {user['email']} (Osud)\n"
                    f"_Text:_ {hf_text}\n\n"
                    f"Hotfix je teď platný — boti ho započítají od příští otázky a přepíše všechna pravidla."
                )

        # Organizer commands
        if self._is_organizer(user["email"]):
            if body.lower().startswith("/poznamka "):
                note_text = body[10:].strip()
                if note_text:
                    result = save_note(user["email"], note_text, source="WhatsApp")
                    return f"📝 {result}"
                return "Napiš poznámku: /poznamka <text>"

            if body.lower().startswith("/ukol "):
                title = body[6:].strip()
                if title:
                    result = await create_task(self.config.baca.api_url, self.config.baca.api_key, title)
                    if result and result.get("id"):
                        return f"✅ Úkol #{result['id']} vytvořen — {result.get('url', '')}"
                    return "❌ Nepodařilo se vytvořit úkol v Bače."
                return "Napiš úkol: /ukol <popis úkolu>"

            # Free-text note triggers
            note_body = detect_note(body)
            if note_body:
                result = save_note(user["email"], note_body, source="WhatsApp")
                return f"📝 {result}"

        # Auto-route free text
        await _waha_send(self.waha_url, self.waha_api_key, chat_id, "🔍 Přemýšlím...")
        try:
            engine = await route(
                self.rulemaster.client, self.config.anthropic.model, body,
            )

            if engine == "rulemaster":
                role = "organizátor" if self._is_organizer(user["email"]) else user["role"]
                answer = await self.rulemaster.query(user_key, body, role, user_email=user["email"])
                await log_question(user["email"], "Rulemaster-WA", body, answer)
                return answer
            else:
                answer = await self.loremaster.query(user_key, body, user)
                await log_question(user["email"], "LoreMaster-WA", body, answer)
                return answer
        except Exception as e:
            logger.error("WA query failed: %s", e, exc_info=True)
            return "Omlouvám se, něco se pokazilo při hledání odpovědi. Zkus to prosím znovu."

    def _is_organizer(self, email: str) -> bool:
        return email.lower() in [e.lower() for e in self.config.auth.organizer_emails]

    def _is_fate(self, email: str) -> bool:
        return email.lower() in [e.lower() for e in self.config.auth.fate_emails]

    async def _notify_other_fate_whatsapp(self, author_email: str, hot_id: str, text: str):
        """Send hotfix notification to other Fate users verified on WhatsApp."""
        msg = (
            f"🔔 Nový hotfix od {author_email}: *{hot_id}*\n\n"
            f"_{text}_\n\n"
            f"Platný okamžitě."
        )
        try:
            all_users = await self.user_store.list_users()
        except Exception as e:
            logger.warning("Failed to list users for hotfix notification: %s", e)
            return
        for u in all_users:
            if (
                u.get("channel_type") == "whatsapp"
                and self._is_fate(u["email"])
                and u["email"].lower() != author_email.lower()
            ):
                try:
                    await _waha_send(self.waha_url, self.waha_api_key, u["channel_id"], msg)
                except Exception as e:
                    logger.warning("Failed to notify %s about hotfix: %s", u["email"], e)

    def _help_text(self, user: dict) -> str:
        text = (
            "🐑 *Ovčina Bot — příkazy*\n\n"
            "*/pravidlo* <dotaz> — Pravidla hry\n"
            "*/lore* <dotaz> — Svět a příběhy\n"
            "*/postava* — Tvá postava a co víš\n"
            "*/reset* — Vymaž historii\n"
            "*/help* — Tento seznam\n\n"
            "Nebo prostě napiš otázku — bot pozná, jestli jde o pravidla nebo lore."
        )
        if self._is_organizer(user.get("email", "")):
            text += (
                "\n\n⭐ *Organizátorské:*\n"
                "*/poznamka* <text> — Zapiš poznámku\n"
                "*/ukol* <text> — Vytvoř úkol v Bače\n"
                "Nebo: Zapiš si... / Take a note..."
            )
        return text

    def _postava_text(self, user: dict) -> str:
        postava = user.get("postava") or "nepřiřazená"
        frakce = user.get("frakce") or "nepřiřazená"
        roles = self.loremaster._roles
        role_data = roles.get(postava, {})

        text = f"🧙 *Tvá postava*\n\nJméno: {postava}\nFrakce: {frakce}\n"
        if role_data:
            popis = role_data.get("popis", "")
            if popis:
                text += f"Popis: {popis}\n"
            vi_o = role_data.get("ví-o", [])
            if vi_o:
                text += f"\nVíš o: {', '.join(vi_o)}\n"
        else:
            text += "\n_Tvá postava zatím nemá přiřazený profil znalostí._\n"
        return text
