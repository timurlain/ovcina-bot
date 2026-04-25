# Ovčina Bot — průvodce pro Osud (organizátory)

*Kompletní průvodce pro ty, kdo hru tvoří*

---

## Co máš jako Osud navíc

Jako organizátor (Osud) máš rozšířený přístup k botu. Kromě hráčských funkcí můžeš:

- **Vidět všechna pravidla** včetně interních mechanik (evoluce příšer, GM procedury, tajné rozhodnutí)
- **Spravovat návrhy** — schvalovat/zamítat návrhy od hráčů
- **Editovat pravidla přímo** (pokud jsi v seznamu editorů)
- **Zapisovat poznámky** a vytvářet úkoly v Bače
- **Vidět NPC rozpis** — jaké postavy hraješ, kdy a kde
- **Zobrazit přehled dotazů** hráčů a co se jich ptají

## Nové: Organizační znalosti

Bot nyní ví všechno o hře a o tobě:

### 🎪 Informace o hře
- **"Kdy je hra?"** — datum, místo, počet registrovaných, uzávěrka
- **"Jaké jsou organizační informace?"** — vše z registrace včetně dodatečných poznámek organizátorů
- **"Co se teď děje?"** — aktuálně probíhající GameEvent
- **"Co bude dál?"** — nadcházející události (default 3)

### 👥 Osobní info
- **"Jsem zaregistrovaný?"** — tvá registrace pro aktuální hru
- **"Kdo se mnou jede?"** — rodina v tvé přihlášce
- **"Kde spím?"** — pokoj, spolubydlící, kapacita
- **"Zaplatil jsem?"** — stav platby

### 🗓️ NPC rozpis (KRITICKÉ pro organizátory)
- **"Co dneska hraju jako NPC?"** — bot načte tvůj rozpis NPC rolí
- **"Jakou postavu a kdy?"** — detaily každé role
- **"Kde mám být a jaké questy vést?"**

Bot automaticky načte rozpis z hra.ovcina.cz přes mapování tvého emailu na personId. Vrátí seznam všech tvých NPC postav s časy, lokacemi, questy a instrukcemi.

### ✅ Úkoly z Bači
- **"Co ještě musím udělat?"** — tvé otevřené úkoly
- **"Mám něco po termínu?"** — overdue úkoly
- Každý úkol obsahuje přímý odkaz na `baca.ovcina.cz/tasks/{id}`

## Editace pravidel

Vybraní editoři (5 lidí nastavených v configu) mohou přímo upravovat pravidla přes bota. Napiš přirozeným jazykem:

> *"Přidej do MAG-006 nové kouzlo úrovně III: Ledový vítr — zmrazí všechny nepřátele na 1 kolo, cena 3 many"*

> *"Změň v ZAK-003 hodnotu blízkých zbraní válečníka na úrovni 5 z 11 na 10"*

> *"Vytvoř rozhodnutí: Na příští hře budou příšery o 1 úroveň silnější"*

Bot:
1. Přečte aktuální soubor pravidla
2. Provede požadovanou změnu
3. Zapíše soubor zpět
4. Zaznamená změnu do **changelogu** (`pravidla/_changelog.md`)

### Changelog
Každá změna se automaticky zapíše:
```
- **2026-05-01 14:30** — osud@example.cz — **MAG-006**: Přidáno kouzlo Ledový vítr
```

### Dostupné editační nástroje
| Nástroj | Co dělá |
|---------|---------|
| **write_rule_file** | Upraví existující pravidlo (read → modify → write) |
| **create_decision** | Vytvoří nové rozhodnutí ROZ-xxx |

## Inteligentní vyhledávání

Bot aktivně prohledává více zdrojů a ukazuje postup:

- **📖 Prohledávám pravidla...** — tématické souhrny a jednotlivá pravidla
- **🗄️ Hledám v databázi...** — hra.ovcina.cz (předměty, příšery, lokace)
- **📋 Kontroluji detail předmětu...** — kompletní detail s požadavky na povolání
- **🔍 Hledám v souborech...** — záložní fulltext
- **📋 Kontroluji tvou registraci...** — registrace
- **🏕️ Hledám tvé ubytování...** — lodging info
- **✅ Hledám tvé úkoly v Bači...** — tasky
- **🗓️ Načítám tvůj NPC rozpis...** — schedule z hra

## Příkazy pro organizátory

| Příkaz | Popis |
|--------|-------|
| **/pravidlo** `<dotaz>` | Zeptej se na cokoliv — vidíš i tajná pravidla |
| **/navrh** `<text>` | Vytvoř návrh nového pravidla |
| **/resolve** `<NAV-ID>` | Začni řešit konkrétní návrh |
| **/schvalit** `<NAV-ID>` | Schvál návrh |
| **/zamitnout** `<NAV-ID>` | Zamítni návrh |
| **/index** | Přehled pravidel a počty |
| **/kdo** | Seznam ověřených uživatelů |
| **/poznamka** `<text>` | Zapiš poznámku |
| **/poznamky** | Posledních 5 poznámek |
| **/ukol** `<text>` | Vytvoř úkol v Bače |
| **/dotazy** | Posledních 10 dotazů hráčů |
| **/reset** | Vymaž historii konverzace |

## Příklady dotazů

### Pravidla a mechaniky
- *"Jak probíhá skupinový souboj?"*
- *"Jaké staty má Uglúk na úrovni 3?"*
- *"Kolik grošů a XP dostanou hráči za příšeru kategorie II?"*
- *"Jaké zbraně jsou dostupné na 3. úrovni?"*
- *"Může válečník používat dlouhý luk?"*

### Organizace
- *"Jaký je teď GameEvent?"*
- *"Co bude dál v programu?"*
- *"Jakou postavu dneska hraju?"*
- *"Kde mám být ve 14:00?"*
- *"Jaké mám úkoly na tuhle hru?"*
- *"Kdo z organizátorů je ubytovaný v Chatě 3?"*

### Editace (pouze editoři)
- *"Přidej kouzlo Kamenná zeď úrovně II do MAG-006..."*
- *"Vytvoř rozhodnutí: Od příští hry mohou hráči 4. úrovně kupovat 2 lektvary"*

### Návrhy
- *"/navrh Zloděj by měl mít možnost používat jedy od úrovně 3"*
- *"/resolve NAV-002"*
- *"/schvalit NAV-002"*

## Práce s návrhy pravidel

Kdokoliv ověřený může poslat návrh příkazem **/navrh**. Návrhy se ukládají do `_navrhy/` se stavem "návrh". Jako Osud je můžeš schválit nebo zamítnout.

Bot ti představí návrh, analyzuje ho proti existujícím pravidlům, upozorní na případné rozpory a pomůže ti rozhodnout.

### Hierarchie pravidel
1. **Axiomy (AXI)** — nikdy se neporušují — bezpečnost, nefyzický souboj, zábava
2. **Základní (ZAK)** — klíčové mechaniky — souboj, třídy, postup
3. **Systémová (MAG, EKO...)** — subsystémy — magie, ekonomika, questy
4. **Situační (SIT)** — pravidla podle rolí — král, obchodník
5. **Rozhodnutí (ROZ)** — jednorázová rozhodnutí

## Tipy pro efektivní práci

- **Využívej kontext** — bot si pamatuje posledních 20 zpráv
- **Ptej se konkrétně** — "Kdy a kde hraju Gothmoga?" > "Co dělám dneska?"
- **Kombinuj dotazy** — bot umí spojit pravidla + databázi + tvůj rozpis
- **Resetuj konverzaci** při přepínání mezi nesouvisejícími dotazy
- **Deleguj hráče** — hráči se mohou ptát přímo bota místo tebe
- **Edituj přirozeně** — nemusíš znát formát souborů, stačí popsat změnu

## Technické detaily

- **Čas**: Všechny časy automaticky konvertovány UTC → Europe/Prague
- **Cache**: Email → personId mapping cachován pro session
- **Progress**: Každé volání nástroje aktualizuje status message
- **Fallback**: Když rundy dojdou, bot se snaží odpovědět z toho co našel
- **Error handling**: Při chybě dostaneš řádnou hlášku, ne ticho

---
*Ovčina LARP — Osud průvodce — bot na WhatsAppu +420 735 907 567*
