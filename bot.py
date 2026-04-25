"""Ovčina Bot — unified entry point for Telegram + WhatsApp channels."""

from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path

from config import load_config
from core.auth import UserStore
from core.rulemaster import Rulemaster
from core.loremaster import LoreMaster
from core.logistics import RegistraceClient, HraScheduleClient, BacaTasksClient
from channels.telegram import start_telegram_bots
from channels.whatsapp import WhatsAppChannel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Start all channels."""
    config = load_config()
    logger.info("Configuration loaded")

    # Shared state
    user_store = UserStore(Path(__file__).parent / "data" / "users.db")

    # Logistics clients — shared by both engines
    registrace_client = RegistraceClient(
        api_url=config.registrace.api_url,
        integration_api_key=config.registrace.integration_api_key,
        game_id=int(config.registrace.game_id),
    )
    hra_schedule_client = HraScheduleClient(
        api_url=config.hra.api_url,
        token=config.hra.api_token,
        game_id=config.hra.game_id,
    )
    baca_client = BacaTasksClient(
        api_url=config.baca.api_url,
        api_key=config.baca.api_key,
    )
    logger.info("Logistics clients initialized (registrace game %s, hra game %d)",
                config.registrace.game_id, config.hra.game_id)

    rulemaster = Rulemaster(
        api_key=config.anthropic.api_key,
        model=config.anthropic.model,
        pravidla_path=config.pravidla_path,
        skills_path=config.skills_path,
        hra_api_url=config.hra.api_url,
        hra_api_token=config.hra.api_token,
        hra_game_id=config.hra.game_id,
        registrace_client=registrace_client,
        hra_schedule_client=hra_schedule_client,
        baca_client=baca_client,
        max_history=config.conversation.max_history,
    )
    rulemaster.set_rule_editors(config.rule_editors)
    logger.info("Rulemaster engine initialized (pravidla: %s, skills: %s, editors: %s)",
                config.pravidla_path, config.skills_path, config.rule_editors)

    loremaster = LoreMaster(
        api_key=config.anthropic.api_key,
        model=config.anthropic.model,
        brain_path=config.loremaster.brain_path,
        kb_public_path=config.loremaster.kb_public_path,
        game_path=config.loremaster.game_path,
        skills_path=config.skills_path,
        hra_api_url=config.hra.api_url,
        hra_api_token=config.hra.api_token,
        hra_game_id=config.hra.game_id,
        registrace_client=registrace_client,
        hra_schedule_client=hra_schedule_client,
        baca_client=baca_client,
        max_history=config.conversation.max_history,
    )
    logger.info("LoreMaster engine initialized (brain: %s, skills: %s)", config.loremaster.brain_path, config.skills_path)

    # Start WhatsApp webhook in a background thread
    whatsapp = WhatsAppChannel(config, user_store, rulemaster, loremaster)
    wa_thread = threading.Thread(
        target=_run_whatsapp,
        args=(whatsapp,),
        daemon=True,
        name="whatsapp-webhook",
    )
    wa_thread.start()
    logger.info("WhatsApp webhook started on port 8080")

    # Start Telegram bots (blocking — runs the event loop)
    logger.info("Starting Telegram bots...")
    asyncio.run(start_telegram_bots(config, user_store, rulemaster, loremaster))


def _run_whatsapp(whatsapp: WhatsAppChannel):
    """Run WhatsApp Flask app in a thread."""
    whatsapp.app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
