# Opportunity: Dynamic ceník changes via in-game events

**Status:** Idea / brain note, not designed
**Captured:** 2026-04-29 (during Block 3 ceník delivery)

## Idea

Trhová krabice ceník is currently locked per-game. Future games could expose **in-game events** that change buy/sell prices dynamically:

- "Drought in Lidé territory — víno doubles in price for 2 periods"
- "Trade caravan from Eastlands arrives — koření buyback drops to 4 gr"
- "Trpaslík guild strike — kámen unbuyable for 3 periods"
- "Festival in Aradhrynd — all zboží buys +50% there for 1 period"

## Why interesting

- Adds temporal dimension to trade strategy (timing matters, not just route)
- Creates organizer levers to nudge economy if it drifts (deflation? print event. inflation? remove buyback)
- Story integration — events tie to lore/narrative/season
- Late-game tension — final-period events can swing closing scores

## What's needed before this lands

- Event-driven price override mechanic in Trhová krabice (technical: API or organizer-facing tool)
- Designer guidelines: how big can swings be, how often, who decides
- Player communication channel — how do hrdinové learn about price shifts?
  - Bot announcement?
  - NPC criers?
  - Daily printed bulletin at obchodník?

## Status

Parked. Game 30 uses static ceník (per `Ovčina/balancing-handoff.md` Block 3 data).

Revisit for Game 31+ design pass.
