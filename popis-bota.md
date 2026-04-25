# Ovčina Bot — průvodce pro hráče

*Tvůj pomocník pro pravidla, svět i organizaci hry*

---

## Jak bot vypadá

Ovčina Bot je dostupný přes:

- **WhatsApp**: +420 735 907 567 ("Ovčina Bača") — doporučený způsob
- **Telegram**: `@ovcina_rulemaster_bot` (pravidla) + `@ovcina_loremaster_bot` (svět a příběhy)

Na WhatsAppu najdeš všechno v jedné konverzaci. Na Telegramu jsou dva boti — jeden pro pravidla, druhý pro svět.

## Co bot umí

### 📋 Organizace hry (NOVÉ)
- **"Kdy je hra?"** — datum, místo, uzávěrka registrace
- **"Jsem zaregistrovaný?"** — kontrola registrace pro tvůj email
- **"Kdo se mnou jede?"** — všichni účastníci z tvé rodiny/skupiny
- **"Kde spím?"** — pokoj, typ ubytování, spolubydlící
- **"Zaplatil jsem?"** — stav platby
- **"Jaké mám úkoly?"** — tvé otevřené úkoly z Bači s odkazy
- **"Co se teď děje?"** — aktuálně probíhající herní událost
- **"Co bude dál?"** — nadcházející události

### 📖 Pravidla hry
- Odpovídá na dotazy k pravidlům — soubojový systém, povolání, magie, ekonomika, questy, artefakty, příšery
- Prohledává databázi předmětů — zná všechny zbraně, zbroje, lektvary, artefakty včetně požadavků na povolání a úroveň
- Rozlišuje role — hráči vidí hráčská pravidla, organizátoři vidí i tajné mechaniky
- Pamatuje si kontext konverzace — můžeš se ptát na navazující otázky

### 🌍 Svět a příběhy
- Odpovídá v rámci postavy — jako by svět byl skutečný
- Zná historii, lokace, frakce, postavy a tajemství
- Respektuje roli tvé postavy — neprozradí to, co tvá postava nezná

### 🔍 Transparentnost
- **Ukazuje postup hledání** — vidíš, co bot právě dělá:
  - 📖 Prohledávám pravidla...
  - 🗄️ Hledám v databázi...
  - 📋 Kontroluji tvou registraci...
  - 🗓️ Načítám tvůj NPC rozpis...

## Jak začít

1. **Napiš botovi** (WhatsApp na číslo výše nebo jeden z Telegram botů)
2. **Pošli svůj email**, pod kterým jsi registrován/a na Ovčinu
3. **Na email ti přijde kód** — napiš ho botovi
4. **Hotovo!** Můžeš se ptát

## Příklady dotazů

### Organizace hry
- *"Kdy je hra a kde se sejdeme?"*
- *"Jsem zaregistrovaný na příští Ovčinu?"*
- *"Kde budu spát a s kým?"*
- *"Zaplatil jsem už?"*
- *"Kdo všechno jede se mnou?"*
- *"Jaké mám ještě úkoly?"*
- *"Jsou nějaké úkoly po termínu?"*

### Pravidla
- *"Jak funguje soubojový systém?"*
- *"Může válečník používat luk?"*
- *"Jaká kouzla jsou na 2. úrovni?"*
- *"Kolik stojí stříbrná mince?"*
- *"Jaké jsou pravidla pro obchodníky?"*
- *"Co se stane, když mě porazí příšera?"*

### Svět a příběhy (LoreMaster)
- *"Vyprávěj mi o Hůrecku."*
- *"Kdo jsou Dúnadané?"*
- *"Co se stalo v Kamenáru?"*

## Příkazy

| Příkaz | Popis |
|--------|-------|
| **/start** | Registrace a ověření emailem |
| **/help** | Seznam příkazů |
| **/pravidlo** `<dotaz>` | Zeptej se na pravidla (WhatsApp) |
| **/lore** `<dotaz>` | Zeptej se na svět (WhatsApp) |
| **/index** | Přehled všech pravidel |
| **/navrh** `<text>` | Pošli návrh na nové pravidlo |
| **/reset** | Vymaž historii konverzace |

Na WhatsAppu stačí prostě napsat otázku — bot pozná, jestli jde o pravidla, lore, nebo organizaci.

### Příkazy pro organizátory
| Příkaz | Popis |
|--------|-------|
| **/poznamka** `<text>` | Zapiš organizátorskou poznámku |
| **/poznamky** | Posledních 5 poznámek |
| **/ukol** `<text>` | Vytvoř úkol v Bače |
| **/dotazy** | Posledních 10 dotazů hráčů |
| **/kdo** | Seznam ověřených uživatelů |

## Důležité

- **Bot nevymýšlí pravidla** — aktivně vyhledává v pravidlech, databázi a souborech Ovčiny
- **Bot zná tebe** — od chvíle, kdy se ověříš emailem, ví kdo jsi a odpovídá na osobní dotazy (registrace, ubytování, úkoly)
- **Tvoje data jsou chráněná** — bot odpovídá pouze tobě na tvé vlastní otázky, ostatním neprozradí tvé osobní údaje
- **Pokud něco neví** — řekne to upřímně místo vymýšlení
- **Neuráží se** — klidně se ptej znovu jinak, pokud odpověď nebyla přesná

---
*Ovčina LARP — bot je k dispozici 24/7 na WhatsAppu i Telegramu*
