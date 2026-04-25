---
id: ZAK-002
název: Útok a obrana
úroveň: základní
kategorie: [souboj, poškození, zbraně, zbroj]
stav: schváleno
viditelnost: hráč
závisí-na: [AXI-001, ZAK-001]
nahrazuje: []
poslední-změna: 2026-04-05
klíčové-fráze:
  - jak útočím
  - jak se bráním
  - útočné a obranné karty
  - počet útoků za kolo
  - jak fungují životy
  - co znamenají čísla na kartičkách
  - útok a obrana pravidla
---

# Útok a obrana

Každý účastník souboje je v každém kole charakterizován dvěma čísly: **útočným číslem** a **obranným číslem**. Tato pravidla popisují, jak se počítá poškození při útoku zbraní.

## Útočné číslo (ÚČ)

Má smysl pouze pokud provádíš **blízký nebo střelecký útok**:

```
ÚČ = Útok zbraně (UZ) + Bonusy (dovednosti, kouzla, …)
```

## Obranné číslo (OČ)

```
OČ = Kvalita zbroje (KZ) + Bonusy (dovednosti, kouzla, …) + Obrana zbraně (OZ)
```

**Poznámka**: Zbraň se vytahuje v předkole a její OZ platí celé kolo.

## Výpočet poškození

Během útoku:

1. Vyber cíl.
2. Hoď šestistěnnou kostkou.
3. Padne-li ti hodnota **6, můžeš házet znova** (a znova, pokud opět padne 6).
4. Celkový hod **[k6+]** přičti ke svému ÚČ.
5. Od této hodnoty odečti OČ obránce.

```
Poškození uděleno = ÚČ útočníka + [k6+] − OČ obránce
```

Pokud je výsledek nula nebo méně, obránce neutrpí žádné poškození.

## Bezvědomí

Pokud má postava po útoku **≤ 0 životů**, upadá do bezvědomí a do konce souboje nemůže zasahovat.

## Léčení a bezvědomí

Během souboje můžeš být léčen **pouze**:
- Kouzly
- Předměty
- Dovednostmi, na kterých je to vysloveně uvedeno

### Po výhře

- Vyléčíš se na **1 život**.
- Můžeš sníst **1 jídlo** a vyléčit se do plného stavu.
- Nemáš-li jídlo či jiný léčující předmět, musíš se jít vyléčit do města.

### Poražení

Poražené postavy mají 0 životů a musí se jít **oživit do nejbližšího města** (s rukama za hlavou, nemohou být znovu napadeni a nesmí sbírat předměty).

## Vybavení v souboji

U sebe mohou postavy nést libovolné množství vybavení, v souboji ale mohou používat:

- **Jednu zbraň**
- **Jednu sadu zbroje** (zbroj + helma + štít)
- **Maximálně 2 kusy magických šperků** (bižuterie) — z toho **maximálně 1 náhrdelník / amulet**, zbytek prsteny.
- **Jeden lektvar** vypitý v předkole

## Společníci a ovládané bytosti (OB)

Během hry mohou hráče doprovázet ovládané bytosti (voják, pes, válečný pes apod.).

- Ovládaná bytost se v souboji vytahuje jako karta a chová se jako další účastník.
- Platí pravidlo **limitu čtyř bytostí** v soubojovém kole.
- Ovládaná bytost si po přežití souboje léčí životy automaticky.
- Co dělá ovládaná bytost, určuje hráč, který ji drží.

## Duše (životy)

Duše reprezentují základní životní energii postavy. **Počet duší = maximální počet životů.** Duše přibývají při zvyšování úrovně. Některé dovednosti a předměty toto pravidlo mění.

| Úroveň | Duše (všechna povolání) |
|---------|------------------------|
| 0 | 10 |
| 1 | 10 |
| 2 | 15 |
| 3 | 20 |
| 4 | 25 |
| 5 | 30 |
