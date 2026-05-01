---
id: EKO-013
název: Ceník obchodování — výkupní a prodejní ceny
úroveň: systémová
kategorie: [ekonomika, obchod, ceník]
stav: schváleno
viditelnost: hráč
závisí-na: [EKO-001, EKO-002]
nahrazuje: []
poslední-změna: 2026-05-01
klíčové-fráze:
  - kolik dostanu za víno
  - kolik stojí dřevo
  - cena obchodního zboží
  - kde prodat šperky
  - kde koupit hračky
  - co kupují trpaslíci
  - co kupují elfové
  - výkupní ceny
  - prodejní ceny
  - obchodní zisk
  - cenovka komodit
  - tabulka cen
  - ceník
---

# Ceník obchodování

Tabulka **výkupních a prodejních cen** pro každé město a každou obchodovanou komoditu.
Mechaniky obchodu (povoz, převoz, kdo s kým obchoduje) viz **EKO-002 — Obchodování a povoz**.

## Co znamenají sloupce

- **Výkup od hráčů** — kolik grošů ti dá obchodník daného města za 1 kus, když mu komoditu **prodáš**.
- **Prodej hráčům** — kolik grošů ti vezme obchodník daného města za 1 kus, když si od něj komoditu **koupíš**.
- **0** = obchodník v tomto městě s komoditou nepracuje (nekupuje / neprodává).

## Velká tabulka — všechny ceny

| Město | Komodita | Typ | Výkup od hráčů | Prodej hráčům |
|---|---|---|---:|---:|
| Elfové | Hračky | Zboží | 12 | 0 |
| Elfové | Šperky | Zboží | 0 | 5 |
| Elfové | Koření | Zboží | 10 | 0 |
| Elfové | Šaty | Zboží | 10 | 0 |
| Elfové | Víno | Surovina | 4 | 8 |
| Elfové | Dřevo | Surovina | 0 | 2 |
| Elfové | Kámen | Surovina | 3 | 6 |
| Elfové | Kožešiny | Surovina | 2 | 4 |
| Trpaslíci | Hračky | Zboží | 0 | 5 |
| Trpaslíci | Šperky | Zboží | 10 | 0 |
| Trpaslíci | Koření | Zboží | 12 | 0 |
| Trpaslíci | Šaty | Zboží | 10 | 0 |
| Trpaslíci | Víno | Surovina | 3 | 6 |
| Trpaslíci | Dřevo | Surovina | 4 | 8 |
| Trpaslíci | Kámen | Surovina | 0 | 0 |
| Trpaslíci | Kožešiny | Surovina | 3 | 6 |
| Lidé | Hračky | Zboží | 10 | 0 |
| Lidé | Šperky | Zboží | 8 | 0 |
| Lidé | Koření | Zboží | 14 | 0 |
| Lidé | Šaty | Zboží | 0 | 5 |
| Lidé | Víno | Surovina | 0 | 2 |
| Lidé | Dřevo | Surovina | 3 | 6 |
| Lidé | Kámen | Surovina | 3 | 6 |
| Lidé | Kožešiny | Surovina | 2 | 4 |
| Nový Arnor | Hračky | Zboží | 10 | 0 |
| Nový Arnor | Šperky | Zboží | 8 | 0 |
| Nový Arnor | Koření | Zboží | 0 | 5 |
| Nový Arnor | Šaty | Zboží | 14 | 0 |
| Nový Arnor | Víno | Surovina | 3 | 6 |
| Nový Arnor | Dřevo | Surovina | 3 | 6 |
| Nový Arnor | Kámen | Surovina | 4 | 8 |
| Nový Arnor | Kožešiny | Surovina | 1 | 2 |

## Rychlý přehled — co kde levně koupíš

- **Elfové** prodávají: Šperky (5), Dřevo (2)
- **Trpaslíci** prodávají: Hračky (5)
- **Lidé** prodávají: Šaty (5), Víno (2)
- **Nový Arnor** prodává: Koření (5)

## Rychlý přehled — co kde draze prodáš

- **Elfové** vykupují: Hračky (12), Koření (10), Šaty (10), Víno (4)
- **Trpaslíci** vykupují: Koření (12), Šperky (10), Šaty (10), Dřevo (4), Kožešiny (3)
- **Lidé** vykupují: Koření (14), Hračky (10), Šperky (8), Kámen (3), Dřevo (3)
- **Nový Arnor** vykupuje: Šaty (14), Hračky (10), Šperky (8), Kámen (4), Dřevo (3), Víno (3)

## Nejvýhodnější obchodní trasy

| Komodita | Kup za | Prodej za | Zisk / kus |
|---|---|---|---:|
| **Koření** | Nový Arnor (5) | Lidé (14) | **+9 grošů** |
| **Šaty** | Lidé (5) | Nový Arnor (14) | **+9 grošů** |
| **Hračky** | Trpaslíci (5) | Elfové (12) | **+7 grošů** |
| **Šperky** | Elfové (5) | Trpaslíci nebo Lidé / N. Arnor (10 / 8) | **+5 / +3 grošů** |
| **Dřevo** | Elfové (2) | Trpaslíci (4) | **+2 groše** |
| **Víno** | Lidé (2) | Elfové (4) | **+2 groše** |

Suroviny (víno, dřevo, kámen, kožešiny) mají obecně **menší marži** než obchodní zboží (hračky, šperky, koření, šaty).

## Poznámky

- Pro převoz komodit potřebuješ **povoz** (EKO-002, 10 grošů, minimálně dvě postavy).
- Ceny platí pro **1 kus / 1 jednotku** komodity.
- Pokud obchodník nabude dojmu, že hráči obešli pravidla převozu (např. nesli sudy v rukou), nemusí s nimi obchodovat (EKO-002).
- Ceny mohou být v průběhu hry organizátorem upraveny — vždy si u obchodníka ověř aktuální nabídku.
