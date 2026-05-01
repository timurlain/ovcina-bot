# Treasure pool design — Game 30

**Datum:** 2026-05-01
**Skill:** economymaster-ovcina
**Active gameId:** 30 (Balinova pozvánka)

## Kontext

API stav v době návrhu:
- 87 lokací v Game 30, **74 s aspoň 1 stash slotem**, **192 stash slotů celkem**
- Žádné TreasureQuests dosud nepřiřazeny (pool prázdný)
- 331 thematic items už připraveno (artefakty, ingredience, special — mimo scope tohoto plánu)

Locked target z Block 1+2 (`balancing-handoff.md`):
- Hidden treasure stash share: **~6 350 g** (25 % z 25 400 g total demand)
- ROZ-010 intent: **přiškrtit** ekonomiku oproti loňsku

## Návrh — 112 filler treasures, 5 030 g

Doplňky k 331 thematic itemům. Pool sedí pod cap (5 030 < 6 350), zbývá ~1 320 g rezervy pro thematic-item value.

### Rozložení po tieru

| Tier | # | Ø g | Total g | Ø sur | Σ sur | Cap |
|---|---:|---:|---:|---:|---:|---:|
| Tiny | 25 | 9 | 233 | 2.1 | 53 | 5–15 g |
| Small | 25 | 23 | 570 | 2.1 | 53 | 15–30 g |
| Medium | 25 | 47 | 1 169 | 2.0 | 51 | 35–55 g |
| Big | 25 | 67 | 1 688 | 0.6 | 15 | 55–75 g |
| Super large | 12 | 114 | 1 370 | 0.6 | 7 | 100–125 g |
| **Σ** | **112** | — | **5 030** | — | **179** | — |

### Stage × Difficulty matice

4 stages (`start`, `early`, `mid`, `late`) × 3 difficulty (0 safe / 1 moderate / 2 remote).

| Stage | d=0 | d=1 | d=2 |
|---|---:|---:|---:|
| start | 25 | 0 | 0 |
| early | 18 | 7 | 0 |
| mid | 5 | 18 | 2 |
| late | 0 | 12 | 25 |

Diagonála: early = bezpečné lokace, late = Moria/Hluboko / dungeon-adjacent.

### Suroviny pool

Byliny 40 / Kožešiny 34 / Víno 28 / Kámen 24 / Jídlo 21 / Dřevo 21 / Mana 6 / Voda hvězd 4 / Menhir 1.

**Distribuce surovin po fázi hry:**
- Start+early+mid (75 treasures): **157 jednotek** = 86 %
- Late (37 treasures): **22 jednotek** = 12 %

Suroviny mají největší marginal value v early/mid (stavba budov, krmení manufaktur, cross-kingdom obchod). Late game = pure gold haul.

## Zásadní designová rozhodnutí

1. **Mana minimální (6 jednotek v 4 treasures)** — mana je vstupné na Treasure Vision (cost 1–2 RV). Když ji nasypeme do pokladů, financuje sebe (loop). Mana zůstává primárně na Cat III/IV monstrech, magických lokacích, Rybníku, ~10 questech (handoff: ~196 RV total supply, ~190 demand).

2. **Resources cluster early, gold cluster late** — v early game mají suroviny velkou utility hodnotu (budovy, manufaktury). V late game už království stojí, hráči potřebují zlato na zbraně/lektvary/dungeon prep. Diagonála: Tiny/Small/Medium nesou 86 % surovin a 39 % zlata; Big/Super large 12 % surovin a 61 % zlata.

3. **Region difficulty rule** — žádný start-stage v difficulty 2 (děti by se nedostaly), žádný late-stage v difficulty 0 (zlaťák by se válel u městské fontány — nedává smysl).

4. **Big cap = 75 g, Super large cap = 125 g** — ROZ-010 nechce loňské bohatství. Originally jsem měla Heavy 100–160 g a Top 200–350 g (9 107 g total) — cropnuto na 5 030 g.

5. **Voda hvězd 4 + Menhir 1 v Top tier** — pre-Citadela / pre-Výheň prep loot. Soft gating na high-tier kingdom buildings.

## Soubory

V této složce:
- `treasure-fillers-game30.json` — zdrojová data, plné DTO
- `treasure-fillers-game30.md` — human-readable
- `treasure-placement-list-game30.csv` — **handoff pro placement agenta** (sloupce: id, tier, gameStage, regionDifficulty, name, groseTotal, coinMix, resources)
- `treasure-placement-list-game30.json` — strukturovaná verze
- `treasure-placement-list-game30.md` — human-readable

## Otevřené pro placement agenta

1. Mapování `regionDifficulty` na `remotenessScore` z location DTO (0 → low, 2 → high)
2. Late-stage treasures **musí** být na lokacích s vysokou remoteness (~150 m+ od centra)
3. Limit max 1 filler treasure per stash slot — některé stashe poberou 2-3 (filler + thematic), jiné 1
4. Top tier kandidáti: Mazarbul Aznân spot, Balinova expedice anchor, Moria peripheral hluboké dungeony
5. Existující `treasure-allocation-plan.md` v této složce — sjednocení s placement listou je úkol pro placement agenta

## Pending — co teď chybí

- **Block 3 — Village production calibration** ← další session
- Block 4 stash content design (částečně pokryto tímto poolem, ale per-stash assignment chybí)
- Block 5 — Rosa Valar economy lock-in
- Block 6 — Validation simulations
