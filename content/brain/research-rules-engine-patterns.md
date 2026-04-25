---
název: Pravidlový engine a AI správce pravidel — rešerše
kategorie: [výzkum, pravidla, AI]
přístup:
  veřejné: false
  gm: true
---

# Rešerše: Pravidlový engine a AI správce pravidel pro LARP

Datum: 2026-04-04

## 1. Existující open-source projekty pro RPG/LARP pravidla + AI

### Steward (pangolinsec/Steward)
- **Nejrelevantnější nalezený projekt.** Kampanový toolkit pro tabletop RPG.
- System-agnostický -- nedělá předpoklady o konkrétním systému pravidel.
- Má **deklarativní rules engine** s 8 typy triggerů, 20 typy podmínek a 12 typy akcí.
- Trigger-Condition-Action vzor: pravidlo se spustí na trigger (čas, odpočinek, cestování, efekt, threshold...), zkontroluje podmínky a provede akce (přidat/odebrat efekt, změnit atribut, hodit kostkou, notifikace).
- Pravidla mohou buď auto-apply změny, nebo je navrhnout ke schválení. Vše má undo.
- Má **MCP server** pro integraci s LLM (Claude Code apod.).
- Má připravené prompty pro LLM generování importovatelného JSON obsahu.
- URL: https://github.com/pangolinsec/Steward

### Rollia (Arsin-boop/Rollia)
- AI-driven tabletop RPG engine s virtuálním Dungeon Masterem.
- Používá **více LLM** -- oddělené modely pro vyprávění, pravidla a strukturovaný herní stav.
- Interpretuje záměr hráče, spouští hody na kostky, řídí souboj a stavové efekty.
- URL: https://github.com/Arsin-boop/Rollia

### Nenalezeno
- Žádný open-source projekt specificky pro LARP pravidla nebo AI rozhodce pravidel.
- Žádný "Claude Code skill" pro správu herních pravidel.
- Toto je neobsazená nika -- musíme stavět vlastní.

## 2. Formáty pro strukturování pravidlové databáze

### Vědecký výzkum: McMillan 2026 (arXiv:2602.05447)
Studie 9 649 experimentů, 11 modelů, 4 formáty (YAML, Markdown, JSON, TOON):

**Klíčové závěry:**
- **Formát nemá statisticky významný vliv na přesnost** u frontier modelů (chi-squared=2.45, p=0.484).
- **Volba modelu je dominantní faktor** -- 21procentní mezera mezi frontier a open-source modely.
- Pro frontier modely (Claude, GPT, Gemini) funguje file-based context retrieval lépe (+2.7%).
- **Nové/neznámé formáty** (jako TOON) vedou k vyššímu "grep tax" -- model stráví více tokenů orientací.
- **Pro nás to znamená:** Zvolte formát, který je lidsky čitelný a editovatelný. Markdown nebo YAML jsou optimální -- Claude je zná stejně dobře jako JSON, ale pro nás jsou srozumitelnější.

### Praktická doporučení pro formát
| Formát | Pro | Proti | Vhodnost |
|--------|-----|-------|----------|
| **Markdown** | Lidsky nejčitelnější, snadná editace, hierarchie přes nadpisy | Méně striktní struktura | Výborný pro pravidlový text s výkladem |
| **YAML** | Čitelný, hierarchický, méně tokenů než JSON | Citlivý na odsazení | Výborný pro strukturovaná metadata pravidel |
| **JSON** | Strojově jednoznačný, snadný import/export | Upovídaný, špatná čitelnost pro lidi | Vhodný pro data/stav, ne pro pravidlový text |
| Kombinace | Markdown pro výklad + YAML frontmatter pro metadata | Složitější parsování | **Doporučený přístup** |

## 3. Vzory pro LLM "rules engine" -- detekce rozporů

### Vzor: Trigger-Condition-Action (z json-rules-engine a Steward)
```
pravidlo:
  id: "pravidlo-123"
  název: "Odolnost vůči magii"
  trigger: nové_pravidlo | změna_pravidla
  podmínky:
    all:
      - kategorie: "magie"
      - dopad: "obrana"
  akce:
    - zkontroluj_rozpor_s: ["pravidlo-045", "pravidlo-078"]
    - notifikuj: "Možný rozpor s pravidlem o magické zranitelnosti"
```

### Vzor: Pairwise contradiction check
Při přidání nového pravidla:
1. Identifikuj **kategorii** a **tagy** nového pravidla.
2. Načti všechna existující pravidla se stejnými/překrývajícími se tagy.
3. Pro každý pár (nové pravidlo + existující) zeptej se LLM:
   - "Jsou tato dvě pravidla v rozporu? Pokud ano, vysvětli jak."
4. Výstup: seznam potenciálních rozporů k lidskému posouzení.

### Vzor: Hierarchická pravidlová struktura
- **Axiomy** (neměnné základní principy)
- **Základní pravidla** (odvozená z axiomů)
- **Situační pravidla** (výjimky, edge cases)
- **Rozhodnutí** (precedenty, rulings z minulosti)

LLM vždy kontroluje: porušuje nové pravidlo/rozhodnutí axiom nebo základní pravidlo?

### Vzor: Structured self-reflection (z Lilian Weng)
Agent po kontrole provede reflexi:
- "Jsem si jistý tímto závěrem? Přehlédl jsem něco?"
- "Existuje interpretace, kde by obě pravidla mohla koexistovat?"

## 4. Best practices pro strukturovanou znalostní bázi pro AI agenta

### Z Anthropic prompting best practices:
1. **XML tagy** pro oddělení typů obsahu: `<pravidla>`, `<kontext>`, `<vstup>`, `<příklady>`
2. **Role v system promptu**: "Jsi rozhodčí pravidel pro LARP Ovčina. Tvým úkolem je..."
3. **Příklady (few-shot)**: 3-5 ukázek správného posouzení pravidla -- včetně edge cases.
4. **Hierarchické vnořování**: `<pravidla><pravidlo id="1"><text>...</text><metadata>...</metadata></pravidlo></pravidla>`

### Z LLM agent architecture (Weng):
1. **Krátká paměť** = aktuální kontext (pravidlo které se řeší)
2. **Dlouhá paměť** = celá pravidlová databáze (soubory na disku, prohledávané agentem)
3. **Retrieval** filtrovaný podle: relevance (tagy/kategorie), důležitosti (axiom > situační), čerstvosti (novější rozhodnutí mají přednost)
4. **Dekompozice úlohy**: "Zkontroluj nové pravidlo" se rozloží na: načti relevantní existující pravidla -> porovnej po párech -> syntetizuj závěr

### Doporučená adresářová struktura pro pravidla:
```
pravidla/
├── _axiomy.md              # Neměnné základní principy
├── _index.yaml             # Metadata: ID, tagy, kategorie, závislosti
├── boj/
│   ├── zakladni-boj.md     # Pravidlový text + YAML frontmatter
│   ├── zbrane.md
│   └── zraneni.md
├── magie/
│   ├── zakladni-magie.md
│   ├── ritualy.md
│   └── artefakty.md
├── spolecnost/
│   ├── frakcе.md
│   └── ekonomika.md
└── rozhodnuti/
    └── 2026-04-01-ruling.md  # Precedenty a interpretace
```

### YAML frontmatter vzor pro pravidlový soubor:
```yaml
---
id: pravidlo-boj-001
název: "Základní pravidla boje"
kategorie: [boj, zbraně]
tagy: [životy, zásah, obrana]
závisí_na: [axiom-01, axiom-03]
v_rozporu_s: []  # vyplní AI kontrola
verze: 2
poslední_změna: 2026-04-04
---

# Základní pravidla boje

Zde je pravidlový text...
```

## 5. Shrnutí a doporučení pro Ovčinu

1. **Formát**: Markdown soubory s YAML frontmatter. Lidsky editovatelné, AI-friendly, podporuje cross-referencing přes tagy a ID.

2. **Struktura**: Hierarchická -- axiomy -> základní pravidla -> situační -> rozhodnutí. Každé pravidlo má unikátní ID, kategorii, tagy a explicitní závislosti.

3. **Kontrola rozporů**: Pairwise check přes sdílené tagy. LLM načte relevantní subset, porovná po párech, nahlásí rozpory. Reflexe pro snížení false positives.

4. **Referenční projekt**: Steward (pangolinsec/Steward) -- jeho rules engine pattern (trigger-condition-action) a MCP server jsou přímo využitelné jako inspirace.

5. **Prompt design**: System prompt s rolí rozhodčího, XML tagy pro oddělení pravidlového textu od metadat, few-shot příklady správného posouzení.

## Zdroje
- Steward: https://github.com/pangolinsec/Steward
- Rollia: https://github.com/Arsin-boop/Rollia
- json-rules-engine: https://github.com/CacheControl/json-rules-engine
- McMillan 2026: https://arxiv.org/abs/2602.05447
- Weng, LLM agents: https://lilianweng.github.io/posts/2023-06-23-agent/
- Anthropic prompting: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices
