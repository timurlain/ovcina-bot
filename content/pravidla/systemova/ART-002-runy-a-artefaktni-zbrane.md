---
id: ART-002
název: Runy a artefaktní zbraně
úroveň: systémová
kategorie: [artefakty, runy, zbraně, knihovna, poklady]
stav: schváleno
viditelnost: organizátor
závisí-na: [ART-001, ROZ-011, EKO-005, EKO-006]
nahrazuje: []
poslední-změna: 2026-04-26
klíčové-fráze:
  - jak připravit runy pro artefaktní zbraně
  - tajná tabulka run
  - runová slova artefaktů
  - vzácnost run R U C
  - losování run z pytlíčku
  - překladová tabulka pro knihu artefaktů
  - runy pro legendární předměty
---

# Runy a artefaktní zbraně

Toto pravidlo je určeno pouze pro organizátory. Popisuje přípravu fyzických run, jejich interní mapování na tvary, vzácnosti a finální runová slova pro artefakty.

Konkrétní fyzická sada pro tisk používá STL soubory v `games/karticky/runy/print-set/`. Její aktuální mapování je v `games/karticky/runy/print-set/print-mapping.md`. Tabulky tvarů ze zdrojového dokumentu níže slouží jako systematická šablona, ne jako závazné přiřazení grafických run pro tisk.

## Základní identita run

Každé runě je přiřazeno číslo, písmeno abecedy a pevné runové jméno. Písmeno není nutné pro mechaniku, ale pomáhá při zapamatování. Číslo slouží primárně pro párování při přípravě hry.

| Číslo | Písmeno | Runa |
|------:|:-------:|------|
| 1 | A | Ash |
| 2 | B | Bur |
| 3 | C | Coch |
| 4 | D | Dur |
| 5 | E | Era |
| 6 | F | Fal |
| 7 | G | Gim |
| 8 | H | Hudr |
| 9 | I | Ishi |
| 10 | J | Jalach |
| 11 | K | Krim |
| 12 | L | Luk |
| 13 | M | Misa |
| 14 | N | Nazg |
| 15 | O | Oba |
| 16 | P | Paa |
| 17 | Q | Quele |
| 18 | S | Sil |
| 19 | R | Raor |
| 20 | T | Tul |
| 21 | U | Uch |
| 22 | V | Vira |
| 23 | W | Welp |
| 24 | X | Exo |
| 25 | Y | Yrum |
| 26 | Z | Zum |

## Přiřazení fyzických tvarů

Každé runě přísluší fyzický tvar. Konkrétní tvary jsou libovolné a záleží na dostupných materiálech. Při přípravě se vygeneruje náhodná posloupnost čísel 1 až 26; podle ní se jednotlivým tvarům přiřadí runa s daným číslem.

Pro aktuální tisk nepoužívej tuto zdrojovou ukázkovou tabulku přímo. Použij STL mapování v `games/karticky/runy/print-set/print-mapping.md`.

| Tvar | Číslo runy |
|------|-----------:|
| Tvar 1 | 21 |
| Tvar 2 | 10 |
| Tvar 3 | 25 |
| Tvar 4 | 19 |
| Tvar 5 | 23 |
| Tvar 6 | 3 |
| Tvar 7 | 1 |
| Tvar 8 | 13 |
| Tvar 9 | 12 |
| Tvar 10 | 18 |
| Tvar 11 | 14 |
| Tvar 12 | 6 |
| Tvar 13 | 15 |
| Tvar 14 | 8 |
| Tvar 15 | 22 |
| Tvar 16 | 4 |
| Tvar 17 | 17 |
| Tvar 18 | 26 |
| Tvar 19 | 24 |
| Tvar 20 | 20 |
| Tvar 21 | 7 |
| Tvar 22 | 9 |
| Tvar 23 | 11 |
| Tvar 24 | 5 |
| Tvar 25 | 2 |
| Tvar 26 | 16 |

## Vzácnost run

Run je více, než kolik je potřeba pro aktuální seznam artefaktů. Některé tedy mohou zůstat ve hře nevyužité, případně tvoří rezervu pro navýšení počtu legendárních předmětů.

| Kód | Číslo runy |
|-----|-----------:|
| R1 | 5 |
| R2 | 3 |
| R3 | 16 |
| R4 | 13 |
| R5 | 25 |
| R6 | 24 |
| R7 | 8 |
| R8 | 9 |
| R9 | 22 |
| R10 | 20 |
| R11 | 18 |
| U1 | 21 |
| U2 | 19 |
| U3 | 11 |
| U4 | 12 |
| U5 | 17 |
| U6 | 10 |
| C1 | 26 |
| C2 | 1 |
| C3 | 4 |
| C4 | 7 |
| není | 2 |
| není | 15 |
| není | 6 |
| není | 14 |
| není | 23 |

## Distribuce ve hře

| Vzácnost | Četnost | Způsob získání |
|----------|---------|----------------|
| Vzácné runy R | 1x každá | Odměna za velkou vizi v knihovně. Jsou dohledatelné podle jména. |
| Neobvyklé runy U | 3x každá | Odměna za poražení větších příšer kategorie III a vyšší. Příšera vydá velkou neidentifikovanou runu, za kterou si hráč v knihovně vylosuje náhodnou U runu, ideálně vytažením z pytlíčku. |
| Běžné runy C | 6x každá | Součást malých pokladů získatelných za vizi v knihovně. Hráči mohou rovnou tahat z pytlíčku. |

## Interní mapovací tabulka

Tato tabulka spojuje pevná jména run, fyzické tvary a herní kódy vzácnosti. Nepublikovat hráčům v této podobě.

| Číslo | Písmeno | Runa | Tvar | Kód |
|------:|:-------:|------|------|-----|
| 1 | A | Ash | Tvar 7 | C2 |
| 2 | B | Bur | Tvar 25 | není |
| 3 | C | Coch | Tvar 6 | R2 |
| 4 | D | Dur | Tvar 16 | C3 |
| 5 | E | Era | Tvar 24 | R1 |
| 6 | F | Fal | Tvar 12 | není |
| 7 | G | Gim | Tvar 21 | C4 |
| 8 | H | Hudr | Tvar 14 | R7 |
| 9 | I | Ishi | Tvar 22 | R8 |
| 10 | J | Jalach | Tvar 2 | U6 |
| 11 | K | Krim | Tvar 23 | U3 |
| 12 | L | Luk | Tvar 9 | U4 |
| 13 | M | Misa | Tvar 8 | R4 |
| 14 | N | Nazg | Tvar 11 | není |
| 15 | O | Oba | Tvar 13 | není |
| 16 | P | Paa | Tvar 26 | R3 |
| 17 | Q | Quele | Tvar 17 | U5 |
| 18 | S | Sil | Tvar 10 | R11 |
| 19 | R | Raor | Tvar 4 | U2 |
| 20 | T | Tul | Tvar 20 | R10 |
| 21 | U | Uch | Tvar 1 | U1 |
| 22 | V | Vira | Tvar 15 | R9 |
| 23 | W | Welp | Tvar 5 | není |
| 24 | X | Exo | Tvar 19 | R6 |
| 25 | Y | Yrum | Tvar 3 | R5 |
| 26 | Z | Zum | Tvar 18 | C1 |

## Kódy pro přidělení artefaktům

Každému artefaktu se přiřadí tři runy tak, že se náhodně přeuspořádá pořadí sloupců v této tabulce.

| Sada | Vzácná | Neobvyklá | Běžná |
|-----:|--------|-----------|-------|
| 1 | R1 | U1 | C1 |
| 2 | R2 | U2 | C2 |
| 3 | R3 | U3 | C3 |
| 4 | R4 | U4 | C4 |
| 5 | R5 | U5 | C1 |
| 6 | R6 | U6 | C2 |
| 7 | R7 | U1 | C3 |
| 8 | R8 | U2 | C4 |
| 9 | R9 | U3 | C1 |
| 10 | R10 | U4 | C2 |
| 11 | R11 | U5 | C3 |
| 12 | R12 | U6 | C4 |

Poznámka: `R12` je ve zdrojové šabloně uvedeno jako rezerva, ale ve zdrojové tabulce vzácnosti nemá přiřazenou konkrétní runu. Nepoužívat bez doplnění mapování.

## Runová slova artefaktů

Následující kódy a runová slova jsou náhodně vygenerovaný, ale použitelný příklad pro hru.

| Artefakt | Kód 1 | Kód 2 | Kód 3 | Runa 1 | Runa 2 | Runa 3 |
|----------|-------|-------|-------|--------|--------|--------|
| Luk Svistič | R10 | U4 | C1 | Tul | Luk | Zum |
| Ošklivá sekera | R11 | U1 | C2 | Sil | Uch | Ash |
| Meč Blesková čepel | R8 | U6 | C4 | Ishi | Jalach | Gim |
| Dýka Vrahův trn | R6 | U6 | C4 | Exo | Jalach | Gim |
| Arcimágova hůl | R1 | U4 | C1 | Era | Luk | Zum |
| Kutna krále lukostřelců | R9 | U3 | C3 | Vira | Krim | Dur |
| Sluneční disk | R4 | U1 | C3 | Misa | Uch | Dur |
| Panovníkova koruna | R7 | U5 | C4 | Hudr | Quele | Gim |
| Dračí pancíř | R5 | U2 | C3 | Yrum | Raor | Dur |
| Náhrdelník síly | R3 | U2 | C2 | Paa | Raor | Ash |
| Kamenný golem | R2 | U5 | C2 | Coch | Quele | Ash |

## Publikační omezení

- Kompletní mapovací tabulku a finální přiřazení run k artefaktům drží pouze organizátoři.
- Do knihy artefaktů patří jen organizátory vybraná překladová tabulka, ne celý interní přehled.
- Hráčská pravidla mohou mluvit o hledání run a skládání artefaktů, ale nesmí prozradit úplné runové kombinace.
