---
id: DOV-003
název: Mechanika odměn za dobrodružné dovednosti — provoz
úroveň: systémová
kategorie: [dovednosti, dobrodruzne, sifra, organizator, knihovna]
stav: schváleno
viditelnost: organizátor
závisí-na: [DOV-001, DOV-002, EKO-006, QUE-007]
nahrazuje: []
poslední-změna: 2026-04-29
klíčové-fráze:
  - jak provozovat dobrodružné dovednosti
  - knihovník registr hesel
  - otáčení šifrovací karty
  - claim dispute hesla
  - tier odměn cipher
---

# Mechanika odměn za dobrodružné dovednosti — provoz

## Pět typů odměn (organizátorský pohled)

Každá kombinace (lokace × dovednost) v matrici dává jeden z pěti typů reveals:

| Typ | Popis | Hustota | Šifra po vybrání |
|---|---|---|---|
| **Empty** | „Nic tu není" nebo atmosférická flavor věta | ~10 % cells | Stále čitelná |
| **Micro** | Krátký lore tidbit, +1–3 XP, 1 mana, 1–2 gr, hint | ~48 % cells | Stále čitelná |
| **Quest-tied** | Klíč, fragment mapy, jméno NPC, heslo do questu | ~12 % cells | Stále čitelná |
| **Standard voucher** | Heslo do knihovny → 5–15 gr nebo malý item | ~22 % cells | **Otočit po uplatnění hesla** |
| **Flagship paired** | Visible TreasureStash na lokaci + cipher heslo do knihovny pro premium odměnu (runa/artefakt/lektvar) | ~8 % cells | **Otočit po uplatnění hesla** |

Per dovednost (z ~65 cipher lokací): ~6 empty / ~31 micro / ~8 quest-tied / ~14 standard / **5 flagship**.

## Knihovník — registr hesel

Knihovník drží **registr aktivních hesel** ve formě tabulky:

| Heslo | Dovednost | Odměna | Vyzvednuto kým + kdy |
|---|---|---|---|
| BUKOVÝ KOŘEN | Znalost bytostí | 12 gr + lektvar Mírného uzdravení | (prázdné dokud nikdo nevyzvedl) |
| ... | ... | ... | ... |

Když hrdina pronese heslo:

1. Knihovník ověří, že heslo je v registru a ještě nebylo vyzvednuto.
2. Vydá příslušnou odměnu.
3. Zapíše do sloupce „Vyzvednuto" jméno hrdiny + čas.
4. **Sdělí hrdinovi (nebo nejbližšímu CP), že má jít na lokaci a otočit šifrovací kartu lícem dolů.**

Pokud heslo bylo již vyzvednuto: knihovník hrdinovi řekne, že „někdo byl rychlejší" a žádnou odměnu nedá.

## Otáčení šifrovací karty

Šifrovací karta na lokaci se otáčí lícem dolů (nebo se odstraní z držáku) ve dvou případech:

- Po uplatnění hesla typu **standard voucher** — viz workflow výše.
- Po vybrání obsahu **flagship paired** — viz workflow výše.

**Kdo otáčí:**

- Primárně **hrdina, který heslo uplatnil** — knihovník mu to uloží jako součást vyzvednutí.
- Sekundárně **organizátor, který je u lokace přítomný** — pokud hrdina nestihne dojít zpět.
- **CP víly nebo Mudrc procházející lokací** — mají v briefingu instrukci „pokud vidíš na lokaci s šifrou označenou jako single-use claim, ověř s knihovnou a otoč."

Otočená karta zůstává **lícem dolů na svém místě po zbytek hry** — slouží jako vizuální signál pro další hrdiny, že tahle dovednost už zde dohrála.

## Tiery permanentních reveals (nepromazávat)

Empty, micro a quest-tied cells **NIKDY se neotáčejí**. I po dekódování zůstávají na lokaci čitelné pro další hrdiny se stejnou dovedností. Lore a drobnosti jsou tím „průchozí value" — buyer dostává hodnotu i v hustě prozkoumaném terénu.

## Spory o claim

Pokud dva hrdinové dorazí ke knihovně s týmž heslem ve stejnou minutu:

- Zvítězí ten, kdo ho **vysloví dříve** (knihovník je arbitr).
- Pokud je remíza nejasná, knihovník hodí **1k6**: 1–3 první hrdina, 4–6 druhý.
- Druhý hrdina odchází bez odměny — neexistuje „split."

## Flagship paired — provoz

25 vybraných lokací má dvě vrstvy odměn:

- **Vrstva 1 (viditelná všem):** klasická TreasureStash kartička u lokace (skutečně viditelná, jak popisuje EKO-006).
- **Vrstva 2 (jen pro nositele dovednosti):** šifra na lokaci, která po dekódování dává heslo do knihovny pro **premium odměnu** (vyšší než standard voucher).

Vrstva 1 funguje normálně podle EKO-006 (kdo vidí, najde). Vrstva 2 se otáčí po uplatnění hesla tak, jak popisuje provoz výše.

**Loremaster vede seznam 25 flagship lokací** v `docs/prompty/loremaster-obsah-sifer.md` — který stash je párovaný s jakou dovedností.

## Cross-refs

- **DOV-001** — hráčský pohled na cipher rewards
- **DOV-002** — fyzická výroba cipher karet
- **EKO-006** — TreasureStashes (visible base layer pro flagship paired)
- **QUE-007** — quest rewards (quest-tied tier čerpá z quest pool)
