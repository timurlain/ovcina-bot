---
id: PRI-008
název: Drobky v zónách příšer
úroveň: systémová
kategorie: [příšery, ekonomika, drobky, zóny]
stav: schváleno
viditelnost: obojí
závisí-na: [PRI-001, EKO-001]
nahrazuje: []
poslední-změna: 2026-04-26
klíčové-fráze:
  - drobky v terénu
  - kamínky od příšer
  - jak fungují drobky
  - sběr kamínků v zóně
  - peníze od příšer v terénu
  - 1 grošový kamínek
---

# Drobky v zónách příšer

## Co jsou drobky

**Drobky** (také: kamínky, pebbles) jsou malé hladké kamínky označené pečetí království nebo organizátorů. **Každý drobek má hodnotu 1 grošu** a přijímá se ve městech jako platná měna.

Drobky **distribuují CP příšer** ve svých zónách — pohazují je nebo nechávají ležet na cestách. Hráči je sbírají při průchodu, často zatímco se vyhýbají útokům příšery. Jde o **fyzickou hru** — běh, vyhýbání, rychlý sběr — a primární zdroj drobných příjmů zejména pro mladší hrdiny.

## Alokace drobků na CP příšery

Každý CP dostává od centrálního hubu drobky podle kategorie příšery, kterou hraje. Alokace platí **na jedno herní období (2 hodiny)**:

| Kategorie CP | Drobky / období |
|--------------|-----------------|
| **I** | 25 |
| **II** | 35 |
| **III** | 50 |
| **IV** | 75 |

## Distribuční model

**Trickled (průběžné doplňování):**

- CP nedostane všechny drobky najednou na začátku období
- Centrální organizátorský hub doplňuje CP průběžně podle skutečné potřeby
- Pokud CP rychle vyhází své drobky, hub mu donese další
- Pokud CP zóna není navštěvovaná, drobky se nevyhazují zbytečně — zůstanou v zásobě

Tento model šetří fyzickou zásobu drobků a umožňuje přesměrovat tok do nejaktivnějších zón.

## Tok kamínků (recyklace)

```
Centrální hub
     ↓
CP příšera (vyhazuje v zóně)
     ↓
Hráč (sbírá drobky)
     ↓
Město (platí drobky za zboží/služby)
     ↓
Centrální hub (znovu naplní CP)
```

Celkový **fyzický inventář** drobků v oběhu je přibližně **2 000 kusů**. Díky recyklaci stačí tato zásoba pro celou hru.

## Kde se drobky NEVYHAZUJÍ

Drobky se distribuují **pouze v zónách příšer**. Nikdy ne:

- V **bezpečných zónách** podle PRI-001 (město, lokace vesnice, řeka před obědem)
- V **dungeonech a Morii** během Balinovy expedice (drobky tam nemají smysl, viz ROZ-014 a ROZ-001)
- V **organizátorských zónách** (kuchyně, sklady, klubovna)

## Fair-play a sběr

- **Žádný strop** na počet drobků na hráče za období
- Hráči si **mohou drobky předávat** mezi sebou (vzájemná pomoc, dělení v družině)
- **Krádež drobků** je možná podle pravidel PvP a krádeže (ZAK-008, ROZ-005)
- CP příšera **nesmí brát drobky zpět** poté, co je vyhodila — patří hráčům

## Vztah k odměnám za porážku příšery

Drobky jsou **dodatečný tok** — nejsou součástí odměny za porážku příšery (viz PRI-004). Hráč může získat drobky pouhým sběrem v zóně, **bez nutnosti porazit příšeru**.

Tato dvojí mechanika je záměrná:
- **Mladší hrdinové** mohou získávat drobky bez boje — jen rychlostí a obratností
- **Starší hrdinové** mohou kombinovat sběr drobků s porážkou příšery (drobky + odměna z PRI-004)

## Designové poznámky pro CP

- Vyhazujte drobky **plynule**, ne najednou — udržuje hráče v pohybu
- Pohazujte drobky tam, kde je **viditelné**, ale s nějakou překážkou (kámen, kořen) — vyžaduje malou snahu při sběru
- Pokud CP končí směnu, **vraťte zbylé drobky** do centrálního hubu (recyklace)
- Pokud zóna byla 30 minut bez návštěvy, **doplňte drobky** v jiné aktivnější zóně (přesun zásoby)
