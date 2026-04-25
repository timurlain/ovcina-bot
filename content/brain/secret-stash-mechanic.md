---
název: Tajná skrýš — herní mechanika
kategorie: [mechaniky, skrýše]
přístup:
  veřejné: false
  gm: true
---

# Tajná skrýš (Secret Stash) — Herní mechanika

## Koncept

Tajná skrýš je sub-lokace — skrytý bod zájmu uvnitř existující lokace. Lokace jsou relativně stálé (hráči, kteří už hru znají, vědí kde jsou), ale tajné skrýše se mění s každým ročníkem. Tím se vytváří nová vrstva průzkumu i pro zkušené hráče.

## Jak to funguje

1. Každá lokace může mít 0–3 tajné skrýše v daném ročníku.
2. Tajná skrýš má **název** (např. "Převrácený vůz"), **fantasy ilustraci** a krátký **popis**.
3. Poklady se přiřazují k tajným skrýším, nikoliv přímo k lokacím.
4. Název tajné skrýše je v rámci jednoho ročníku **unikátní** — žádné dvě skrýše nemají stejný název.

## Průběh hry

- Hráč získá vodítko (z questu, od NPC, z nalezené zprávy): *"Poklad najdeš pod převráceným vozem."*
- Vodítko obsahuje **název** tajné skrýše a její **fantasy ilustraci**.
- Hráč neví, na které lokaci se skrýš nachází — musí:
  - Prozkoumávat lokace a fyzicky ji najít
  - Obchodovat s informacemi s ostatními hráči
  - Zapamatovat si ji / zapsat si ji pro budoucí použití
- Protože se skrýše mění každý ročník, znalost z minulého roku nepomůže.

## Příprava (pro organizátory)

- Ilustrace slouží jako fantasy obrázek — ukazuje, jak skrýš vypadá v herním světě (ne fotka rekvizity).
- Organizátoři na lokaci umístí rekvizitu nebo vizuální značku odpovídající popisu.
- Při přípravě ročníku je potřeba:
  - Vymyslet a pojmenovat tajné skrýše pro každou lokaci
  - Připravit fantasy ilustrace
  - Vyrobit/sehnat odpovídající rekvizity
  - Přiřadit poklady k jednotlivým skrýším

## Doménový model

```
SecretStash
├── Id (int, PK)
├── Name (string, unique per Game)
├── Description (string?)
├── ImageUrl (string?)
├── LocationId (int, FK → Location)
└── GameId (int, FK → Game)
```

Poklady (TreasurePlacement) se váží na SecretStash, ne na Location.
