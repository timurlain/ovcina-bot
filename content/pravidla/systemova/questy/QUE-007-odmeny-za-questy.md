---
id: QUE-007
název: Odměny za questy a zkušenosti
úroveň: systémová
kategorie: [questy, zkušenosti, odměny]
stav: schváleno
viditelnost: hráč
závisí-na: [QUE-001, QUE-003, QUE-006]
nahrazuje: []
poslední-změna: 2026-04-26
klíčové-fráze:
  - co dostanu za splnění questu
  - odměny za questy
  - zkušenosti za questy
  - jak fungují odměny
  - peníze za splnění úkolu
  - questové odměny přehled
  - kolik grošů za quest
  - odměna podle obtížnosti
---

# Odměny za questy a zkušenosti

## Questy jako zdroj zkušeností

Quest je úkol pro hrdinu, který mu dává **zkušenosti**. Hráči mohou questy získat různými způsoby:

- Některé jsou **vyvěšeny ve městech**.
- Jiné u **potulných mudrců**.
- Jiné jsou **vypsány na lokacích**.
- Některé jsou **tajné** a má je každý jiné.

## Zkušenosti z příšer

Zkušenosti jsou také odměnou za **poražení příšer**. Příšery vědí, zač stojí, a po zásluze hráče odmění.

## Reprezentace zkušeností

Zkušenosti jsou reprezentovány **barevnými drahokamy**. Jakmile je hráč získá, jsou jeho — **zkušenosti nejsou přenosné** mezi hráči.

## Bodové odměny podle obtížnosti

Tabulka standardních odměn za splnění questu podle obtížnosti definované v QUE-002:

| Obtížnost | Standardní odměna | Doplňková odměna |
|-----------|-------------------|------------------|
| **Lehké** | 5 zkušeností, 5 grošů | (vzácně: ingredience nebo svitek) |
| **Střední** | 15 zkušeností, 15 grošů | Předmět nebo dovednost (~30 % středních questů) |
| **Těžké** | 50 zkušeností, 50 grošů | **Vždy:** unikátní předmět (artefaktové úrovně), dovednost, nebo akce ovlivňující hru |
| **Osobní quest** (per QUE-001) | 30 zkušeností, 25 grošů | Bespoke per envelope — typicky unikátní dovednost nebo pojmenovaný předmět |

### Pravidlo pro Těžké questy

Pokud Těžký quest dává předmět, **musí to být artefaktové úrovně** (typ `Artifact` nebo `MinorArtifact`, nikdy běžná zbraň, zbroj nebo bižuterie). Konkrétní předmět určuje tvůrce obsahu při návrhu questu, ne pravidlo.

### Náklady osobního questu

Hráč platí **10 zkušeností** pro otevření obálky osobního questu (per QUE-001). Čistý zisk po splnění:

- 30 zk (odměna) − 10 zk (cena obálky) = **+20 zkušeností**
- + 25 grošů
- + bespoke odměna

## Využití zkušeností

Zkušenosti slouží k **postupu na vyšší úrovně**:

| Postup | Cena (zkušenosti) |
|--------|-------------------|
| Z úrovně 0 na 1 | 5 zk |
| Z úrovně 1 na 2 | 10 zk |
| Z úrovně 2 na 3 | 15 zk |
| Z úrovně 3 na 4 | 20 zk |
| Z úrovně 4 na 5 | 25 zk |

Úrovně se zvyšují **po jedné** a není možné přeskočit.
