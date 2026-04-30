---
typ: návrh-publikace
cílový-soubor: pravidla-pro-hrdiny-2026.md
audience: Rulemasters / organizátoři (k revizi)
datum: 2026-04-30
stav: čeká na schválení
---

# Návrh změn publikace pro Hrdiny — 2026

Účel: přepsat `pravidla-pro-hrdiny-2026.md` proti aktuálnímu stavu pravidlové databáze.
Rozsah: pravidla s `viditelnost: hráč` nebo `obojí`, stav `schváleno`.
Po schválení této listiny → regenerace publikace.

---

## 1. Současný stav publikace (co tam je)

| Sekce | Pokrývá pravidla |
|------|------------------|
| Vítej, Hrdino! (intro) | AXI-001, AXI-002 (částečně) |
| Soubojový systém | ZAK-001 |
| Útok a obrana | ZAK-002 |
| Válečník | ZAK-003 |
| Střelec | ZAK-004 |
| Zloděj | ZAK-005 (bez tajné zlodějiny ZLO-001 — správně) |
| Mág + magie inline | ZAK-006 + MAG-001, MAG-002, MAG-003, MAG-004 (částečně), MAG-008, MAG-009, MAG-010 |
| Test pro Hrdiny (kvíz) | — |

**Verze v souboru:** v1.1, ročník 2026.

---

## 2. Pokrytí proti databázi — gap analýza

Schválená pravidla s viditelností `hráč` / `obojí`, která **chybí** v současné publikaci:

### 2.1 Axiomy (obojí)

| ID | Název | Status v publikaci | Návrh |
|----|-------|-------------------|------|
| AXI-001 | Bezpečnost dětí | částečně (intro) | rozšířit do samostatné sekce |
| AXI-002 | Bezkontaktní souboj | v intru | nechat v intru |
| AXI-003 | Zábava pro všechny věkové skupiny | **chybí** | krátká zmínka |
| AXI-004 | Volný svět | **chybí** | krátká zmínka |
| AXI-005 | Férovost a spolupráce | **chybí** | přidat |
| AXI-006 | Smrt není konec | **CHYBÍ** | **přidat — důležité** |
| AXI-007 | Dobrovolnictví a komunita | **chybí** | krátká zmínka |

### 2.2 Základní (hráč)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| ZAK-001 – ZAK-006 | Souboj, povolání | pokryto | ponechat, sjednotit s aktuální verzí |
| ZAK-007 | Vývoj postavy / začátek hry | částečně | **doplnit progresi a počáteční vybavení** |
| ZAK-008 | PvP souboje a šerpy | **CHYBÍ** | **přidat** |

### 2.3 Magie (hráč)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| MAG-001..004, 008..010 | Mana, sesílání, koncentrace, kniha, progrese, dovednosti | pokryto v sekci Mág | sjednotit s aktuálním zněním |
| MAG-005 | Katalog kouzel úrovně 0 (svitky) | částečně | přidat plný katalog jako přílohu |
| MAG-006 | Katalog kouzel úrovně I–V | **chybí** | **přidat plný katalog jako přílohu** |
| MAG-007 | Učení se kouzel | částečně | doplnit ceny v knihovně |
| MAG-011 | Snadná magie | **chybí** | krátká sekce |
| MAG-012 | Typy kouzel a živly | **chybí** | krátká sekce |

### 2.4 Dobrodružné dovednosti (obojí) ★ uživatelem označeno jako chybějící

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| DOV-001 | Dobrodružné dovednosti — přehled | **CHYBÍ** | **přidat samostatnou sekci** — pět dovedností, jak je hrdina získá, jeden hrdina = jedna dovednost, šifrovací karta, co najde na lokaci, viditelnost odměn |

DOV-002 (fyzická výroba) a DOV-003 (knihovník/provoz) jsou `viditelnost: organizátor` — **NEPATŘÍ do hráčské publikace**.

### 2.5 Ekonomika (hráč)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| EKO-001 | Měnový systém | **CHYBÍ** | **přidat** |
| EKO-002 | Obchodování a povoz | **CHYBÍ** | **přidat** (vč. tabulky drobného prodeje) |
| EKO-003 | Produkce surovin a zboží | **CHYBÍ** | **přidat** |
| EKO-011 | Daně národa (obojí) | **CHYBÍ** | krátká zmínka (jen co hráč vidí) |
| BYL-001 | Byliny — sběr, prodej, využití | **CHYBÍ** | **přidat** (provázaný na lektvary) |

### 2.6 Lektvary (hráč)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| LEK-001 | Systém lektvarů | **CHYBÍ** | **přidat samostatnou sekci** — typy, použití v boji, alchymista, výroba |

### 2.7 Questy (hráč)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| QUE-006 | Volené questy | **CHYBÍ** | **přidat** |
| QUE-007 | Odměny za questy a zkušenosti | **CHYBÍ** | **přidat** |

### 2.8 Příšery (obojí)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| PRI-007 | Trofeje za poražené příšery | **CHYBÍ** | **přidat** |
| PRI-008 | Drobky v zónách příšer | k ověření viditelnosti | viz §4 (Otevřené body) |

### 2.9 Situační (obojí)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| SIT-006 | Pravidla pro rozvoj měst | **chybí** | krátká hráčská verze (vize z pohledu hrdiny, ne z pohledu krále) |
| SIT-007 | Bojová akademie v Brodečku | **CHYBÍ** | **přidat** |
| SIT-008 | Hráčské nemovitosti — Dům a Panství | **CHYBÍ** | **přidat** |

### 2.10 Rozhodnutí (obojí)

| ID | Název | Status | Návrh |
|----|-------|--------|------|
| ROZ-014 | Pilíře slávy — bodování národů | **CHYBÍ** | **přidat samostatnou sekci** — ročník 2026 |

---

## 3. Návrh struktury nové publikace

```
1. Vítej, Hrdino! (intro + axiomy AXI-001..005)
2. Začátek hry (ZAK-007)
   2.1 Glejt, pouzdro, životy
   2.2 Volba povolání
   2.3 Počáteční vybavení
3. Soubojový systém (ZAK-001, ZAK-002)
4. Povolání (ZAK-003..006)
   4.1 Válečník
   4.2 Střelec
   4.3 Zloděj
   4.4 Mág
5. Magie — pro mágy podrobně (MAG-001..012)
   5.1 Mana a sesílání
   5.2 Koncentrace, reakce
   5.3 Magická kniha, učení kouzel
   5.4 Snadná magie
   5.5 Typy kouzel a živly
6. PvP a šerpy (ZAK-008)
7. Smrt není konec (AXI-006)
8. Ekonomika (EKO-001..003, EKO-011, BYL-001)
   8.1 Měna a peníze
   8.2 Obchodování a povoz
   8.3 Produkce a sběr
   8.4 Byliny
   8.5 Daně (krátce)
9. Lektvary a alchymie (LEK-001)
10. Questy (QUE-006, QUE-007)
    10.1 Volené questy
    10.2 Odměny a zkušenosti
11. Příšery a trofeje (PRI-007 + PRI-008 podle rozhodnutí)
12. Dobrodružné dovednosti (DOV-001)
13. Hrdina ve světě
    13.1 Bojová akademie (SIT-007)
    13.2 Dům a Panství (SIT-008)
    13.3 Rozvoj města — co může hrdina ovlivnit (SIT-006 hráčská verze)
14. Pilíře slávy — jak vyhraje národ (ROZ-014)
15. Přílohy
    A. Katalog kouzel úrovně 0 — svitky (MAG-005)
    B. Katalog kouzel úrovně I–V (MAG-006)
    C. Test pro Hrdiny (kvíz, ponechán)
```

---

## 4. Otevřené body — vyžadují rozhodnutí

| # | Otázka | Možnosti |
|---|--------|----------|
| O1 | **Zachovat Drobkův narativní hlas** v textu, nebo přepnout na strohý referenční styl? | (a) ponechat Drobka — vhodné pro děti / online čtení; (b) striktní reference; (c) hybrid — Drobek v rámečcích, hlavní text strohý |
| O2 | **PRI-008 Drobky v zónách příšer** — ověřit viditelnost (frontmatter to neuvádí jasně). Patří do hráčské publikace? | (a) ano, plné znění; (b) krátce v sekci 11; (c) jen organizátor |
| O3 | **MAG-005 / MAG-006 plné katalogy kouzel** — přílohou? | (a) přílohy, plný text; (b) jen odkaz na samostatné kouzelnické karty; (c) zkrácený přehled v sekci Magie |
| O4 | **ZAK-008 PvP a šerpy** — kolik detailu pro hrdiny vs. organizátora? | (a) plná pravidla; (b) jen základ (kdy smím / kdy nesmím), zbytek u krále/CP |
| O5 | **AXI-007 Dobrovolnictví a komunita** — patří do publikace pro hrdiny? Spíš obojí směrem na rodiče/orgu. | (a) ano, sekce Vítej; (b) ne — ponechat jen v organizátorské publikaci |
| O6 | **EKO-011 Daně národa** — viditelnost obojí, ale obsah je z 90 % pro krále. Zmínit v hráčské publikaci? | (a) jednou větou („z výnosů hrdinů odvádí král daň"); (b) vůbec ne |
| O7 | **Příloha s kvízem** — ponechat? | (a) ano, ponechat; (b) přepracovat na nový rozsah pravidel; (c) vyhodit |
| O8 | **Verze** — bumpnout na v2.0 (velký rozsah změn) nebo v1.2? | doporučuji v2.0 |

---

## 5. Co se NEMĚNÍ ani neaktualizuje

- Soubojový systém (ZAK-001) — beze změny od 2026-04-26.
- Útok a obrana (ZAK-002) — beze změny.
- Válečník (ZAK-003), Střelec (ZAK-004), Zloděj (ZAK-005), Mág (ZAK-006) — beze změny.
- Drobkův intro hlas v sekci „Vítej, Hrdino!" — pokud se rozhodne O1=(a) nebo (c).

---

## 6. Co dělat s tajnými pravidly

**NEPATŘÍ do hráčské publikace, ponechat odděleně:**
- ZLO-001 Zlodějina (tajné, dostane jen zloděj na kartičce / quest Chmaták)
- ROZ-005 Zlodějský systém — mechanika nálepek
- DOV-002 Šifrovací karty — fyzická výroba
- DOV-003 Mechanika odměn za dobrodružné dovednosti — provoz
- ART-001 Artefakty (org-only do schválení distribuce)
- Většina EKO-004..010 (organizátorská)
- Většina SIT-001..005 (král, vesnice, organizátor)
- Všechna PRI-001..006 (organizátorská)
- Všechna ROZ kromě ROZ-014

---

## 7. Postup po schválení

1. Uživatel projde §2 a §4, vyřeší otázky O1–O8.
2. Rulemaster vygeneruje novou publikaci `pravidla-pro-hrdiny-2026.md` (přepíše stávající).
3. Diff oproti staré verzi pro kontrolu.
4. Pokud se měnily zdrojové soubory pravidel během práce (poslední-změna pole) — flagovat.
5. Před online publikací: kontrola diakritiky, validace všech `stav: schváleno` referencí.

---

## 8. Statistika

- **Celkem pravidel v DB:** 86 (84 schváleno, 1 návrh, 1 zastaralé).
- **Pro hráčskou publikaci** (`hráč` + `obojí`, `schváleno`): ~50 pravidel.
- **V současné publikaci pokryto:** ~15 pravidel.
- **Kvantitativní gap:** ~35 pravidel chybí nebo je pokryto jen částečně.
