# Prompt pro Claude Design — pravidla.ovcina.cz

Tohle je zadání pro statickou HTML stránku s pravidly Ovčiny LARP pro děti 10–11 let. Hostuje se jako `pravidla.ovcina.cz`.

**Tahle stránka je sestrou** dvou už hotových aplikací — **OvčinaHra** (`hra.ovcina.cz`, Blazor WASM) a **Registrace Ovčina** (`registrace.ovcina.cz`, Blazor Server). Sdílí jejich vizuální DNA: stejné fonty, stejnou paletu, stejnou strukturu hlavičky a patičky. Liší se obsahem (pravidla pro děti místo administrativy) a má vlastní interaktivní prvky.

**Hoď do Claude Design tento soubor + soubor `pravidla-pro-hrdiny-2026.md` jako zdroj textu.**

---

## Co potřebuju

**Jeden statický HTML soubor** plus volitelně `style.css` a `script.js`. Ke hostování jako `pravidla.ovcina.cz`. **Žádný framework** (ne Blazor, ne React, ne Bootstrap, ne Tailwind). Vanilla HTML + CSS + minimální vanilla JS. Otevřu to ve Wordu/Notepadu a vidím dovnitř.

## Zdroj textu

Použij obsah souboru `pravidla-pro-hrdiny-2026.md` **doslova** jako text. Neupravuj formulace — to je naše kanonická česká verze pro děti.

V markdownu jsou HTML komentáře `<!-- IMAGE: ... -->`, `<!-- INTERACTIVE: ... -->` a `<!-- HEADER: ... -->`, které říkají, kam patří obrázky a interaktivní prvky.

---

## Sdílená DNA (musí být stejné jako sister apps)

### Fonty

Načti z Google Fonts (preconnect + stylesheet, stejně jako sister apps):

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Merriweather:wght@400;700;900&display=swap" rel="stylesheet" />
```

Použití:
- `--font-heading: 'Merriweather', 'Georgia', serif` — všechny nadpisy, brand link, table headers, accent numbers
- `--font-body: 'Inter', 'Segoe UI', sans-serif` — body text, navigace, formuláře
- `--font-mono: 'JetBrains Mono', 'Consolas', monospace` — kód, čísla v tabulkách, klávesové zkratky

### Paleta — pergamen + tmavě hnědá + cihlová

Tohle jsou **přesně** custom properties z `registrace-ovcina-cz/wwwroot/app.css` — kopíruj 1:1:

```css
:root {
  /* Core palette */
  --color-text-primary: #2C1810;       /* dark warm brown — body text */
  --color-text-secondary: #8B4513;     /* saddle brown — labels, secondary */
  --color-accent: #B22222;             /* firebrick red — primary actions, links */
  --color-border: #D4C4B0;             /* light parchment border */
  --color-surface: #FFF8F0;            /* parchment background */
  --color-surface-alt: #F5EDE3;        /* slightly darker parchment — page bg */
  --color-header: #3C2415;             /* dark brown — header & footer bg */
  --color-header-text: #FFF8F0;        /* parchment on dark */
  --color-card-border: #B26223;        /* warm brown — card accents, borders */

  /* Typography */
  --font-heading: 'Merriweather', 'Georgia', serif;
  --font-body: 'Inter', 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Consolas', monospace;

  /* Spacing & radius */
  --radius-card: 8px;
  --radius-button: 6px;
  --shadow-card: 0 2px 8px rgba(44, 24, 16, 0.12);
  --shadow-elevated: 0 4px 16px rgba(44, 24, 16, 0.18);
}

html, body {
  background: var(--color-surface-alt);
  color: var(--color-text-primary);
}
body { font-family: var(--font-body); font-size: 1rem; line-height: 1.6; }
h1, h2, h3, h4, h5, h6 { font-family: var(--font-heading); font-weight: 700; line-height: 1.3; }
h1 { font-size: 2rem; } h2 { font-size: 1.625rem; } h3 { font-size: 1.325rem; }
a { color: var(--color-accent); text-decoration: none; }
a:hover { color: #8B1A1A; text-decoration: underline; }
code, pre { font-family: var(--font-mono); }
```

### Kingdom seal palette (KANONICKÁ, **použij tyhle**, ne ty z registrace)

Sister apps mají generic kingdom palette, ale pro Ovčina LARP je **kanonická** (manželkou schválená 2026-04-22) muted heritage paleta:

```css
--seal-esgaroth:    #242F3D;  /* dark blue-gray — Esgaroth */
--seal-aradhrynd:   #243525;  /* dark forest green — Aradhrynd */
--seal-azanulinbar: #8C2423;  /* deep red — Azanulinbar */
--seal-arnor:       #504B25;  /* olive — Arnor */
```

NEPŘESYŤUJ je — jsou záměrně tlumené. Použij v dekorativní pásce v hlavičce a u kingdom tagů, kdykoliv se v textu zmiňují.

### Hlavička (header) — sticky top

Sister apps mají tenhle pattern. Sleduj ho:

- **Background:** `var(--color-header)` (#3C2415), spodní okraj 3px solid `var(--color-card-border)` (#B26223).
- **Sticky-top:** zůstane nahoře při scrollu.
- **Container:** flexbox, padding ~12px svisle.
- **Brand link:** `Merriweather 900, 1.4rem, letter-spacing: 0.02em`, parchment barva `#FFF8F0`, bez podtržení. Text: **„Bojová pravidla pro Hrdiny"**.
- **Sub-text** pod brandem (mobile: hidden): „Ovčina LARP · ročník 2026" v `#C4A882, 0.85rem`.
- **Kingdom seal band:** pod hlavičkou tenký dekorativní pruh se 4 muted kingdom barvami (3px výška by mělo stačit), nebo vsazen do hlavičky vpravo.
- **Žádná navigace** v hlavičce (single page) — místo toho odkaz „Zpět nahoru" plovoucí v rohu.

### Patička (footer)

- Stejné `--color-header` pozadí, top border 3px `--color-card-border`.
- Text v `#C4A882`, font-size 0.85rem.
- Obsah: „© 2026 Ovčina LARP · v1.0 · Vychází z kanonických pravidel" + odkaz „Plné znění pravidel" (na rulemaster repo nebo placeholder).

### Karty / panely (sdílený pattern)

Sister apps používají dva typy karet, převezmi je:

```css
/* Standard parchment card */
.card-parchment {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
}

/* Accent card with top stripe */
.card-parchment-accent {
  background: var(--color-surface);
  border: 1px solid var(--color-card-border);
  border-top: 3px solid var(--color-card-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
}

/* Info panel — for "Drozd radí" callouts */
.info-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-text-secondary);
  border-radius: var(--radius-card);
  padding: 1.25rem;
  box-shadow: var(--shadow-card);
}
```

### Tabulky (table-warm)

Pravidla jsou tabulkově hutná — tabulky používej hodně. Pattern z registrace:

```css
.table-warm thead th {
  background: var(--color-header);
  color: var(--color-header-text);
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.75rem;
  border-bottom: 2px solid var(--color-card-border);
}
.table-warm tbody td { padding: 0.65rem 0.75rem; vertical-align: middle; }
.table-warm tbody tr:nth-child(even) { background: var(--color-surface-alt); }
.table-warm tbody tr:hover { background: #EDE4D8; }
```

### Tlačítka

```css
.btn-primary {
  background: var(--color-accent);
  border: 1px solid var(--color-accent);
  color: #fff;
  font-weight: 600;
  border-radius: var(--radius-button);
  padding: 0.5rem 1.25rem;
}
.btn-primary:hover { background: #8B1A1A; box-shadow: 0 2px 8px rgba(178,34,34,0.25); }
```

---

## Co tuhle stránku odlišuje (vlastní distinctní vrstva)

### 1. Drozd jako vypravěč

Drozd = drozd v kartografově klobouku s notesem, maskot OvčinaHry. **Není to jen avatar — je to průvodce skrz celou stránku.**

- **V hlavičce:** malý Drozd avatar vpravo nebo ve spodní části kingdom seal pásky.
- **U každého blockquote začínajícího `> **Drozd radí:**`** zobraz speciální „Drozd callout" s malým Drozdem nalevo a obsahem napravo. Použij `.info-panel` styl + Drozd avatar.
- **Drozd SVG:** v repech ho zatím nemáš zachycenou jako master assert (existuje `DrozdWelcome.razor` komponenta v některých worktrees ovcinahry, ale není canonical). **Nakresli si jednoduchý SVG drozda** — drozd hrdo nesoucí lupu nebo notes, v style line art s teplou hnědou výplní (#B26223 + #3C2415). Odvahy, nebýt přesný — ať to vypadá jako maskot.

### 2. Kostka — povinný interaktivní prvek

V kapitole **„Útok a obrana"** najdeš `<!-- INTERACTIVE: dice roller -->`. Implementuj:

- Velké tlačítko **„Hoď kostkou!"** (`.btn-primary`).
- Animovaná **d6** (CSS transform, ~1.5 s rotation; na konci ukáže výslednou hodnotu).
- **Exploding sixes:** padne-li 6, hází se znova a přičítá. Opakuj dokud padá 6. Ukaž běžící součet: „Hod: 6 + 6 + 3 = **15**".
- Pod tím dvě číselná pole: **ÚČ** (default 5) a **OČ** (default 3).
- Živý vzorec: `poškození = ÚČ + hod − OČ = ?`. Aktualizuj při změně.
- Tlačítko **Reset**.
- Respektuj `prefers-reduced-motion` — bez animací když uživatel nechce.

### 3. Počitadlo many — bonus interaktivní prvek (jen pokud snadné)

V kapitole **„Magie"** je `<!-- INTERACTIVE: animated mana counter -->`. Implementuj jen pokud nezdrží:

- 9 zelených kroužků (`var(--seal-aradhrynd)`) na vodorovné liště — karabinka.
- Tlačítka „Sešli kouzlo I (1 mana)", „II (2)", „III (3)" — odsouvají kroužky do odhazovací hromádky pod lištou.
- Tlačítko **Koncentrace** — vrátí 5 kroužků zpět.
- Tlačítko **Konec souboje** — vrátí všechny kroužky zpět.
- Disable spell tlačítka, když není dost many.

### 4. Pohyb na webu

- **Fade-in sekcí** při scrollu (Intersection Observer, opacity 0 → 1, ~400ms).
- **Smooth scroll** pro odkazy z TOC.
- **Sticky TOC** vlevo na desktop, sliding panel na mobile.
- **Žádné flip-cards, žádné parallax** — ať je to lehké.

### 5. Obrázky — primárně z lokální složky `games/karticky/`

Karty (zbraně, mince, předměty, budovy) jsou v `Ovčina/games/karticky/` rozdělené po typech:

```
games/karticky/
  zbrane/zbrane/tiff/   ← dyka.tif, kratky mec.tif, dlouhy mec.tif, bastard.tif,
                          hul.tif, stit.tif, velky stit.tif, valecna sekera.tif,
                          oboubrita sekera.tif, musketa.tif, remdich.tif, ...
  predmety/             ← zlato.tif, stribro.tif, drahokamy.jpg, duse.tif,
                          zakladni utok.tif, zakladni obrana.tif, krystaly.tif,
                          byliny.tif, povoz.tif, nahrdelnik.tif, sip.tif, ...
  budovy/               ← stavby (pro rules nepotřebné)
```

**Formát = TIFF (jeden JPG)** → web tohle neumí. **Build krok:**

1. Pro každou kartu, kterou používáš na webu, převeď `.tif` → `.webp` (kvalita ~85, max width 400px). Použij ImageMagick nebo `pillow` v Pythonu:
   ```python
   from PIL import Image
   img = Image.open("games/karticky/zbrane/zbrane/tiff/dyka.tif")
   img.thumbnail((400, 600))
   img.save("assets/cards/dyka.webp", "WEBP", quality=85)
   ```
2. Ulož všechny použité karty do `assets/cards/<type>/<slug>.webp`.
3. Web pak referencuje lokální `assets/cards/zbrane/dyka.webp` — žádný API call za běhu.

**Doporučené karty pro tabulky v textu:**

- **Startovní výbava (kapitola Tvoje postava):** `zbrane/dyka.tif` (sada C), `zbrane/kratky mec.tif` (sada A demo), `zbrane/luk` (sada B demo, pokud existuje), `predmety/zlato.tif` nebo `predmety/stribro.tif` (sada D)
- **Útok a obrana → Vybavení v souboji:** `zbrane/dlouhy mec.tif`, `zbrane/stit.tif`, `predmety/nahrdelnik.tif`
- **Povolání tabulky:** vedle každého povolání jednu typickou zbraň jako thumbnail vlevo (Válečník: bastard.tif, Střelec: luk pokud je / sip.tif, Zloděj: dyka.tif, Mág: hul.tif)
- **Životy a léčení:** `predmety/duse.tif`
- **Magie → Mana:** `predmety/krystaly.tif`
- **Lektvary:** ikona lahvičky pokud v karticky/predmety je, jinak SVG

**Žádné karty povolání** — neexistují, nevyrábějc fake. U povolání použij hlavně tu zbraň jako vizuální anchor, nebo siluetu v `var(--color-card-border)`.

### 6. Doplňkové obrázky z API (jen pokud třeba)

Pro to, co v `karticky/` není (monstra, lokace, pečetě království):

```bash
curl -X POST https://api.hra.ovcina.cz/api/auth/service-token \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"rulemaster","secret":"OvcinaSkills2026!ServiceAccess"}'
```

- **Hero band — pečetě království:** pokud v API existuje obrázek pečetě, stáhni; jinak **nakresli SVG kruhové pečetě** v muted barvě (Esgaroth `#242F3D` modrá, Aradhrynd `#243525` zelená, Azanulinbar `#8C2423` červená, Arnor `#504B25` olivová).
- **Příšery k příkladu souboje (vlk, skřet, troll):** `/api/monsters` pokud máš.

V buildu vše do `assets/img/`. Optimalizuj na ~80 KB každý.

---

## Struktura stránky

1. **`<header>` sticky** — brand link, kingdom seal band, malý Drozd v rohu
2. **`<aside>` TOC** — sticky vlevo, na mobile collapsible
3. **`<main>`** — chapter sekce, generózní whitespace
   - Každá kapitola = `<section>` s `<h2>` a anchor ID
   - Drozd callouts jako `.info-panel` s avatarem
   - Tabulky `.table-warm`
   - Interactive bloky (kostka, mana counter)
4. **„Zpět nahoru" plovoucí tlačítko** vpravo dole, objeví se po prvním scrollu
5. **`<footer>`** — copyright, verze, odkaz na canonical pravidla

## Technické

- **Single HTML** preferred, max plus `style.css` + `script.js`.
- **Žádné frameworks.** Vanilla.
- **Responsive:** mobile-first (320px → tablet 768px → desktop 1024px).
- **Accessibility:** semantic HTML, ARIA kde třeba, keyboard-navigable kostka, respektuj `prefers-reduced-motion`.
- **Performance:** pod 200 KB bez obrázků, fast on slow Wi-Fi.
- **UTF-8.** Diakritika všude.
- **Žádné cookies, žádný analytics, žádný komentářový systém.**

## Výstup

Jeden HTML soubor (nebo HTML + minimální `assets/` složka), připravený k nahrání jako `pravidla.ovcina.cz`. Žádné instalace, žádný `npm install`, jen otevři a zobraz.

---

## Souhrn vizuální identity

> **Pergamen + tmavě hnědá hlavička + cihlově červený akcent. Merriweather pro nadpisy, Inter pro tělo. 8px karty, 6px tlačítka. Sticky hlavička s brandem v Merriweather 900. Karty s 4px barevným okrajem vlevo. Tabulky s tmavou hlavičkou v capitálkách. Muted kingdom seals jako jediné výrazné barvy. Drozd jako maskot v každém callout boxu. Kostka jako jediný „wow" interaktivní prvek. Ne víc.**

Když je v pochybnostech, vyber **jednodušší** řešení.
