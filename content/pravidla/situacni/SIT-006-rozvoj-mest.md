---
id: SIT-006
název: Pravidla pro rozvoj měst
úroveň: situační
kategorie: [město, stavba, budovy, rozvoj, ekonomika]
stav: schváleno
viditelnost: obojí
závisí-na: []
nahrazuje: []
poslední-změna: 2026-04-26
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

| Budova | Účel | Cena |
|--------|------|------|
| Pila | Produkce 4 dřeva za období | 20 grošů |
| Důl | Produkce 4 kamene za období | 20 grošů |
| Vinice | Produkce 4 vína za období | 20 grošů |
| Statek | Produkce 4 jídla za období | 20 grošů |

Patří postavám nebo králi. Po postavení ihned dává 2 suroviny svého typu.

### Divoká příroda (pouze ve vesnici)

Budovy s náhodnou složkou produkce — sběr, lov a rybaření. Stavět je lze **pouze ve vesnici**. Náhoda se vyhodnocuje hodem 1k6 každé období.

| Budova | Účel | Cena |
|--------|------|------|
| Lovecký srub | 2 jídla fixně každé období + náhodná produkce kožešin (1k6: 1-2 nic, 3-5: 1 kožešina, 6: 2 kožešiny) | 8 grošů, 2 dřeva |
| Herbárium | Náhodná produkce bylinek každé období (1k6, počet bylinek = hodnota kostky, tedy 1-6 bylinek) | 10 grošů, 2 dřeva, 1 jídlo |
| Rybník | 1 jídlo fixně každé období + 1k6 bonus (1-2 nic, 3-4: +1 jídlo, 5-6: +1 Rosa Valar curio) | 8 grošů, 2 dřeva, 1 kámen |

### Manufaktura (pouze ve městě)

- **Produkce:** 1 zboží za období (dává se do trhové krabice).
- **Cena:** 20 grošů.
- Po postavení dává staviteli ihned 5 grošů zpět a jedno zboží se přidá do trhové krabice.
- Každé období dá hráči 4 + X grošů, kde X je celkový počet manufaktur ve městě (včetně této). Tedy 1. manufaktura dá 5 grošů za období.
- **Daň z budovy** (viz EKO-011): U manufaktury se 1 groš za období strhává **přímo z výplaty 4 + X** — král dostává 1 groš, majitel 3 + X.

### Vojenské a magické budovy (pouze ve městě)

| Budova | Účel | Cena |
|--------|------|------|
| Psinec | Ve městě se dají kupovat psi | 10 grošů, 2 jídla, 2 dřeva |
| Kovárna | Zbraně úrovně 3 | 10 grošů, 2 dřeva, 2 kameny |
| Výheň | Zbraně úrovně 4 | 15 grošů, 2 many, 1 menhir, 2 dřeva, 2 kameny, 2 vína, 2 jídla |
| Arsenál | Zbraně úrovně 4, 5 a vyšší; kování legendárních zbraní. Nahrazuje Výheň. | 30 grošů, 10 kamene, 5 dřeva, 1 menhir |
| Svitkovna | Kouzla úrovně 3 | 10 grošů, 2 dřeva, 2 vína |
| Kouzelnická věž | Koupě a učení kouzel úrovně 4 | 15 grošů, 2 many, 1 voda hvězd, 2 dřeva, 2 kameny, 2 vína, 2 jídla |
| Citadela mudrců | Koupě a učení kouzel úrovně 4 a 5. Nahrazuje Kouzelnickou věž. | 30 grošů, 10 vína, 5 jídla, 1 voda hvězd |

### Ostatní budovy (pouze ve městě)

| Budova | Účel | Cena |
|--------|------|------|
| Bradavičné gladiátorské gymnázium Bilba Pytlíka | Groše se dají měnit za zkušenosti (5 grošů = 1 zkušenost). Potřebuje hráče 4. úrovně na založení. | 10 grošů, 6 dřeva, 2 jídla, 2 kameny, 2 vína |
| Lazaret | Postavy se mohou ve vesnici léčit zdarma | 5 grošů |

### Prestižní budovy (pouze ve městě)

Budovy podporující bodování národa v Pilířích slávy (viz ROZ-014).

| Budova | Účel | Cena |
|--------|------|------|
| Cechovní dům | Každá manufaktura ve stejném městě produkuje +1 groš za období navíc (formulka 4 + X se mění na 5 + X) | 15 grošů, 3 dřeva, 2 kamene |
| Síň trofejí | Trofeje z příšer kategorie III nebo IV zde uložené počítají **dvojnásobně** pro Pilíř Moci na konci hry (viz ROZ-014) | 20 grošů, 3 dřeva, 3 kamene |

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
