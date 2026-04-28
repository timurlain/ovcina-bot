---
id: BYL-001
název: Byliny — sběr, prodej a využití
úroveň: systémová
kategorie: [byliny, sběr, ekonomika, alchymie, bylinkář, questy]
stav: schváleno
viditelnost: hráč
závisí-na: [LEK-001, ROZ-013, QUE-001, QUE-003]
nahrazuje: []
poslední-změna: 2026-04-27
zdroj-pravdy: api.hra.ovcina.cz (Item #452 Byliny, Quest #75 Bylinkář)
klíčové-fráze:
  - co jsou byliny
  - kde sbírat byliny
  - jak prodat byliny
  - byliny do lektvarů
  - quest bylinkář
  - sběr bylin
  - lokace s bylinami
  - cena bylin
  - byliny obchodník
  - jak získat XP za byliny
  - titul bylinkář
---

# Byliny — sběr, prodej a využití

Byliny jsou herní zdroj — fyzicky reprezentovaný **kartičkou rostliny**. Hrdina je sbírá na lokacích po Středozemi a může je používat třemi způsoby: plnit s nimi quest **„Bylinkář"**, prodávat je obchodníkům, nebo z nich (s dovedností Alchymista) vařit lektvary.

> **Zdroj pravdy:** Item #452 *Byliny* v API `api.hra.ovcina.cz` (Resource).

## Sběr bylin

Byliny rostou na zelených lokacích — typicky kde NPC pečuje o zahradu, kde se konají rituály, nebo kde se les drží v ruce. Mezi známé sběrné lokace patří:

- **Tichá zahrada**
- **Příbytky skřítků**
- **Ostrov čarodějnice**
- **Rhosgobel**
- **Aradhrynd**
- **Podhorany**
- **Močál**

Hrdina si byliny **vezme z lokace** podle jejích pravidel — typicky z košíku, podle cedulky („1 bylina za období") nebo dle pokynu organizátora lokace.

## Mechanika — různé karty, jeden druh

Existuje více **různých karet** byliny — různé druhy rostlin (jména, ilustrace, popis). Toto má **dvojí význam**:

| Vrstva | Důsledek |
|--------|----------|
| **Mechanická (alchymie, prodej)** | Každá bylina = jedna bylina. Recepty a obchodníci počítají **kusy**, nikoli druh. |
| **Pedagogická + bonus za rozmanitost** | Pro quest „Bylinkář" se počítá počet **různých druhů**, které hrdina sebral. |

## Tři použití bylin

### 1. Quest „Bylinkář" (General quest)

> *„Na naší zemi rostou různé léčivé bylinky. Posbírej co nejvíce různých bylinek do svého herbáře."*

**Bylinkář je obecný quest** — může ho splnit kdokoli, bez ohledu na povolání. Hrdina ukáže obchodníkovi nebo Osudu sbírku **různých** bylin a postupně získává XP a titul:

| Počet různých bylin | Odměna |
|:---:|--------|
| 5 | **2 XP** |
| 10 | dalších **4 XP** |
| 15 | dalších **8 XP** + titul **„Bylinkář"** |

**Označení karet:** obchodník nebo Osud kartičky označí (typicky dírkou děrovačem nebo razítkem) tak, aby je nebylo možné nárokovat dvakrát. Označení **nezabraňuje** dalšímu použití karty na alchymii nebo prodej — jen na opakovaný nárok XP.

### 2. Prodej obchodníkovi (5:1)

Hrdina může prodat byliny **jakémukoliv obchodníkovi v jakémkoliv království**:

> **5 bylin = 1 groš**

Žádný denní limit, žádné omezení — pokud má hrdina byliny, obchodník je rád vykoupí. Cena je nízká, takže prodávání je víc cesta, jak se zbavit přebytku, než hlavní zdroj příjmu.

### 3. Výroba lektvarů (s dovedností Alchymista)

Hrdina s dovedností **Alchymista** (osobní quest, viz ROZ-013, LEK-001) může z bylin vařit lektvary v **Lesní knihovně**. Recepty počítají **počet** bylin, ne druh — pro alchymii jsou všechny byliny mechanicky rovnocenné.

Vyrobitelné jsou 4 lektvary: *Energy drink, Léčivý lektvar, Lektvar štěstí, Jed.* Přesné recepty viz `LEK-001-system-lektvaru.md`.

## Poznámky pro organizátory

- **Souběh quest + alchymie + prodej:** označení kartičky (dírka/razítko) jen blokuje opakovaný nárok XP — bylinu si hrdina dál může nechat na alchymii nebo prodej. Nejde o spotřebu, jen o evidenci.
- **Distribuce na lokacích:** každá zelená lokace má vlastní pravidla (košík, denní limit, „1 za období"). Sběr by neměl být frustrující — pokud je v zóně 0 bylin po prvním období, je nastavení špatně.
- **Rovnováha s alchymií:** hlavním limitem výroby lektvarů je **počet lahviček** (ROZ-013/LEK-001), ne bylin. Byliny by tedy měly být v každém období dostupné v rozumném počtu.
- **Tituly:** „Bylinkář" je trvalý titul, který si hrdina může nárokovat na glejtu / obálce. Není to dovednost s herní mechanikou — je to vyznamenání.
- **Více vítězů u titulu Bylinkář:** titul mohou získat všichni, kdo dosáhnou 15 různých bylin. Není to soutěž o 1. místo.

## Související pravidla

- **LEK-001** — Systém lektvarů (cíl alchymie)
- **ROZ-013** — Alchymie a lektvary (Lesní knihovna, dovednost Alchymista)
- **QUE-003** — Globální questy (Bylinkář spadá pod tuto kategorii)
- **EKO-002** / **EKO-003** — Obchodování a produkce surovin

## Otevřené otázky pro budoucí ladění

- Mají různé byliny vlastní herní funkci mimo questy a alchymii (např. pro hraničáře, kuchaře, vesnice)?
- Bude existovat „pokročilá" varianta dovednosti Bylinkář, která zvyšuje šanci najít byliny na lokaci nebo otevírá speciální recepty?
