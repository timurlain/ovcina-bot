# Game 30 — Treasure Allocation Plan (DRAFT v4)

**Status:** awaiting Tomáš sign-off · 2026-05-01
**Total treasures:** **443** = 112 fillers + 331 pool item units (each unit individual)
**Stashes covered:** 192 / 192 — 0 empty, mean 2.31 per stash
**Files in this directory:**
- `treasure-allocation-plan.json` — 443 records (full POST payloads)
- `treasure-allocation-plan.csv` — same data, semicolon-delimited

---

## Locked rules (per Tomáš)

1. Pool items go **individually** — each unit is its own `AssignTreasure` quest.
2. Platinová mince → substitute **5× Zlatá mince** in payload.
3. Voda hvězd ×4 + Menhir ×1 → POST to pool first, then assign as `PoolItems`.
4. Worth scales with **RegRem** (region remoteness): 0 = Střed; 1 = medium hvozd / hory / pláně; 2 = deep wilderness.
5. **Runes (Tier A) spread Start + Early + Midgame, none in Lategame.**
6. **Potions (Tier G) back-weighted to late game** ← v4 change. Game-changer single-shots saved for big fights.
7. +2/+2 Náhrdelník (Tier B) → Lategame.
8. **Mid/Late phases keep wilderness only** ← v4 change. All 35 Střed (RR0) stashes live in Start+Early phases.
9. All 192 stashes filled.

---

## Coin & resource API mapping

| Filler denom | g | API itemId | itemName |
|---|---|---|---|
| měďák | 1 | 376 | Groš |
| stříbrňák | 5 | 377 | Stříbrná mince |
| zlaťák | 25 | 378 | Zlatá mince |
| platinová | 125 | 378 ×5 | Zlatá mince (substituted) |

| Surovina | API itemId | Channel |
|---|---|---|
| Byliny / Dřevo / Jídlo / Kámen / Kožešiny / Mana / Víno | 452 / 374 / 399 / 375 / 433 / 382 / 373 | UnlimitedItems |
| **Voda hvězd** | 402 | **PoolItems** (+4 to pool first) |
| **Menhir** | 426 | **PoolItems** (+1 to pool first) |

---

## v4 Phase × RegRem stash distribution

| Phase | RegRem 0 (Střed) | RegRem 1 (medium) | RegRem 2 (hard) | total |
|---|---:|---:|---:|---:|
| **Start** | 18 | 18 | 12 | **48** |
| **Early** | 17 | 18 | 13 | **48** |
| **Midgame** | 0 | 30 | 18 | **48** |
| **Lategame** | 0 | 23 | 25 | **48** |
| **TOTAL** | **35** | **89** | **68** | **192** |

Stashes shuffled with seed `20260501` for determinism. **Mid/Late RR0 = 0:** Střed is for early-game civilization action; wilderness phases stay wild.

---

## v4 matrix — per (Phase × RegRem) treasure breakdown

`fill` = filler bundles; `A`–`G`+`S` = pool item units of that worth tier.

| Phase | RegRem | stashes | fill | A | B | C | D | E | F | G | S | TOTAL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Start    | 0 | 18 | 18 | — | — | — | — | 18 | 18 | — | — | 54 |
| Start    | 1 | 18 | 7 | — | — | — | — | 22 | 7 | 1 | — | 37 |
| Start    | 2 | 12 | — | **10** | — | — | — | — | — | 2 | — | 12 |
| Early    | 0 | 17 | 17 | — | — | — | — | — | 17 | — | — | 34 |
| Early    | 1 | 18 | 8 | — | — | 26 | 18 | — | — | 2 | — | 54 |
| Early    | 2 | 13 | — | **18** | — | 5 | 13 | — | — | 3 | — | 39 |
| Midgame  | 0 | — | — | — | — | — | — | — | — | — | — | — |
| Midgame  | 1 | 30 | 25 | — | — | 32 | 9 | — | — | 3 | — | 69 |
| Midgame  | 2 | 18 | — | **25** | — | 6 | — | — | — | 5 | — | 36 |
| Lategame | 0 | — | — | — | — | — | — | — | — | — | — | — |
| Lategame | 1 | 23 | 12 | — | 15 | 11 | — | — | — | 8 | — | 46 |
| Lategame | 2 | 25 | 25 | — | 25 | — | — | — | — | 11 | **1** | 62 |
| **TOTAL** |  | **192** | **112** | **53** | **40** | **80** | **40** | **40** | **42** | **35** | **1** | **443** |

**Anchors honored (v4):**
- ✅ All **53 runes** in Start RR2 (10) + Early RR2 (18) + Midgame RR2 (25). Zero in Lategame.
- ✅ All **40 +2/+2 Náhrdelník** in Lategame (15 RR1 + 25 RR2)
- ✅ **Potions (35) back-weighted:** Start 3 / Early 5 / Midgame 8 / Lategame 19
- ✅ Unique **Kamenný klíč** in Lategame × RR2
- ✅ All 12 Super-large fillers in Lategame × RR2
- ✅ Worth scales with RegRem — RR2 only sees A/B/S/Super; RR0 holds E/F/Tiny/Small only

---

## Potions (Tier G) by phase — for review

| Phase | Count | Notes |
|---|---:|---|
| Start | 3 | mostly RR2 — small early peppering for adventurous heroes |
| Early | 5 | RR1 + RR2 mix |
| Midgame | 8 | RR1 + RR2, building toward big fights |
| Lategame | **19** | bulk in RR1 (8) + RR2 (11) — saved for endgame combat |

---

## Per-tier filler placement

| Filler tier | Count | Phase | RR0 | RR1 | RR2 |
|---|---:|---|---:|---:|---:|
| Tiny | 25 | Start | 18 | 7 | 0 |
| Small | 25 | Early | 17 | 8 | 0 |
| Medium | 25 | Midgame | 0 | 25 | 0 |
| Big | 25 | Lategame | 0 | 12 | 13 |
| Super large | 12 | Lategame × RR2 | 0 | 0 | 12 |

---

## Pre-flight POST sequence

```http
POST /api/treasure-planning/pool   { "gameId": 30, "itemId": 402, "count": 4 }   # Voda hvězd
POST /api/treasure-planning/pool   { "gameId": 30, "itemId": 426, "count": 1 }   # Menhir
```

Then `POST /api/treasure-planning/assign` ×443 in deterministic order.

---

## Ready to push?

v4 changes vs v3:
- ✅ Potions back-weighted to late game (Start 3, Early 5, Mid 8, Late 19) — was Start 14, Mid 12, Late 9
- ✅ Mid/Late phases drop all RR0 stashes (cleaner wilderness in late game)
- ✅ Tier F (utility) stays Start+Early as production booster

Reply **"go"** and I run the push.
