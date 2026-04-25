# Ovčina Bot

WhatsApp + Telegram bot for the Ovčina LARP — answers rule, lore, and logistics
questions for players and organizers. Runs on Azure Container Apps, talks to a
cloud WAHA instance for WhatsApp.

## Architecture

```
WhatsApp → cloud WAHA (Container App) → webhook → ovcina-bot (Container App)
Telegram (long-poll)                  ↗
```

- **Code:** `bot.py`, `config.py`, `channels/`, `core/`
- **Content (baked into image):** `content/{pravidla,.skills,brain,knowledge-base,games}`
- **Persistent state:** `data/users.db` (SQLite) — mounted as Azure File Share

## Local dev

1. `cp .env.example .env` and fill in the secrets
2. `py -3.14 -m venv .venv && .venv/Scripts/pip install -r requirements.txt`
3. `.venv/Scripts/python bot.py`

The local config currently reads from OneDrive paths. For a fully cloud-style
local run, point `content/` at the local repo copy.

## Deploy

Push to `main` → GitHub Actions builds image → pushes to GHCR → updates the
Container App. ~30 s rollout.

Required GitHub secrets:
- `AZURE_CREDENTIALS` — Service principal JSON for `az login`

Container App env vars (set as Container App secrets, not committed):
- `TELEGRAM_RULEMASTER_TOKEN`, `TELEGRAM_LOREMASTER_TOKEN`
- `ANTHROPIC_API_KEY`
- `WAHA_URL`, `WAHA_API_KEY`
- `REGISTRACE_API_KEY`, `REGISTRACE_INTEGRATION_KEY`
- `AZURE_COMMUNICATION_CONNECTION_STRING`
- `HRA_API_TOKEN`
- `BACA_API_KEY`
