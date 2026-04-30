"""Telegram channel — two bots (Rulemaster + LoreMaster)."""

from __future__ import annotations

import asyncio
import logging
import re
import threading
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

from core.auth import UserStore, send_verification_email, check_registration, lookup_user_character
from core.notes import detect_note, save_note, list_notes
from core.question_log import init_question_log, log_question, get_recent_questions
from core.baca import create_task

logger = logging.getLogger(__name__)


# ============================================================
# Webhook runtime — handles shared with the Flask webhook routes.
#
# The Telegram Applications run on a dedicated asyncio loop in the main thread
# (started by start_telegram_bots). The Flask app handling the inbound webhook
# requests runs on a separate thread. The Flask handlers reach into the
# Telegram loop via `asyncio.run_coroutine_threadsafe`. Both the loop and the
# Application instances are exposed here as a small thread-safe registry.
# ============================================================

class _WebhookRuntime:
    """Thread-safe holder for cross-thread access to the Telegram loop + apps."""

    def __init__(self):
        self._lock = threading.Lock()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.rulemaster_app = None
        self.loremaster_app = None
        self.rulemaster_secret: str | None = None
        self.loremaster_secret: str | None = None

    def set(self, *, loop, rulemaster_app, loremaster_app,
            rulemaster_secret=None, loremaster_secret=None):
        with self._lock:
            self.loop = loop
            self.rulemaster_app = rulemaster_app
            self.loremaster_app = loremaster_app
            self.rulemaster_secret = rulemaster_secret
            self.loremaster_secret = loremaster_secret

    def snapshot(self):
        with self._lock:
            return (
                self.loop,
                self.rulemaster_app,
                self.loremaster_app,
                self.rulemaster_secret,
                self.loremaster_secret,
            )


_runtime = _WebhookRuntime()


def set_webhook_runtime(**kwargs):
    """Update the cross-thread runtime registry (called from the Telegram loop)."""
    _runtime.set(**kwargs)


def get_webhook_runtime() -> _WebhookRuntime:
    """Read access for Flask handlers running on the WhatsApp/HTTP thread."""
    return _runtime


FULL_RULES_URL = (
    "https://solvertech-my.sharepoint.com/:w:/g/personal/"
    "tomas_pajonk_solvertech_cz/IQAdV_WIsZSrTpUsW0lyTyqrAdyUqGVJ85pnf-upucy7hGw?e=SceaAc"
)


def _is_organizer(email: str, config) -> bool:
    return email.lower() in [e.lower() for e in config.auth.organizer_emails]


async def _resolve_postava(role: str, email: str, config) -> str | None:
    """Look up the player's character name from registrace at verify time.

    Only meaningful for hráč role — organizers route through the GM prompt
    and don't read postava. Returns None on any failure (logged).
    """
    if role != "hráč":
        return None
    try:
        return await lookup_user_character(
            config.registrace.api_url,
            config.registrace.integration_api_key,
            email,
            config.registrace.game_id,
        )
    except Exception as e:
        logger.warning("lookup_user_character failed for %s: %s", email, e)
        return None


def _is_fate(email: str, config) -> bool:
    return email.lower() in [e.lower() for e in config.auth.fate_emails]


async def _get_user_or_deny(update: Update, user_store: UserStore) -> dict | None:
    user = await user_store.get_user("telegram", str(update.effective_user.id))
    if not user:
        await update.message.reply_text("Nejsi ověřen/a. Pošli /start pro registraci.")
        return None
    return user


def _split_message(text: str, max_len: int = 4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


# ============================================================
# SHARED HANDLERS (both bots)
# ============================================================


async def cmd_poznamka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save a note (organizer only). Works on both bots."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user or not _is_organizer(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro organizátory.")
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Napiš poznámku: /poznamka <text>")
        return
    bot_name = context.bot_data.get("bot_name", "telegram")
    result = save_note(user["email"], text, source=bot_name)
    await update.message.reply_text(f"📝 {result}")


async def cmd_hotfix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Write a hotfix rule (Osud only). Overrides all pravidla immediately."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    if not _is_fate(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro Osudy.")
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text(
            "Napiš hotfix takto: `/hotfix <text pravidla>`\n\n"
            "Hotfix přepíše všechna ostatní pravidla a začne platit okamžitě pro všechny boty.",
            parse_mode="Markdown",
        )
        return

    from core.hotfixes import add_hotfix
    result = add_hotfix(author_email=user["email"], author_role="Osud", text=text)
    hot_id = result["id"]

    confirmation = (
        f"✅ *{hot_id}* zapsán\n\n"
        f"_Autor:_ {user['email']} (Osud)\n"
        f"_Text:_ {text}\n\n"
        f"Hotfix je teď platný — boti ho započítají od příští otázky a přepíše všechna pravidla."
    )
    await update.message.reply_text(confirmation, parse_mode="Markdown")

    # Notify other Fate verified on Telegram
    all_users = await user_store.list_users()
    notify_msg = (
        f"🔔 Nový hotfix od {user['email']}: *{hot_id}*\n\n"
        f"_{text}_\n\n"
        f"Platný okamžitě."
    )
    for u in all_users:
        if (
            u.get("channel_type") == "telegram"
            and _is_fate(u["email"], config)
            and u["email"].lower() != user["email"].lower()
        ):
            try:
                await context.bot.send_message(
                    chat_id=int(u["channel_id"]),
                    text=notify_msg,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.warning("Failed to notify %s about hotfix: %s", u["email"], e)


async def cmd_ukol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a task in Bača (organizer only). Works on both bots."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user or not _is_organizer(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro organizátory.")
        return
    title = " ".join(context.args) if context.args else ""
    if not title:
        await update.message.reply_text("Napiš úkol: /ukol <popis úkolu>")
        return
    await update.message.chat.send_action("typing")
    result = await create_task(config.baca.api_url, config.baca.api_key, title)
    if result and result.get("id"):
        url = result.get("url", "")
        await update.message.reply_text(
            f"✅ Úkol #{result['id']} vytvořen — {url}"
        )
    else:
        await update.message.reply_text(
            "❌ Nepodařilo se vytvořit úkol v Bače. Zkus to později."
        )


async def cmd_dotazy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List recent user questions (organizer only)."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user or not _is_organizer(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro organizátory.")
        return
    text = await get_recent_questions(limit=10)
    for chunk in _split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")


async def cmd_poznamky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List recent notes (organizer only)."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user or not _is_organizer(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro organizátory.")
        return
    text = list_notes(limit=5)
    for chunk in _split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")


# ============================================================
# RULEMASTER BOT HANDLERS
# ============================================================

# All handlers access shared state via context.bot_data (set in post_init)


async def rm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rulemaster /start — registration or command overview."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await user_store.get_user("telegram", str(update.effective_user.id))
    if user:
        text = (
            f"Už jsi ověřen/a jako {user['email']}.\n\n"
            "📖 *Dostupné příkazy:*\n"
            "/pravidlo <dotaz> — Zeptej se na pravidla\n"
            "/pravidla — Odkaz na kompletní pravidla\n"
            "/navrh <text> — Pošli návrh pravidla\n"
            "/index — Přehled pravidel\n"
            "/napoveda — Příručka bota (PDF)\n"
            "/reset — Vymaž historii konverzace\n"
            "/help — Úplný seznam příkazů\n"
        )
        if _is_organizer(user["email"], config):
            text += "\n⭐ /pruvodce — GM průvodce (PDF)\n"
        text += "\nNebo prostě napiš dotaz přímo do chatu!"
        await update.message.reply_text(text, parse_mode="Markdown")
        return

    await update.message.reply_text(
        "Ahoj! Jsem *Rulemaster* — rozhodčí pravidel Ovčiny. 📖\n\n"
        "Znám všech 76 pravidel hry a můžu ti na ně okamžitě odpovědět.\n\n"
        "Po ověření budeš mít k dispozici:\n"
        "• Ptát se na pravidla — stačí napsat dotaz\n"
        "• /pravidlo <dotaz> — cílený dotaz na pravidla\n"
        "• /pravidla — odkaz na kompletní pravidla\n"
        "• /navrh <text> — návrh nového pravidla\n"
        "• /index — přehled všech pravidel\n"
        "• /napoveda — příručka bota (PDF)\n"
        "• /reset — vymazat historii\n\n"
        "Pro ověření mi pošli svůj email, pod kterým jsi registrován/a na Ovčinu.",
        parse_mode="Markdown",
    )


async def rm_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rulemaster /help."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await user_store.get_user("telegram", str(update.effective_user.id))
    text = (
        "📖 *Rulemaster — příkazy*\n\n"
        "*Základní:*\n"
        "/start — Registrace a ověření\n"
        "/help — Tento seznam\n"
        "/napoveda — Příručka bota (PDF)\n"
    )
    if user:
        text += (
            "\n*Pravidla:*\n"
            "/pravidlo <dotaz> — Zeptej se na pravidla\n"
            "/pravidla — Odkaz na kompletní pravidla\n"
            "/navrh <text> — Pošli návrh pravidla\n"
            "/index — Přehled pravidel\n"
            "/reset — Vymaž historii konverzace\n"
            "\n💡 Nebo prostě napiš dotaz přímo do chatu!\n"
        )
        if _is_organizer(user["email"], config):
            text += (
                "\n⭐ *Organizátorské příkazy:*\n"
                "/kdo — Seznam ověřených uživatelů\n"
                "/pruvodce — GM průvodce (PDF)\n"
                "/poznamka <text> — Zapiš poznámku\n"
                "/poznamky — Posledních 5 poznámek\n"
                "/ukol <text> — Vytvoř úkol v Bače\n"
                "/dotazy — Posledních 10 dotazů uživatelů\n"
            )
    await update.message.reply_text(text, parse_mode="Markdown")


async def rm_pravidlo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask a rules question."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    rulemaster = context.bot_data["rulemaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Napiš dotaz: /pravidlo <tvůj dotaz>")
        return
    await update.message.chat.send_action("typing")
    role = "organizátor" if _is_organizer(user["email"], config) else user["role"]
    answer = await rulemaster.query(update.effective_user.id, query, role)
    await log_question(user["email"], "Rulemaster", query, answer)
    for chunk in _split_message(answer):
        await update.message.reply_text(chunk)


async def rm_pravidla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show link to the full rules document."""
    await update.message.reply_text(
        "📜 *Kompletní pravidla Ovčiny*\n\n"
        f"[Otevřít dokument s pravidly]({FULL_RULES_URL})\n\n"
        "Tento dokument obsahuje všechna aktuální pravidla hry. "
        "Pokud máš dotaz ke konkrétnímu pravidlu, napiš ho přímo do chatu "
        "nebo použij /pravidlo <dotaz>.",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


async def rm_navrh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Submit a rule proposal."""
    user_store = context.bot_data["user_store"]
    rulemaster = context.bot_data["rulemaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    proposal = " ".join(context.args) if context.args else ""
    if not proposal:
        await update.message.reply_text("Napiš návrh: /navrh <popis pravidla>")
        return
    result = await rulemaster.add_proposal(update.effective_user.id, proposal, user["email"])
    await update.message.reply_text(result)


async def rm_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show rule categories overview."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    index_path = config.pravidla_path / "_index.md"
    if not index_path.exists():
        await update.message.reply_text("Rejstřík pravidel není dostupný.")
        return
    text = index_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    header = "\n".join(lines[:7])
    await update.message.reply_text(header)


async def rm_napoveda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the player guide PDF."""
    pdf_path = Path(__file__).parent.parent / "popis-bota.pdf"
    if not pdf_path.exists():
        await update.message.reply_text("Příručka bota není momentálně dostupná.")
        return
    await update.message.reply_document(
        document=pdf_path,
        filename="Rulemaster-napoveda.pdf",
        caption="📖 Příručka Rulemaster bota — jak se ptát na pravidla Ovčiny.",
    )


async def rm_pruvodce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the GM guide PDF (organizer only)."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user or not _is_organizer(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro organizátory.")
        return
    pdf_path = Path(__file__).parent.parent / "gm-pruvodce.pdf"
    if not pdf_path.exists():
        await update.message.reply_text("GM průvodce není momentálně dostupný.")
        return
    await update.message.reply_document(
        document=pdf_path,
        filename="GM-pruvodce-Ovcina.pdf",
        caption="⭐ GM průvodce — kompletní pravidla včetně organizátorských mechanik.",
    )


async def rm_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear Rulemaster conversation history."""
    user_store = context.bot_data["user_store"]
    rulemaster = context.bot_data["rulemaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    rulemaster.clear_history(update.effective_user.id)
    await update.message.reply_text("Historie konverzace vymazána.")


async def rm_kdo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List verified users (organizer only)."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await _get_user_or_deny(update, user_store)
    if not user or not _is_organizer(user["email"], config):
        await update.message.reply_text("Tento příkaz je pouze pro organizátory.")
        return
    users = await user_store.list_users()
    if not users:
        await update.message.reply_text("Žádní ověření uživatelé.")
        return
    lines = ["*Ověření uživatelé:*\n"]
    for u in users:
        org_mark = " ⭐" if _is_organizer(u["email"], config) else ""
        lines.append(f"• {u['email']} ({u['role']}){org_mark}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def rm_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rulemaster free text — email verification or rule query."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    rulemaster = context.bot_data["rulemaster"]
    text = update.message.text.strip()
    tg_id = str(update.effective_user.id)

    # 6-digit verification code
    if re.match(r"^\d{6}$", text):
        email = await user_store.verify_code("telegram", tg_id, text, config.auth.code_expiry_minutes)
        if email:
            role = "organizátor" if _is_organizer(email, config) else "hráč"
            postava = await _resolve_postava(role, email, config)
            await user_store.save_user("telegram", tg_id, email, role, postava=postava)
            await update.message.reply_text(
                f"✅ Ověřeno! Jsi přihlášen/a jako {email} (role: {role}).\n"
                "Teď se můžeš ptát na pravidla — stačí napsat dotaz."
            )
        else:
            await update.message.reply_text(
                "❌ Neplatný nebo prošlý kód. Zkus to znovu nebo pošli email."
            )
        return

    # Email from unverified user
    user = await user_store.get_user("telegram", tg_id)
    if not user and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", text):
        email = text.lower()
        await update.message.chat.send_action("typing")
        is_registered = await check_registration(
            config.registrace.api_url,
            config.registrace.api_key,
            email,
            config.registrace.game_id,
        )
        if not is_registered and not _is_organizer(email, config):
            await update.message.reply_text(
                f"Email {email} není registrován na Ovčinu. "
                "Zkontroluj email nebo se nejdřív zaregistruj."
            )
            return
        code = await user_store.generate_code("telegram", tg_id, email)
        try:
            send_verification_email(
                config.azure_email.connection_string,
                config.azure_email.sender_address,
                email,
                code,
            )
            await update.message.reply_text(f"📧 Poslal jsem ti kód na {email}. Napiš mi ho.")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            await update.message.reply_text(
                "Nepodařilo se odeslat email. Zkus to za chvíli znovu."
            )
        return

    # Organizer note via free text ("Zapiš si...", "Take a note...", etc.)
    if user and _is_organizer(user["email"], config):
        note_body = detect_note(text)
        if note_body:
            result = save_note(user["email"], note_body, source="Rulemaster")
            await update.message.reply_text(f"📝 {result}")
            return

    # Verified user — rule query
    if user:
        status_msg = await update.message.reply_text("🔍 Hledám v pravidlech...")

        async def _rm_progress(status_text: str):
            try:
                await status_msg.edit_text(status_text)
            except Exception:
                pass

        try:
            role = "organizátor" if _is_organizer(user["email"], config) else user["role"]
            answer = await rulemaster.query(
                update.effective_user.id, text, role,
                user_email=user["email"], on_progress=_rm_progress,
            )
            await log_question(user["email"], "Rulemaster", text, answer)
        except Exception as e:
            logger.error("Rulemaster query failed: %s", e, exc_info=True)
            answer = "Omlouvám se, něco se pokazilo při hledání odpovědi. Zkus to prosím znovu."
        try:
            await status_msg.delete()
        except Exception:
            pass
        for chunk in _split_message(answer):
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(
            "Nejsi ověřen/a. Pošli mi svůj email pro ověření, nebo napiš /start."
        )


# ============================================================
# LOREMASTER BOT HANDLERS
# ============================================================


async def lm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """LoreMaster /start — registration or command overview."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    user = await user_store.get_user("telegram", str(update.effective_user.id))
    if user:
        postava = user.get("postava") or "nepřiřazená"
        frakce = user.get("frakce") or "nepřiřazená"
        text = (
            f"Už jsi ověřen/a jako {user['email']}.\n"
            f"Postava: *{postava}* | Frakce: *{frakce}*\n\n"
            "🌍 *Dostupné příkazy:*\n"
            "/lore <dotaz> — Zeptej se na svět\n"
            "/stav — Aktuální stav herního světa\n"
            "/postava — Tvá postava a co víš\n"
            "/reset — Vymaž historii konverzace\n"
            "/help — Úplný seznam příkazů\n"
            "\nNebo prostě napiš dotaz přímo do chatu!"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
        return

    await update.message.reply_text(
        "Ahoj! Jsem *LoreMaster* — průvodce světem Ovčiny. 🌍\n\n"
        "Znám historii, lokace, frakce a příběhy tohoto světa.\n"
        "Odpovím ti na základě toho, co tvá postava ví.\n\n"
        "Po ověření budeš mít k dispozici:\n"
        "• Ptát se na svět — stačí napsat dotaz\n"
        "• /lore <dotaz> — cílený dotaz\n"
        "• /stav — stav herního světa\n"
        "• /postava — info o tvé postavě\n"
        "• /reset — vymazat historii\n\n"
        "Pro ověření mi pošli svůj email, pod kterým jsi registrován/a na Ovčinu.",
        parse_mode="Markdown",
    )


async def lm_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """LoreMaster /help."""
    user_store = context.bot_data["user_store"]
    user = await user_store.get_user("telegram", str(update.effective_user.id))
    text = (
        "🌍 *LoreMaster — příkazy*\n\n"
        "*Základní:*\n"
        "/start — Registrace a ověření\n"
        "/help — Tento seznam\n"
    )
    if user:
        text += (
            "\n*Svět:*\n"
            "/lore <dotaz> — Zeptej se na svět\n"
            "/stav — Aktuální stav herního světa\n"
            "/postava — Tvá postava a co víš\n"
            "/reset — Vymaž historii konverzace\n"
            "\n💡 Nebo prostě napiš dotaz přímo do chatu!\n"
        )
        config = context.bot_data["config"]
        if _is_organizer(user["email"], config):
            text += (
                "\n⭐ *Organizátorské příkazy:*\n"
                "/poznamka <text> — Zapiš poznámku\n"
                "/poznamky — Posledních 5 poznámek\n"
                "/ukol <text> — Vytvoř úkol v Bače\n"
                "/dotazy — Posledních 10 dotazů uživatelů\n"
            )
    await update.message.reply_text(text, parse_mode="Markdown")


async def lm_lore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask a lore question."""
    user_store = context.bot_data["user_store"]
    loremaster = context.bot_data["loremaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Napiš dotaz: /lore <tvůj dotaz>")
        return
    await update.message.chat.send_action("typing")
    user_key = f"telegram:{update.effective_user.id}"
    answer = await loremaster.query(user_key, query, user)
    await log_question(user["email"], "LoreMaster", query, answer)
    for chunk in _split_message(answer):
        await update.message.reply_text(chunk)


async def lm_postava(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show character info and knowledge profile."""
    user_store = context.bot_data["user_store"]
    loremaster = context.bot_data["loremaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return

    postava = user.get("postava") or "nepřiřazená"
    frakce = user.get("frakce") or "nepřiřazená"

    roles = loremaster._roles
    role_data = roles.get(postava, {})

    text = f"🧙 *Tvá postava*\n\n*Jméno:* {postava}\n*Frakce:* {frakce}\n"
    if role_data:
        popis = role_data.get("popis", "")
        if popis:
            text += f"*Popis:* {popis}\n"
        vi_o = role_data.get("ví-o", [])
        if vi_o:
            text += f"\n*Víš o:* {', '.join(vi_o)}\n"
        nevi_o = role_data.get("neví-o", [])
        if nevi_o:
            text += f"*Nevíš o:* {', '.join(nevi_o)}\n"
    else:
        text += "\n_Tvá postava zatím nemá přiřazený profil znalostí._\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def lm_stav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the current state of the game world."""
    user_store = context.bot_data["user_store"]
    loremaster = context.bot_data["loremaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    await update.message.chat.send_action("typing")
    user_key = f"telegram:{update.effective_user.id}"
    answer = await loremaster.query(
        user_key,
        "Jaký je aktuální stav herního světa? Co se děje? Shrň situaci z pohledu mé postavy.",
        user,
    )
    for chunk in _split_message(answer):
        await update.message.reply_text(chunk)


async def lm_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear LoreMaster conversation history."""
    user_store = context.bot_data["user_store"]
    loremaster = context.bot_data["loremaster"]
    user = await _get_user_or_deny(update, user_store)
    if not user:
        return
    user_key = f"telegram:{update.effective_user.id}"
    loremaster.clear_history(user_key)
    await update.message.reply_text("Historie konverzace vymazána.")


async def lm_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """LoreMaster free text — email verification or lore query."""
    config = context.bot_data["config"]
    user_store = context.bot_data["user_store"]
    loremaster = context.bot_data["loremaster"]
    text = update.message.text.strip()
    tg_id = str(update.effective_user.id)

    # 6-digit verification code
    if re.match(r"^\d{6}$", text):
        email = await user_store.verify_code("telegram", tg_id, text, config.auth.code_expiry_minutes)
        if email:
            role = "organizátor" if _is_organizer(email, config) else "hráč"
            postava = await _resolve_postava(role, email, config)
            await user_store.save_user("telegram", tg_id, email, role, postava=postava)
            await update.message.reply_text(
                f"✅ Ověřeno! Jsi přihlášen/a jako {email} (role: {role}).\n"
                "Teď se můžeš ptát na svět — stačí napsat dotaz."
            )
        else:
            await update.message.reply_text(
                "❌ Neplatný nebo prošlý kód. Zkus to znovu nebo pošli email."
            )
        return

    # Email from unverified user
    user = await user_store.get_user("telegram", tg_id)
    if not user and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", text):
        email = text.lower()
        await update.message.chat.send_action("typing")
        is_registered = await check_registration(
            config.registrace.api_url,
            config.registrace.api_key,
            email,
            config.registrace.game_id,
        )
        if not is_registered and not _is_organizer(email, config):
            await update.message.reply_text(
                f"Email {email} není registrován na Ovčinu. "
                "Zkontroluj email nebo se nejdřív zaregistruj."
            )
            return
        code = await user_store.generate_code("telegram", tg_id, email)
        try:
            send_verification_email(
                config.azure_email.connection_string,
                config.azure_email.sender_address,
                email,
                code,
            )
            await update.message.reply_text(f"📧 Poslal jsem ti kód na {email}. Napiš mi ho.")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            await update.message.reply_text(
                "Nepodařilo se odeslat email. Zkus to za chvíli znovu."
            )
        return

    # Organizer note via free text ("Zapiš si...", "Take a note...", etc.)
    if user and _is_organizer(user["email"], config):
        note_body = detect_note(text)
        if note_body:
            result = save_note(user["email"], note_body, source="LoreMaster")
            await update.message.reply_text(f"📝 {result}")
            return

    # Verified user — lore query
    if user:
        status_msg = await update.message.reply_text("🔍 Prozkoumávám svět...")

        async def _lm_progress(status_text: str):
            try:
                await status_msg.edit_text(status_text)
            except Exception:
                pass

        try:
            user_key = f"telegram:{update.effective_user.id}"
            answer = await loremaster.query(user_key, text, user, send_status=_lm_progress)
            await log_question(user["email"], "LoreMaster", text, answer)
        except Exception as e:
            logger.error("LoreMaster query failed: %s", e, exc_info=True)
            answer = "Omlouvám se, něco se pokazilo při hledání odpovědi. Zkus to prosím znovu."
        try:
            await status_msg.delete()
        except Exception:
            pass
        for chunk in _split_message(answer):
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(
            "Nejsi ověřen/a. Pošli mi svůj email pro ověření, nebo napiš /start."
        )


# ============================================================
# BOT STARTUP
# ============================================================


async def start_telegram_bots(config, user_store, rulemaster, loremaster):
    """Start both Telegram bots concurrently. Blocking — runs until interrupted."""

    # Init shared user store and question log
    await user_store.init()
    await init_question_log()

    # --- Rulemaster bot ---
    rm_request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    rm_app = Application.builder().token(config.telegram.rulemaster_token).request(rm_request).build()
    rm_app.bot_data["config"] = config
    rm_app.bot_data["user_store"] = user_store
    rm_app.bot_data["rulemaster"] = rulemaster
    rm_app.bot_data["bot_name"] = "Rulemaster"
    rm_app.add_handler(CommandHandler("start", rm_start))
    rm_app.add_handler(CommandHandler("help", rm_help))
    rm_app.add_handler(CommandHandler("pravidlo", rm_pravidlo))
    rm_app.add_handler(CommandHandler("pravidla", rm_pravidla))
    rm_app.add_handler(CommandHandler("navrh", rm_navrh))
    rm_app.add_handler(CommandHandler("index", rm_index))
    rm_app.add_handler(CommandHandler("napoveda", rm_napoveda))
    rm_app.add_handler(CommandHandler("pruvodce", rm_pruvodce))
    rm_app.add_handler(CommandHandler("reset", rm_reset))
    rm_app.add_handler(CommandHandler("kdo", rm_kdo))
    rm_app.add_handler(CommandHandler("poznamka", cmd_poznamka))
    rm_app.add_handler(CommandHandler("poznamky", cmd_poznamky))
    rm_app.add_handler(CommandHandler("dotazy", cmd_dotazy))
    rm_app.add_handler(CommandHandler("ukol", cmd_ukol))
    rm_app.add_handler(CommandHandler("hotfix", cmd_hotfix))
    rm_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rm_message))

    # --- LoreMaster bot ---
    lm_request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    lm_app = Application.builder().token(config.telegram.loremaster_token).request(lm_request).build()
    lm_app.bot_data["config"] = config
    lm_app.bot_data["user_store"] = user_store
    lm_app.bot_data["loremaster"] = loremaster
    lm_app.bot_data["bot_name"] = "LoreMaster"
    lm_app.add_handler(CommandHandler("start", lm_start))
    lm_app.add_handler(CommandHandler("help", lm_help))
    lm_app.add_handler(CommandHandler("lore", lm_lore))
    lm_app.add_handler(CommandHandler("stav", lm_stav))
    lm_app.add_handler(CommandHandler("postava", lm_postava))
    lm_app.add_handler(CommandHandler("reset", lm_reset))
    lm_app.add_handler(CommandHandler("poznamka", cmd_poznamka))
    lm_app.add_handler(CommandHandler("poznamky", cmd_poznamky))
    lm_app.add_handler(CommandHandler("dotazy", cmd_dotazy))
    lm_app.add_handler(CommandHandler("ukol", cmd_ukol))
    lm_app.add_handler(CommandHandler("hotfix", cmd_hotfix))
    lm_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lm_message))

    # Run both bots concurrently. Webhook mode is enabled when a base URL is
    # configured; that's the only multi-replica-safe path. The legacy polling
    # path stays for local dev / single-replica fallback.
    webhook_base = (config.telegram.webhook_base_url or "").rstrip("/")
    use_webhooks = bool(webhook_base)

    async with rm_app:
        async with lm_app:
            await rm_app.start()
            await lm_app.start()
            logger.info("Both Telegram bots started (Rulemaster + LoreMaster)")

            if use_webhooks:
                rm_url = f"{webhook_base}/webhook/telegram/rulemaster"
                lm_url = f"{webhook_base}/webhook/telegram/loremaster"
                rm_secret = config.telegram.rulemaster_webhook_secret or None
                lm_secret = config.telegram.loremaster_webhook_secret or None
                # drop_pending_updates clears any polling backlog from a prior run.
                await rm_app.bot.set_webhook(
                    url=rm_url, secret_token=rm_secret,
                    allowed_updates=Update.ALL_TYPES, drop_pending_updates=True,
                )
                await lm_app.bot.set_webhook(
                    url=lm_url, secret_token=lm_secret,
                    allowed_updates=Update.ALL_TYPES, drop_pending_updates=True,
                )
                logger.info("Telegram webhooks registered: rm=%s lm=%s", rm_url, lm_url)
                # Expose handles so the Flask webhook routes (running on a
                # different thread) can dispatch updates onto this loop.
                set_webhook_runtime(
                    loop=asyncio.get_running_loop(),
                    rulemaster_app=rm_app,
                    loremaster_app=lm_app,
                    rulemaster_secret=rm_secret,
                    loremaster_secret=lm_secret,
                )
            else:
                await rm_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
                await lm_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
                logger.info("Telegram running in long-polling mode (no webhook URL configured)")

            # Block until interrupted
            stop_event = asyncio.Event()
            try:
                await stop_event.wait()
            except (KeyboardInterrupt, SystemExit):
                pass
            finally:
                if use_webhooks:
                    set_webhook_runtime(
                        loop=None, rulemaster_app=None, loremaster_app=None,
                        rulemaster_secret=None, loremaster_secret=None,
                    )
                    try:
                        await rm_app.bot.delete_webhook()
                        await lm_app.bot.delete_webhook()
                    except Exception:
                        pass
                else:
                    await rm_app.updater.stop()
                    await lm_app.updater.stop()
                await rm_app.stop()
                await lm_app.stop()
