---
id: SIT-006
název: Pravidla pro rozvoj měst
úroveň: situační
kategorie: [město, stavba, budovy, rozvoj, ekonomika]
stav: schváleno
viditelnost: obojí
závisí-na: []
nahrazuje: []
poslední-změna: 2026-05-01
klíčové-fráze:
  - jak rozvíjet město
  - pravidla pro rozvoj měst
  - co ovlivňuje rozvoj
  - jak investovat do města
  - správa města
  - rozvoj a budování
  - pořadí stavby budov
  - prerekvizity vojenských a magických budov
  - kovárna výheň arsenál
  - svitkovna kouzelnická věž citadela mudrců
---

# Pravidla pro rozvoj měst

Stavbu budovy povoluje král, může ji postavit jak král, tak hráči. Pozor na limit počtu budov ve městě!

- **Město:** maximálně 9 budov (na začátku).
- **Vesnice:** maximálně 3 budovy.

Každá produkční budova někomu patří a obchodník dává její produkci přímo k ní.

## Ceník budov

### Produkční budovy (město i vesnice)

> Produkční budovy lze stavět v jakémkoliv národě. Pokud kingdom není rodný pro danou surovinu, produkce se halvuje (4 → 2 surovin/období). **Statek je výjimka:** jídlo nemá rodné království, Statek produkuje 4 jídla/období všude.
>
> Rodné páry: Dřevo–Elfové, Kámen–Trpaslíci, Víno–Lidé, Kožešiny–Nový Arnor.

| Budova | Účel | Cena |
|--------|------|------|
| Důl | 4 kamene / období (Trpaslíci) / 2 kamene / období (jinde) | 20 grošů |
| Koželužna | 4 kožešin / období (Nový Arnor) / 2 kožešin / období (jinde) | 20 grošů |
| Pila | 4 dřeva / období (Elfové) / 2 dřeva / období (jinde) | 20 grošů |
| Statek | 4 jídla / období (univerzální, žádné rodné království) | 20 grošů |
| Vinice | 4 vína / období (Lidé) / 2 vína / období (jinde) | 20 grošů |

Patří postavám nebo králi. Po postavení ihned dává 2 suroviny svého typu. Detailní halved-if-foreign rule viz EKO-003.

### Manufaktura (pouze ve městě)

**Cena gold (escalující):** 1. manufaktura ve městě stojí 20 g, 2. = 25 g, 3. = 30 g, 4. = 35 g, 5. = 40 g, 6. = 45 g.

**Materiály (konstantní):** 3 jednotky surovin typu A + 3 jednotky surovin typu B + 1 jídlo. A a B jsou různé suroviny ze 4 (dřevo / kámen / víno / kožešiny), hráč volí při stavbě.

**Po stavbě:** 5 g zpět + 1 zboží do trhové krabice.

**Produkce každé období:** 1 zboží do trhové krabice + výplata 4 + X grošů (X = počet manufaktur ve městě).

**Daň:** Z výplaty 1 g jde králi, 3+X majiteli. S Cechovním domem ve stejném městě se výplata mění na 5+X (1 g král, 4+X majitel).

**Výplaty manufaktury jdou přes trhovou krabici, ne přes krále** (viz EKO-004).

### Příroda (pouze ve vesnici)

Budovy s náhodnou složkou produkce — sběr, lov a rybaření. Stavět je lze **pouze ve vesnici**. Náhoda se vyhodnocuje hodem 1k6 každé období.

| Budova | Účel | Cena |
|--------|------|------|
| Herbárium | Náhodná produkce bylinek každé období (1k6, počet bylinek = hodnota kostky, tedy 1-6 bylinek) | 10 grošů, 2 dřeva, 1 jídlo |
| Lovecký srub | 2 jídla fixně každé období + náhodná produkce kožešin (1k6: 1-2 nic, 3-5: 1 kožešina, 6: 2 kožešiny) | 8 grošů, 2 dřeva, 1 kožešina |
| Rybník | 1 jídlo fixně každé období + 1k6 bonus (1-2 nic, 3-4: +1 jídlo, 5-6: +1 Rosa Valar curio) | 8 grošů, 2 dřeva, 1 kámen |

### Vojenské a magické budovy (pouze ve městě)

> **Upgrade chain.** Zbraně: Kovárna (úroveň 3) → Výheň (úroveň 4, nahrazuje Kovárnu) → Arsenál (úroveň 4–5+, nahrazuje Výheň). Kouzla: Svitkovna (úroveň 3) → Kouzelnická věž (úroveň 4, nahrazuje Svitkovnu) → Citadela mudrců (úroveň 4–5, nahrazuje Kouzelnickou věž). Detailní mechanika upgrade řetězce viz níže.

| Budova | Účel | Cena |
|--------|------|------|
| Arsenál | Zbraně úrovně 4, 5 a vyšší; kování legendárních zbraní. Nahrazuje Výheň. | 30 grošů, 5 dřeva, 10 kamene, 2 kožešin, 1 menhir |
| Citadela mudrců | Koupě a učení kouzel úrovně 4 a 5. Nahrazuje Kouzelnickou věž. | 30 grošů, 10 vína, 5 jídla, 2 kožešin, 1 voda hvězd |
| Kouzelnická věž | Koupě a učení kouzel úrovně 4. Nahrazuje Svitkovnu. | 15 grošů, 2 dřeva, 2 kameny, 2 vína, 2 jídla, 1 kožešina, 2 many, 1 voda hvězd |
| Kovárna | Zbraně úrovně 3 | 10 grošů, 2 dřeva, 2 kameny, 1 kožešina |
| Psinec | Ve městě se dají kupovat psi | 10 grošů, 2 dřeva, 2 jídla, 1 kožešina |
| Svitkovna | Kouzla úrovně 3 | 10 grošů, 2 dřeva, 2 vína |
| Výheň | Zbraně úrovně 4. Nahrazuje Kovárnu. | 15 grošů, 2 dřeva, 2 kameny, 2 vína, 2 jídla, 1 kožešina, 2 many, 1 menhir |

### Prestižní budovy (pouze ve městě)

Budovy podporující bodování národa v Pilířích slávy (viz ROZ-014).

| Budova | Účel | Cena |
|--------|------|------|
| Cechovní dům | Každá manufaktura ve stejném městě produkuje +1 groš za období navíc (formulka 4 + X se mění na 5 + X) | 15 grošů, 3 dřeva, 2 kamene, 1 kožešina |
| Síň trofejí | Trofeje z příšer kategorie III nebo IV zde uložené počítají **dvojnásobně** pro Pilíř Moci na konci hry (viz ROZ-014) | 20 grošů, 3 dřeva, 3 kamene, 1 kožešina |

### Ostatní budovy (pouze ve městě)

| Budova | Účel | Cena |
|--------|------|------|
| Bradavičné gladiátorské gymnázium Bilba Pytlíka | Groše se dají měnit za zkušenosti (5 grošů = 1 zkušenost). Potřebuje hráče 4. úrovně na založení. | 10 grošů, 6 dřeva, 2 kameny, 2 vína, 2 jídla, 2 kožešin |

### Hráčské nemovitosti (město i vesnice)

Plná pravidla viz **SIT-008 — Hráčské nemovitosti**. Zde jen ceník pro účely limitu budov a daně.

| Budova | Účel | Cena |
|--------|------|------|
| Dům | Hráčská nemovitost. Max 1 / hráč. Nájem 1 g/období v hře + 1 g/období do banku pro příští hru. **Nezapočítává se do limitu budov**, ale **podléhá dani z budov** (1 g/období do královské pokladny). | 40 grošů, 2 dřeva, 2 kameny, 1 jídlo |
| Panství | Upgrade z Domu. Max 1 / hráč. Nájem 3 g/období v hře + 3 g/období do banku. 1 bod do Pilíře Bohatství. **Nezapočítává se do limitu budov**, ale **podléhá dani z budov** (1 g/období). | 80 grošů, dodatečný recept: 4 dřeva, 4 kameny, 2 jídla, 1 šperky, 1 hračky, 1 šaty, 1 koření |

Daň z budov (1 g/období do královské pokladny — viz EKO-011) se vztahuje i na Dům a Panství.

## Pořadí stavby vojenských a magických budov

Vojenské a magické budovy se **stavějí v pevném pořadí**. Každá vyšší úroveň vyžaduje předchozí budovu jako prerekvizitu — nelze přeskočit stupeň.

### Řetězec zbraní

```
Kovárna (lvl 3)  →  Výheň (lvl 4)  →  Arsenál (lvl 4, 5 a vyšší)
```

- **Kovárna** se může postavit kdykoli (žádná prerekvizita).
- **Výheň** lze postavit **jen ve městě, kde už stojí Kovárna**.
- **Arsenál** lze postavit **jen ve městě, kde už stojí Výheň**. Po postavení Arsenálu Výheň zaniká (nahrazuje ji Arsenál — viz tabulka výše).

### Řetězec kouzel

```
Svitkovna (lvl 3)  →  Kouzelnická věž (lvl 4)  →  Citadela mudrců (lvl 4 a 5)
```

- **Svitkovna** se může postavit kdykoli (žádná prerekvizita).
- **Kouzelnickou věž** lze postavit **jen ve městě, kde už stojí Svitkovna**.
- **Citadelu mudrců** lze postavit **jen ve městě, kde už stojí Kouzelnická věž**. Po postavení Citadely Kouzelnická věž zaniká (nahrazuje ji Citadela).

### Proč

Postupný řetězec znamená, že národ musí investovat dlouhodobě a strategicky — nelze rovnou skočit na nejvyšší úroveň. Levnější budova (Kovárna / Svitkovna) je nutný první krok, který zároveň hned přináší užitek (zbraně / kouzla úrovně 3) a teprve postupné upgrady odemykají vyšší úrovně.

### Co se stavbou původní budovy

Když je postavena upgrade (Arsenál nebo Citadela), původní střední budova (Výheň / Kouzelnická věž) **zaniká** — počítá se jako jedna budova v limitu. Tedy Kovárna + Arsenál existují vedle sebe, ale Výheň se odebírá (nepočítá se do limitu 9 budov).

> *Příklad:* Aradhrynd má v 5. období Kovárnu, Výheň a tři manufaktury. V 6. období staví Arsenál — Výheň zaniká, zůstává Kovárna + Arsenál + tři manufaktury (5 budov).

## Růst města

Za každé dvě kompletní sady zboží, které město vykoupí a samo nevyrábí, se rozroste a zvedne se počet maximálních budov o 1. Výkup probíhá automaticky -- město vždy vykoupí, co je mu dovezeno, podle ceníku.

*Příklad: V druhém období elfský obchodník vykoupí z karavan (2x šaty, 2x hračky, 2x kožešiny) -- město má nyní limit budov 10.*

## Svatyně národa — archivováno

Pravidlo **Svatyně národa** (Oromeho slzy, bodování svatyně) bylo součástí Ovčiny 29 a dále se nehraje. Plné znění viz archiv: **ARC-001 — Svatyně národa a Oromeho slzy**. Bodování národů nyní zajišťuje **ROZ-014 — Pilíře slávy**.
