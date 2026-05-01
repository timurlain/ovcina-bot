# Události pro království — kniha rozhodnutí

> *„Koruna není pohodlí, nýbrž tíže. A každé období žádá od krále nové slovo."*

Soubor obálek a vyhodnocovacích klíčů pro hru **Ovčina 30 — Balinova pozvánka**. Každé období dostává král jedné z obálek; přečte ji, rozhodne se pro jednu ze tří možností, a obchodník vyhodnotí důsledek.

**Tématická linka:** Události se odehrávají v období příprav na Balinovu výpravu do Morie (T.A. 2864). Většina rozhodnutí se proplétá s hlavními příběhovými příležitostmi hry — **Daon Grimburgoth a jeho Grimburzové** rozdmýchávají nedůvěru a přepadávají vesnice; **spojenectví čtyř království** je v ohrožení; **Balinovi poslové** zkoušejí, kdo z králů je hoden výpravy. Plný kontext viz `../game-30-design.md`.

## Mechanika v kostce

- **Čtyři království** rozhodují souběžně: Aradhrynd (elfové), Esgaroth (lidé), Azanulinbar-dum (trpaslíci), Nový Arnor.
- **Sedm aktivních období** (P2–P8). P1 je úvod hry, P9 závěr — bez události. Některá období neobsahují událost pro každé království (viz matice níže).
- **Asynchronní (offline) události** — král obdrží obálku, do konce období odevzdá rozhodnutí (papírek s písmenem A/B/C) obchodníkovi. Bez odpovědi = **ignorováno**.
- **Live události** (označené `LIVE`) — odehrávají se v reálném čase v terénu, vyžadují okamžitou reakci království, **nelze odložit ani přepsat**.
- **Žádná volba není „správná".** Každá možnost má cenu i přínos.

## Tři pilíře slávy

Pilíře sčítá obchodník na konci hry podle [PRA-15 Pilíře slávy](../pravidla/pravidla-pro-obchodniky):

| Pilíř | Co sem patří |
|---|---|
| **Moc** | držené vesnice, postavené vojenské budovy, trofeje |
| **Bohatství** | vykoupené cizí zboží, držené suroviny, plná trhová krabice |
| **Vědomosti** | splněné osobní questy, listy *Mazarbul Aznân* |

Události některé pilíře navyšují přímo (`+1 Pilíř X`). **Strop neexistuje** — sláva sebraná z událostí se sčítá s questovou.

## Doom

„Doom" je skrytý důsledek špatného rozhodnutí. Hráči se o něm v okamžiku volby nedozvědí; obchodník ho zaznamená a Osud ho promítne do **závěrečného vyhodnocení nebo do dalšího ročníku hry**.

- 1× Doom = drobný stín nad královstvím (např. zlé sny, ztracený posel).
- 2× Doom = vážnější trhlina (např. mor, požár v období končící hry).
- 3+× Doom = něco se zlomí napevno — záleží na Osudovi.

## Měřítko odměn a nákladů (% královského příjmu)

Hodnoty se škálují podle **královského příjmu v daném období** — symetricky pro odměnu i pro náklad. Malá = 25 % příjmu, střední = 50 %, velká = 75 %. XP odměny **nejsou** finančně škálované (5 / 10 / 15 podle závažnosti).

| Období | Královský příjem | Malá (25 %) | Střední (50 %) | Velká (75 %) |
|---|---:|---:|---:|---:|
| P2 (úvod) | ~150 g | **40 g** | **75 g** | **115 g** |
| P3 | ~180 g | **45 g** | **90 g** | **135 g** |
| P4 | ~220 g | **55 g** | **110 g** | **165 g** |
| P5 | ~260 g | **65 g** | **130 g** | **195 g** |
| P6 | ~320 g | **80 g** | **160 g** | **240 g** |
| P7 | ~380 g | **95 g** | **190 g** | **285 g** |
| P8 (vrchol) | ~450 g | **115 g** | **225 g** | **340 g** |

Královský příjem zahrnuje daň z obyvatel (~34 hráčů × 1 g), daň z budov, podíl na produkci surovin a manufakturní výplaty. Příjem roste 3× od začátku ke konci hry.

> **Královská kniha** ukazuje králi přesné groše u každé volby (cena, kterou zaplatí), aby mohl rozhodnout informovaně. **Odměny zůstávají skryté** — vidí je jen obchodník v evaluation packu.

> Předpoklad: Block 3 (kingdom production calibration) ekonomického balancingu je dosud BLOCKED. Čísla jsou derivovaná z royal sinks (~2,070 g/království za hru: Balinova výprava 1,500 + budovy 250 + rezerva 200 + mitrilová zbroj 120) a daňové formule. Po finalizaci Block 3 případně přepočítej.

## Matice událostí

| Období | Aradhrynd (elfové) | Esgaroth (lidé) | Azanulinbar-dum (trpaslíci) | Nový Arnor |
|:-:|:-:|:-:|:-:|:-:|
| P1 | — | — | — | — |
| P2 | Uprchlíci | Uprchlíci | Uprchlíci | Uprchlíci |
| P3 | Štědrý mecenáš | Štědrý mecenáš | Štědrý mecenáš | Štědrý mecenáš |
| P4 | **Neklidný hřbitov** `LIVE` | Duch u brodu | Napětí s elfy z Arnoru | Válka šlechtických rodů |
| P5 | Starý kamenný most | Válka šlechtických rodů | **Neklidný hřbitov** `LIVE` | Měchy v kovárně |
| P6 | Válka šlechtických rodů | **Útok na elfy** `LIVE` | Válka šlechtických rodů | **Neklidný hřbitov** `LIVE` |
| P7 | Zamčená truhla | **Neklidný hřbitov** `LIVE` | Balinův posel (Lóni) | Posel z vorařské osady |
| P8 | Stádo válečných koní | Válečník z Ailgarthu | Trpasličí průmysl | Věštba trpasličí zkázy |
| P9 | — | — | — | — |

## Soubory v této složce

| Soubor | Komu |
|---|---|
| `aradhrynd-kral.md` | Král elfů — 8 stran (titulka + 7 obálek) |
| `aradhrynd-obchodnik.md` | Obchodník elfů — 8 stran vyhodnocení |
| `esgaroth-kral.md` | Starostka Nenneke IV. — 8 stran |
| `esgaroth-obchodnik.md` | Obchodník lidí — 8 stran vyhodnocení |
| `azanulinbar-kral.md` | Trpasličí král — 8 stran |
| `azanulinbar-obchodnik.md` | Obchodník trpaslíků — 8 stran vyhodnocení |
| `arnor-kral.md` | Vládce Nového Arnoru — 8 stran |
| `arnor-obchodnik.md` | Obchodník Arnoru — 8 stran vyhodnocení |

## NPC které je třeba připravit

Mimo královy a obchodníky přítomné ve městech musí Osud zajistit:

| NPC | Pro koho | Kdy | Stručně |
|---|---|---|---|
| **Mistr-mecenáš** (×4 šablona) | všechna království | P3 | Bohatý dárce — krátký dopis stačí |
| **Bandité Brodu** (skupina 3–5) | Esgaroth | P6 LIVE | Žoldnéři plánující úder na elfy |
| **Sphectorští bratři** (skupina 3) | scénka u všech | dle volby C | 2 šlechtici + 1 soudce — hrají hráči |
| **Duch z brodu** | Esgaroth | P4 | Naříkající stín u brodu nedaleko Esgarothu |
| **Lóni z Erebora — Balinův posel** | Azanulinbar | P7 | Canon postava (LotR App. A); nese Balinovu pozvánku, zkouší znalost mohylového hesla |
| **Válečník z Ailgarthu** | Esgaroth | P8 | Severšťan u piva, hledá krajana |
| **Tichý posel z vorařské osady** | Nový Arnor | P7 | Doručovatel s opracovaným dřevem |
| **Vědma severu** | Nový Arnor | P8 | Vize v ohni — Erebor v plamenech |
| **Nemrtví na hřbitově** | LIVE u 4 království | P4–P7 | Bestiář; používají existující mechaniku |

Detaily NPC budou dodány samostatně Loremasterem (skill `loremaster-npc-creator`).

## Lokační šifry (DOV) k umístění

Čtyři události mají skrytou znalost (heslo, jméno, číslo). Aby měly cesty více kanálů (knihovna / NPC / šifra), navrhujeme tyto **statické cipher overlay zprávy** rozmístit v terénu:

| Událost | Klíč | Lokace pro umístění | Ciphertext (jen písmena + mezery) |
|---|---|---|---|
| Zamčená truhla *(elfové, P7)* | OROPHER | Stará elfí svatyně poblíž Aradhryndu | `OROPHER OTEC THRANDUILUV` |
| Válečník z Ailgarthu *(lidé, P8)* | 37 | Esgarothská knihovna nebo ailgarthský sloup | `AILGARTH MA TRICETSEDM DOMU` |
| Posel z vorařské osady *(Arnor, P7)* | OHTAR | Vorařská osada — značka na sloupu | `SPRAVCE BRODU SE JMENUJE OHTAR` |
| Balinův posel *(trpaslíci, P7)* | „Hora je naše. Vrátíme se." | Mohyla posledního krále Ereboru | `HORA JE NASE VRATIME SE` |

Per [DOV-001 / DOV-002](../pravidla/systemova/dovednosti) — **bez interpunkce**, jen písmena a mezery, T3 obtížnost (klíč k velkému payoff). Per kingdom-quest pravidlu **max 1 sáček per lokace**, šifry zde slouží jako *intel* kanál, ne jako fyzický sáček.

## Poznámky pro Osud

- Pillar bonus z událostí je *aditivní* — quest-systém ho převládá (cap z brain not enforced).
- LIVE události vyžadují **NPC v terénu v daném období**. Plánujte logistiku.
- Doom se eviduje skryté — nikdy hráčům neoznamujte, že „získali Doom".
- *Dědictví po šlechtici* a *Podivný kult* jsou parking-lot — návrhářské rezervy, do tisku nejdou.

---

**Poslední aktualizace:** 2026-05-01 · Loremaster
