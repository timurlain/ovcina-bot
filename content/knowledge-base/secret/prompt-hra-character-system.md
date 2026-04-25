# OvčinaHra: Character System Implementation

## Context

Use /hra-ovcina-tinkerer skill for implementation.

We are adding a **character management system** to OvčinaHra (hra.ovcina.cz). Characters are a core part of the world — they walk through locations, fight monsters, do quests. Some characters are played by real children at LARP events, others exist only in lore.

**Deadline: 2026-05-01** (game day)

**Design doc:** `C:\Users\TomášPajonk\source\repos\timurlain\registrace-ovcina-cz\docs\plans\2026-04-12-qr-glejt-character-system-design.md`

## What exists already (registrace side — done)

- **QR sticker print page** at registrace.ovcina.cz — generates QR codes encoding `hra.ovcina.cz/p/{personId}`
- **Character seed API** at `GET /api/v1/games/{gameId}/characters` — returns character data (personId, name, race, class, kingdom, level, continuity status) protected by API key
- **OIDC auth** — hra already authenticates organizers via registrace

## What to build in OvčinaHra

### 1. Data Model (EF Core entities + migrations)

**Character** — persistent world entity:
```
Id (int, PK)
Name (string, required)
Race (string?, nullable)
Kingdom (string?, nullable)
BirthYear (int?, nullable — in-game lore year, not real year)
Notes (string?, nullable)
IsPlayedCharacter (bool — true = played by a real person, false = lore NPC)
ExternalPersonId (int?, nullable — registrace Person.Id, for played characters)
ParentCharacterId (int?, nullable — FK to Character, in-game family tree)
IsDeleted (bool)
CreatedAtUtc (DateTime)
UpdatedAtUtc (DateTime)
```

**CharacterAssignment** — links character to a game, played by a person:
```
Id (int, PK)
CharacterId (int, FK → Character)
GameId (int — references registrace Game.Id, NOT a local FK)
ExternalPersonId (int — registrace Person.Id)
IsActive (bool — false if character died mid-game)
StartedAtUtc (DateTime)
EndedAtUtc (DateTime?, nullable — set when character dies)
```

**CharacterEvent** — timestamped event log:
```
Id (int, PK)
CharacterAssignmentId (int, FK → CharacterAssignment)
Timestamp (DateTime)
OrganizerUserId (string — the organizer who logged this)
OrganizerName (string — display name, denormalized for history)
EventType (string — "LevelUp", "SkillGained", "PointsChanged", "Note", "ClassChosen")
Data (string — JSON payload, content depends on EventType)
Location (string?, nullable — freeform, which town/station)
```

**Indexes:**
- Character: unique index on ExternalPersonId (where not null)
- CharacterAssignment: index on GameId, index on ExternalPersonId, index on CharacterId
- CharacterEvent: index on CharacterAssignmentId

### 2. Character CRUD Pages

**Character list page** — table with: Name, Race, Kingdom, IsPlayed badge, actions
- Search/filter by name
- "Vytvořit postavu" (Create character) button
- Link to character detail

**Character detail/edit page** — form with all fields:
- Name, Race, Kingdom, BirthYear, Notes
- IsPlayedCharacter toggle
- ExternalPersonId (shown as "Hráč z registrace" — display only if linked)
- Parent character link (dropdown/search of other characters)
- Game appearances list (which games this character played in)
- Event log for the current/selected game

### 3. Import from Registrace

An admin action (button on character list page or a separate page) that:
1. Calls `GET https://registrace.ovcina.cz/api/v1/games/{gameId}/characters` with the API key
2. For each character seed:
   - If a Character with matching ExternalPersonId already exists → update name/race/class if changed
   - If not → create new Character (IsPlayedCharacter = true) + CharacterAssignment for this game
3. Shows a summary: "Importováno X nových, aktualizováno Y existujících"

**API key**: store in app configuration (`IntegrationApi:ApiKey` or similar). The registrace API key is: `ab5380ce6b84a05b1085cd2550c162b0a38a15c645a0e092c00069b5976237d0`

**Game ID for import**: The current game in registrace is ID=1 (30. Ovčina Balinova pozvánka). Hardcode for now or make it a config value — we only run one game at a time.

### 4. Scan Page (`/p/{personId}`)

**This is the QR code target.** When an organizer scans a player's glejt badge:

Route: `/p/{personId:int}`
Auth: required (organizer must be logged in via OIDC)

**Flow:**
1. Receive personId from URL
2. Find active CharacterAssignment where ExternalPersonId = personId and IsActive = true (for current game)
3. Load the Character + recent CharacterEvents
4. Display character profile with quick actions

**What the organizer sees:**
- Character name, kingdom, race (header)
- Current level (count of LevelUp events)
- Current points (sum of PointsChanged events, by category)
- Recent events (last 10, with timestamp + organizer + type)

**Class progression mechanic:**
- Characters start at **level 0 with no class** — they are rookies ("Začátečník")
- XP is earned through PointsChanged events (category "XP" or tracked via LevelUp count)
- After accumulating **5 XP**, the player chooses a class
- Until class is chosen: show "Začátečník" where class would normally appear
- When XP >= 5 and class is null: show a prominent **"Zvolte povolání"** (Choose class) prompt with a class picker
- Choosing a class creates a `ClassChosen` event and sets the class on the Character entity
- **Exactly 4 classes:** Warrior (Válečník), Archer (Lučištník), Thief (Zloděj), Mage (Mág)
- Show as 4 big buttons on the class picker — no freeform text, no dropdown
- After class is set, character continues leveling normally

**Quick action buttons (big, mobile-friendly — this is used on phones in the field):**
- **"Level up"** — one tap, creates a LevelUp event. Show new level number.
- **"Přidat body"** (Add points) — pick category (Dobré/Špatné/Neutrální) + enter amount + optional note → creates PointsChanged event
- **"Přidat poznámku"** (Add note) — freeform text → creates Note event
- **"Přidat dovednost"** (Add skill) — type skill name → creates SkillGained event
- **"Zvolte povolání"** (Choose class) — only shown when XP >= 5 and class is null. Class picker (freeform text or dropdown if class list is defined). Creates ClassChosen event.

**Each event records:** timestamp (auto), organizer (from auth claims), location (optional text field shown on quick actions).

**If person not found or no active assignment:** Show "Postava nenalezena. Tento hráč nemá aktivní postavu v aktuální hře."

**Mobile UX priority:** This page MUST work well on phone screens. Large buttons, minimal scrolling to reach actions, clear typography.

### 5. No offline-first complexity

Signal is mostly available at the game location, with occasional dead spots. Do NOT build offline-first PWA sync. If a write fails, show an error and let the organizer retry. The Blazor WASM app already caches its own assets client-side.

## API Endpoints needed (backend)

Follow the existing minimal API pattern with MapGroup in OvčinaHra:

```
GET    /api/characters                     — list all (with search query param)
GET    /api/characters/{id}                — detail
POST   /api/characters                     — create
PUT    /api/characters/{id}                — update
DELETE /api/characters/{id}                — soft delete

GET    /api/characters/{id}/assignments    — game appearances
POST   /api/characters/import/{gameId}     — import from registrace

GET    /api/scan/{personId}                — resolve person → active character + current state
POST   /api/scan/{personId}/events         — log a new event (LevelUp, PointsChanged, etc.)
GET    /api/scan/{personId}/events         — recent events
```

## Build order (for May 1 deadline)

1. **Entities + migrations** — Character, CharacterAssignment, CharacterEvent
2. **Character CRUD API + pages** — basic list + edit
3. **Import from registrace** — call seed API, create characters
4. **Scan page + event log** — the QR target, quick actions
5. **Polish** — test with real data, fix mobile UX issues

## Key constraints

- Do NOT change the registrace app — it's done
- Do NOT build player-facing profiles — organizer-only
- Do NOT build offline sync — retry on failure is enough
- Do NOT build skill catalogs or progression rules — just log freeform events
- Family tree UI (ParentCharacterId) can be basic — a dropdown on the edit form
- Version should bump with each PR merge (check current version in .csproj)
- NEVER push to main directly — always PR
