---
name: ovcina-bot-tinkerer
description: >
  Project-specific implementation skill for the Ovčina Bot — a Telegram + WhatsApp
  bot (Rulemaster + LoreMaster) with tool_use agent loop, rule editing, and logistics
  integration. Use when working on `ovcina-bot/`, adding tools, updating prompts,
  integrating new APIs, debugging tool calls, editing the bot's search or agent
  loop, wiring WAHA (WhatsApp), or when the user mentions "ovcina bot", "rulemaster
  bot", "loremaster bot", "bot pravidel", "bot whatsapp", or talks about adding
  features to the Ovčina bot. Do NOT use for content/lore creation (that's
  ovcina-loremaster) or pure rules editing via CLI (that's rulemaster-ovcina).
---

# Ovčina Bot Tinkerer

## Project

**Location:** `C:\Users\TomášPajonk\OneDrive - SolverTech s.r.o\Bridge\Ovčina\ovcina-bot\`
**Python:** 3.13 (via `py -3.13`), virtualenv in `.venv/Scripts/python`
**Model:** `claude-opus-4-6` (in `config.yaml`)
**Main entry:** `bot.py`
**Channels:** Telegram (two separate bots) + WhatsApp (via WAHA Docker on `localhost:3000`)

### Start / restart
```bash
# Kill existing
wmic process where "name='python.exe' and commandline like '%bot.py%'" call terminate

# Start WAHA (if not running)
cd "<bot-dir>" && docker compose up -d

# Start bot in background
cd "<bot-dir>" && .venv/Scripts/python bot.py
```

Always run syntax check before restarting:
```bash
cd "<bot-dir>" && py -3.13 -c "import ast; [ast.parse(open(f, encoding='utf-8').read()) for f in ['bot.py', 'config.py', 'core/tools.py', 'core/logistics.py', 'core/rulemaster.py', 'core/loremaster.py']]"
```

## Architecture

Two Claude engines + WhatsApp webhook, all sharing logistics clients:

```
bot.py
 ├── Rulemaster (rules + items + write tools if editor)
 ├── LoreMaster  (lore + items + locations)
 ├── WhatsAppChannel (Flask webhook → WAHA API)
 └── Shared state:
     - UserStore (SQLite, email auth)
     - RegistraceClient (logistics — game info, user info, lodging)
     - HraScheduleClient (GameEvents + NPC schedules)
     - BacaTasksClient (user tasks)
```

Both engines use the same tool_use agent loop from `core/tools.py`. They each have their own system prompt loaded from `.skills/ovcina-{rulemaster,loremaster}/BOT_PROMPT*.md` (single source of truth). Both engines get the full logistics tool set.

### Agent loop pattern (`core/tools.py`)

Every query runs this loop:
1. Call `client.messages.create()` with tools
2. If `stop_reason == "end_turn"` → return text
3. Else execute each `tool_use` block via the engine's handler dict
4. Append tool results, repeat (max 8 rounds)
5. On exhaustion: one final tool-less call to force an answer

Tool handlers are **closures** created per-query by `engine._make_tool_handlers(user_role, user_email)` — they capture `self`, `user_role`, and `user_email` so tools auto-fill "the current user."

**Progress reporting:** `on_progress` callback fires before each tool call with a human-friendly message. Telegram handler edits a single status message in place; WhatsApp sends one upfront.

## Key files

| File | What |
|------|------|
| `bot.py` | Entry point — loads config, creates clients, wires engines to channels |
| `config.py` | dataclasses + `load_config()` reading `config.yaml` |
| `config.yaml` | all secrets and paths (NOT in git, has hardcoded tokens for now) |
| `core/tools.py` | Tool definitions + `run_agent_loop()` + shared handlers + `_TOOL_STATUS` map for progress |
| `core/logistics.py` | `RegistraceClient`, `HraScheduleClient`, `BacaTasksClient` + formatters |
| `core/rulemaster.py` | Rulemaster engine, theme search, write tools (editors only), `query()` |
| `core/loremaster.py` | LoreMaster engine, lore search with role-based access, `query()` |
| `core/hra_search.py` | Low-level hra.ovcina.cz search (used by `search_hra_api` tool) |
| `core/auth.py` | Email verification, user store, check_registration |
| `core/baca.py` | Create tasks in Bača (legacy, now superseded by BacaTasksClient) |
| `channels/telegram.py` | Two Telegram bots (rm_* + lm_* handlers), status msg pattern |
| `channels/whatsapp.py` | Flask webhook, `_handle_verified()` dispatches to engines |
| `.skills/ovcina-rulemaster/BOT_PROMPT.md` | Rulemaster system prompt (loaded at init) |
| `.skills/ovcina-loremaster/BOT_PROMPT_PLAYER.md` | In-character player prompt |
| `.skills/ovcina-loremaster/BOT_PROMPT_GM.md` | Organizer mode prompt |

**Do NOT** put system prompts in Python code — they belong in `.skills/`. The engines load them at init and the format strings expect `{user_role}` / `{postava}` / `{lore_context}` etc.

## Configuration cheat sheet

`config.yaml` key sections:
- `telegram.rulemaster_token`, `telegram.loremaster_token` — from env
- `waha.url`, `waha.api_key` — WAHA API key regenerates on container recreate
- `anthropic.model: "claude-opus-4-6"`
- `skills_path` — `.skills/` root (prompts live here)
- `pravidla.path` — rules directory
- `pravidla.editors: [email, ...]` — rule editors (5 currently)
- `registrace.api_url`, `registrace.api_key` (OIDC), `registrace.integration_api_key` (**new**, for bot integration API), `registrace.game_id: "1"`
- `hra.api_url`, `hra.api_token` (JWT service token, 30-day), `hra.game_id: 30`
- `baca.api_url`, `baca.api_key`
- `auth.organizer_emails: [...]`

**Registrace vs Hra game_id**: different systems. Registrace uses game 1, Hra uses game 30. Both refer to the same event.

## Integration patterns

### Registrace (base: `/api/v1`, auth: `X-Api-Key`)
- `GET /games/{id}/info` → GameInfoDto (name, dates, registration stats, `organizationInfo` free-form JSON)
- `GET /users/{email}/game-info?gameId=Y` → attendees[], lodging, payment, gameRoles
- `GET /users/{email}/lodging?gameId=Y` → just the lodging slice (may be null)
- `GET /users/{email}/person-id` → `{personId: 47}` or 404 — **critical for hra integration**
- `GET /users/by-email?email=X` → identity check (also includes personId in v0.9.3)

`RegistraceClient` caches email→personId in-memory per session.

### Hra (base: `/api`, auth: `Bearer <JWT>`)
- `GET /api/users/{personId:int}/schedule?gameId={id}` → UserScheduleDto with events, NPC played, timeSlots
- `GET /api/games/{id}/events` / `events/current` / `events/next?count=N` → GameEvent list
- `GET /api/items/{id}/can-use?playerClass=X&level=N` → ItemUsabilityDto
- `GET /api/items/usable?playerClass=X&level=N&gameId=Y` → list
- **PlayerClass enum is English-only**: `Warrior, Archer, Thief, Mage` (case-insensitive). Claude must translate: Válečník→Warrior, Lovec/Lučištník→Archer, Zloděj→Thief, Mág→Mage
- **NpcRole enum**: `Fate, Merchant, King, Monster, Story, Other`
- **gameId fallback pattern**: search with gameId first, if empty retry without, flag "⚠️ not in current game." 20/180 items currently linked to game 30, growing manually.
- **All times UTC** — `_format_prague()` in `logistics.py` converts for display

### Bača (auth: `X-Api-Key`)
- `GET /api/tasks?assigneeEmail=X&status=Open` — works directly with email
- Deep link format: `https://baca.ovcina.cz/tasks/{id}`
- Empty list if email not found (not 404)
- Optional filters: `status, priority, category, overdue, all`

## Tool definitions

Every tool has a JSON schema in `core/tools.py` following Anthropic's `tools` API format. Grouped as:

- `RULEMASTER_TOOLS_BASE` = search_rules, get_rule_file, search_hra_api, get_item_detail, search_files
- `RULEMASTER_WRITE_TOOLS` = write_rule_file, create_decision (editor-only, added conditionally in `query()`)
- `LOREMASTER_TOOLS_BASE` = search_lore, search_hra_api, get_item_detail, get_location_detail, search_files
- `LOGISTICS_TOOLS` = get_event_info, get_my_registration, get_my_lodging, get_my_tasks, get_my_schedule, get_current_event, get_next_events
- Final sets: `RULEMASTER_TOOLS = RULEMASTER_TOOLS_BASE + LOGISTICS_TOOLS` (write tools added at query time)
- `LOREMASTER_TOOLS = LOREMASTER_TOOLS_BASE + LOGISTICS_TOOLS`

## How to add a new read-only tool

1. **Define** in `core/tools.py` (schema + description in Czech)
2. **Add to tool set** (e.g. `LOGISTICS_TOOLS`)
3. **Add status line** to `_TOOL_STATUS` dict for progress messages
4. **Implement handler** in both `rulemaster.py._make_tool_handlers()` and `loremaster.py._make_tool_handlers()` — they're closures over `self` and user context
5. **Update prompt** in `.skills/ovcina-{rulemaster,loremaster}/BOT_PROMPT*.md` — tell Claude when to use it
6. **Syntax check** and restart bot
7. **Test** in Telegram (Rulemaster is the testbench)

## How to add a write tool (editors only)

Follow the pattern of `write_rule_file` in `rulemaster.py`:
- Tool goes in `RULEMASTER_WRITE_TOOLS` (not the base set)
- Tool definition should clearly say "editor-only" in the description
- Handler is added inside the `if user_email and user_email.lower() in self._rule_editors:` block in `_make_tool_handlers`
- **ALWAYS log to changelog** via `log_changelog(self.pravidla_path, user_email, rule_id, change_summary)`
- Final tool set in `query()`: `tools = RULEMASTER_TOOLS + RULEMASTER_WRITE_TOOLS if is_editor else RULEMASTER_TOOLS`

## How prompts work

System prompts are **templates** loaded from `.skills/` at engine init. They have format-string placeholders:

- Rulemaster `BOT_PROMPT.md`: `{user_role}` (filled from user's registered role)
- LoreMaster `BOT_PROMPT_PLAYER.md`: `{postava}`, `{frakce}`, `{postava_popis}` (from character profile)
- LoreMaster `BOT_PROMPT_GM.md`: no placeholders

The engine does `self._prompt_template.format(user_role=role)` etc. If you add new placeholders, update both the prompt file AND the engine's `query()` method.

**Never add `{lore_context}` or `{rules_context}` placeholders** — those were from the pre-tool_use era. Context comes from tool calls now.

## Error handling and user experience

- **Every query is wrapped in try/except** in the Telegram/WhatsApp handlers. On error, user sees "Omlouvám se, něco se pokazilo..." — not silence
- **Immediate status message** ("🔍 Hledám...") before work starts, edited live with tool progress, deleted when real answer arrives
- **Agent loop exhaustion** (>8 rounds) makes one final tool-less call to force a text answer from whatever context was gathered
- **Tool call errors** bubble up into tool results as `"Chyba při volání {name}: {e}"` — Claude can adapt and try something else

## Logging and debugging

Log file is the background task output file (temp dir). To inspect:
- Look for `core.tools - INFO - Tool call: <name>(<args>)` lines to trace what Claude decided to search
- Look for `Agent loop round N/8` to see how many rounds it took
- Look for `WARNING - Agent loop exhausted 8 rounds` to catch exhaustion cases
- HTTP 4xx/5xx from APIs come through as `logger.error("registrace ...")` etc.

## Known issues and gotchas

1. **Theme files stale** (`pravidla/_témata/*.md`) — contain outdated spell/item lists. SYNC-PROMPT.md exists in that directory to reconcile them. `magie.md` was the trigger but others may also be stale.

2. **gameId=30 filter returns empty for items** — items exist globally but most aren't linked. Bot's `search_hra_api` does the fallback automatically; don't "fix" it.

3. **WAHA API key regenerates on container recreate** — need to persist in `.env` or rebuild config each time.

4. **Dataclass field ordering** — `Config` has required fields first, defaulted fields last. Don't insert a defaulted field before a required one — TypeError at import time.

5. **UTC-everywhere → Prague display** — Hra API returns UTC. Registrace too. `_format_prague()` in `logistics.py` handles the conversion. Always use it for user-visible timestamps.

6. **PlayerClass must be English** — Czech class names (Válečník, Lovec, Zloděj, Mág) need translation before calling hra's item usability endpoints. The prompt tells Claude this but watch for it if building new tools.

7. **Telegram message editing fails if content is identical** — progress status updates catch the exception and `pass`.

8. **Loremaster engine takes `user: dict`, Rulemaster takes `user_role: str + user_email: str`** — different interfaces! Loremaster extracts email from `user.get("email")` inside `_make_tool_handlers`.

9. **Keep Rulemaster and LoreMaster separate for now** — user wants to merge into single "Bača" persona on WhatsApp later, but not yet.

10. **`.claude/skills/ovcina-loremaster/` still duplicated** in azra repo (Claude Code needs it for discovery) vs `Ovčina/.skills/ovcina-loremaster/SKILL.md` (canonical). The BOT_PROMPT files are single-source.

## Current state (2026-04-13)

**Working:**
- Tool-using agent loop with 8 rounds, progress reporting, error handling
- Rulemaster with rule editing for 5 editors (tomas.pajonk@hotmail.cz, tom@pajonk.cz, tomas.pajonk@solvertech.cz, deatch@email.cz, stanam@email.cz)
- Write tools with changelog logging to `pravidla/_changelog.md`
- Full logistics integration: registrace game/user info/lodging/person-id, hra schedule/events/items, bača tasks
- Email→personId resolver via registrace, cached per session
- UTC→Europe/Prague conversion for all timestamps
- Status messages with per-tool progress (📖 Prohledávám pravidla..., 🗄️ Hledám v databázi..., etc.)
- Both Telegram bots + WhatsApp webhook on port 8080
- Bot prompts externalized to `.skills/`, single source of truth
- Rule editor list in `config.yaml` → `pravidla.editors`

**Backends integrated:**
- Registrace v0.9.3 (`/api/v1/*` with `X-Api-Key`)
- Hra v0.4.1 (Bearer token, GameEvent system, item usability)
- Bača (X-Api-Key, `?assigneeEmail=X`)

**Pending / known work:**
- Unify Rulemaster + LoreMaster into one "Bača" persona on WhatsApp (user's long-term plan)
- Azure deploy for WhatsApp (currently local Docker)
- Proactive notifications (scheduler firing GameEvent start messages)
- Theme file sync (run SYNC-PROMPT.md)
- More items linked to game 30 (user is adding manually)
- WAHA API key persistence

## Common tasks — step by step

### Adding a new prompt instruction
1. Edit `.skills/ovcina-rulemaster/BOT_PROMPT.md` (or the loremaster one)
2. Restart bot (prompts are loaded at init, not per-query)
3. Test

### Debugging "the bot didn't find the right answer"
1. Look at `core.tools - INFO - Tool call:` lines to see what Claude searched
2. Check if the data source had it (direct API call via ctx_execute with curl)
3. Check `format_*` function output
4. Check if the prompt steers Claude to the right tool

### Adding a new backend integration
1. Write client class in `core/logistics.py` (async, `_get` pattern)
2. Add formatter function
3. Add tool definition in `core/tools.py`
4. Add to `LOGISTICS_TOOLS` (or make a new set if it's a different category)
5. Add handler closure in both engines' `_make_tool_handlers`
6. Add clients in `bot.py` main() and pass to engine constructors
7. Update config.yaml if new credentials needed
8. Update config.py dataclass (watch field ordering!)
9. Update prompts to tell Claude when to use the new tool
10. Syntax check, restart, test

### Syntax check
```bash
cd "<bot-dir>" && py -3.13 -c "import ast; [ast.parse(open(f, encoding='utf-8').read()) for f in ['bot.py', 'config.py', 'core/tools.py', 'core/logistics.py', 'core/rulemaster.py', 'core/loremaster.py', 'channels/telegram.py', 'channels/whatsapp.py']]; print('OK')"
```

## Test credentials and sample commands

```bash
# Hra service token
TOKEN=$(curl -s -X POST https://api.hra.ovcina.cz/api/auth/service-token \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"bot","secret":"OvcinaSkills2026!ServiceAccess"}' | jq -r .token)

# User schedule (personId 309 is a test user)
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.hra.ovcina.cz/api/users/309/schedule?gameId=30"

# Registrace integration API key
KEY="ab5380ce6b84a05b1085cd2550c162b0a38a15c645a0e092c00069b5976237d0"
curl -H "X-Api-Key: $KEY" https://registrace.ovcina.cz/api/v1/games/1/info
curl -H "X-Api-Key: $KEY" "https://registrace.ovcina.cz/api/v1/users/tomas.pajonk%40hotmail.cz/person-id"

# Bača tasks
BACA_KEY="kl3F0jpJwC2cKbHPsYzOw77fC9IDqH679S8O85BqorA"
curl -H "X-Api-Key: $BACA_KEY" \
  "https://baca.ovcina.cz/api/tasks?assigneeEmail=tomas.pajonk@hotmail.cz&status=Open"
```

## References to longer memory

Full project memory is in `C:\Users\TomášPajonk\.claude\projects\C--Users-Tom--Pajonk-source-repos-azra\memory\ovcina-bot-session-2026-04-11-12.md` — that file has the complete history of decisions, gotchas found during implementation, and the exact backend status reports from both teams. Read it if something in this skill contradicts reality or you need deeper context.

## Do NOT

- Do not put system prompts in Python source code — `.skills/` is the only source of truth
- Do not add `{rules_context}` or `{lore_context}` placeholders — those are pre-tool_use artifacts
- Do not pass `gameId` to all item searches — the fallback pattern is intentional
- Do not hardcode English class names for Czech users — translate only when calling hra API
- Do not merge Rulemaster + LoreMaster yet — user will say when
- Do not delete the duplicate loremaster `SKILL.md` in azra `.claude/skills/` — Claude Code needs it for discovery
- Do not skip the syntax check before restarting
- Do not commit to git unless user explicitly asks (user's standing rule)
