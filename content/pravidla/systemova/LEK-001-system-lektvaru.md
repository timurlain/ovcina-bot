---
id: LEK-001
název: Systém lektvarů
úroveň: systémová
kategorie: [lektvary, souboj, alchymie]
stav: schváleno
viditelnost: hráč
závisí-na: [QUE-001]
nahrazuje: []
poslední-změna: 2026-04-27
zdroj-pravdy: api.hra.ovcina.cz (ItemType=Potion)
klíčové-fráze:
  - co jsou lektvary
  - jak fungují lektvary
  - jak používat lektvar
  - kde koupit lektvar
  - účinky lektvarů
  - léčivé lektvary
  - seznam lektvarů
  - kdy lze vypít lektvar
  - bojové lektvary
  - reakční lektvary
  - jak se vyrábějí lektvary
  - alchymie a vaření lektvarů
  - quest alchymista
  - dovednost alchymista
  - lesní knihovna
  - kde se dají vařit lektvary
  - poplatek za lektvar
  - byliny do lektvarů
---

# Systém lektvarů

Lektvary jsou reprezentovány **lahvičkami** s provázkem přivázaným lístečkem, na kterém je popis a způsob použití.

> **Zdroj pravdy:** kanonický seznam lektvarů je v databázi `api.hra.ovcina.cz` (typ `Potion`). Při neshodě má vždy přednost API.

## Obecná pravidla

- **Timing určuje lísteček** každého lektvaru — některé se pijí v předkole, jiné před bojem, jiné jako reakce, některé mimo souboj.
- V jednom soubojovém kole smíš vypít **nejvýše jeden lektvar**.
- **Lektvary se nedají kombinovat** — jakmile jeden účinkuje, druhý mu neudělá místo (tato podmínka je explicitně zopakovaná na řadě lístečků).
- **Některé lektvary se nepijí** — pokropí se s nimi cíl (např. příšera).

## Vyrobitelnost a vzácnost

- **Vyrobitelné (Craftable)** — hráči-alchymisté si je vaří z bylin po splnění osobního questu **„Alchymista"**. V praxi limitované hlavně dostupnými lahvičkami.
- **Limitované (Limited)** — jednorázové, nelze vyrobit, počty kusů určují organizátoři. Jsou to vlastně legendární poklady — velice mocné, hráči si je obvykle šetří.

## Výroba malých lektvarů

Aby si hráč mohl vařit lektvary, musí:

1. **Splnit osobní quest „Alchymista"** — tím získá stejnojmennou dovednost **Alchymista**. Jde o osobní quest (jeden z herních „obálkových" osobních questů — viz QUE-001 a ROZ-006), ne o veřejný NPC quest.
2. **Sbírat byliny** v terénu — byliny rostou na různých lokacích a po celé herní mapě (plný systém viz **BYL-001**).
3. **Mít prázdné lahvičky** — to je v praxi nejtěsnější limit výroby.

### Vyrobitelné lektvary

Vyrobitelné jsou **pouze čtyři lektvary**: *Energy drink, Léčivý lektvar, Lektvar štěstí, Jed.* Každý má svůj recept (počet bylin a další náležitosti). Kanonický seznam vyrobitelných lektvarů spravuje API (`isCraftable=true`).

### Byliny — mechanika vs. naučný prvek

**Mechanicky** je každá bylina ekvivalentní jakékoli jiné: jedna bylina v ruce = jedna bylina v receptu, bez ohledu na typ. Recepty počítají kusy bylin, ne konkrétní druhy.

**Pedagogicky** mají byliny různé karty s různými druhy rostlin (jména, obrázky, popis) — aby se děti během hry seznámily s různými bylinami. Je to vzdělávací vrstva, ne herní omezení.

### Postup vaření v Lesní knihovně

Vlastní vaření probíhá výhradně v lokaci **Lesní knihovna**. Hráč:

1. Přinese si **prázdné lahvičky** a potřebný počet **bylin** podle receptu.
2. V lokaci si do lahvičky **doplní vhodnou tekutinu** (každý lektvar má svou barvu — viz lísteček).
3. **Vyrobí štítek** s popisem a instrukcemi a přiváže ho provázkem k lahvičce. Materiály na štítky jsou v lokaci připravené.
4. **Zaplatí poplatek** — orientačně **kolem 10 grošů** za lektvar (přesná částka se může v průběhu hry měnit).

> Velké (limitované) lektvary se nedají vyrobit. Hráči je získávají jako poklad — z dungeonu, z odměn za questy nebo nákupem od NPC.

---

## Bojové lektvary

### V předkole (vypité na začátku bojového kola)

| Lektvar | Efekt | Vyrobitelný |
|---------|-------|:---:|
| **Energy drink** | Doplň si **3 many**. | ano |
| **Léčivý lektvar** | Vyléč si až **20 životů**. | ano |

### Před bojem (vypité dříve, působí celý souboj)

| Lektvar | Efekt | Dostupnost |
|---------|-------|:---:|
| **Elixír bezedné many** | Do konce souboje sesíláš kouzla, která umíš, **bez potřeby trhat magickou energii**. | limitovaný |
| **Lektvar neviditelnosti** | První **3 kola boje** začínáš schovaný — nemůžeš být cílem útoku ani cíleného kouzla. | limitovaný |
| **Lektvar nezranitelnosti** | Každé poškození, které utrpíš, se **snižuje na 3 ž**. | limitovaný |
| **Lektvar štěstí** | Během boje můžeš **1× za kolo přehodit hod kostkou** a vybrat si lepší číslo. | vyrobitelný |
| **Příznivé větry** | Po vypití **celá družina ignoruje efekt jednoho bojiště**. | limitovaný |

### Reakce (během cizí akce v souboji)

| Lektvar | Efekt | Limitovaný |
|---------|-------|:---:|
| **Mnoholičný lektvar** | *Reakce.* Zvolej „Opakuju akci" a vypij lektvar — **1× zopakuj akci**, kterou právě provedl kterýkoli účastník souboje. Můžeš provést jen pokud máš ještě akci, kterou tímto vyčerpáš. | ano |

## Cílové lektvary (nepijí se)

| Lektvar | Použití | Efekt | Vyrobitelný |
|---------|---------|-------|:---:|
| **Jed** | Pokropit příšeru | **Nepij!** Zabije jednu příšeru **kategorie II. a nižší**. Příšeře **kategorie III.** sníží životy na polovinu. | ano |

---

## Mimo souboj

| Lektvar | Použití | Efekt | Limitovaný |
|---------|---------|-------|:---:|
| **Lektvar moudrosti věků** | Vypij u obchodníka | Okamžitě **postup o jednu úroveň**. | ano |
| **Lektvar znovuzrození** | Vypij u obchodníka | Můžeš **změnit své povolání**. Nové povolání bude na stejné úrovni jako staré. | ano |
| **Lektvar osobní neodolatelnosti** | Vypij před vyjednáváním | Pokus se přesvědčit nepřátele, aby ti dali své poklady a bez boje odešli. | ano |
| **Nápoj bohů** | Prodej u krále | Žádný efekt pro hráče. **Král si jej rád koupí.** | ano |

---

## Poznámky pro organizátory

- **Synchronizace s API:** vždy ber `api.hra.ovcina.cz` jako kanonický. Při doplňování / mazání lektvarů zdroj pravdy je DB.
- **Historické lektvary, které byly v dřívějších verzích pravidel a v API již nejsou:** *Lektvar života, Lektvar many, Lektvar osudu.* Funkce přebrali *Léčivý lektvar* a *Energy drink*, případně byly zrušeny.
- **Velké lektvary mohou být bojové.** Dřívější pravidlo „velké lektvary se v souboji nepoužívají" platilo pro Petrův původní seznam, ale Stáňin (současný) seznam obsahuje bojové i reakční velké lektvary. Žádný globální zákaz použití velkých lektvarů v souboji **neexistuje**.
