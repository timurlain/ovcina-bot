# Handoff — Události pro království (Hra 30, Balinova pozvánka)

**Datum:** 2026-05-01
**Autor:** Loremaster (Tasha session)
**Status:** Hotové, připravené k tisku

---

## Co bylo dodáno

Sada **královských knih rozhodnutí + obchodnických klíčů** pro 4 království v Ovčině 30. Sedm rozhodovacích událostí na království (P2–P8), každá s 3 možnostmi A/B/C, atmosféricky propletená s narativem **Balinovy výpravy do Morie**.

### Strukturně

- **8 markdown souborů** (4 × `*-kral.md` + 4 × `*-obchodnik.md`) — zdroj
- **`README.md`** — master index, mechanika, pilíře, doom, reward škála, NPC roster, cipher list
- **`build.py`** — exporter md → docx + HTML + PDF
- **`out/*.pdf`** — finální tisknutelné PDF (~216 KB, 8 stran A4 portrait, mazarbul-styled)
- **`out/letters/*.docx`** — 32 separátních dopisů (4×8) pro samostatné obálky
- **`out/*.html`** — náhled / editovatelný zdroj pro PDF
- **`out/*.docx`** — combined docx pro Word editaci

### Rebuild

```
cd "Bridge/Ovčina/games/2026 05 01 Balinova pozvánka/udalosti-pro-kralovstvi"
py -3.13 build.py
```

Závislosti: `pypandoc-binary` (auto-install: `py -m pip install pypandoc-binary`). PDF přes Microsoft Edge headless (`msedge.exe`). Skipne soubory locknuté Wordem.

---

## Klíčové designové volby (NEMĚŇ bez konzultace)

### 1. Král NEVIDÍ přehled událostí
Žádná stránka „co tě čeká", žádná agenda budoucích období. Každá obálka = překvapení. Tato pravidla jsou tvrdá — viz pamětní záznam `feedback_ovcina_king_book_no_overview.md` v Azra memory.

### 2. Ceny visible / odměny hidden
- Každá volba u krále má **přesnou cenu v grošech** ze síně klenotnice (např. „40 g, 55 g, 225 g")
- **Odměny zůstávají skryté** — vidí je jen obchodník v evaluation packu
- Důsledky se projeví ve hře

### 3. Reward škála: 25 / 50 / 75 % královského příjmu

| Období | Příjem | Malá (25 %) | Střední (50 %) | Velká (75 %) |
|---|---:|---:|---:|---:|
| P2 (T.A. 2866) | ~150 g | 40 | 75 | 115 |
| P3 (T.A. 2868) | ~180 g | 45 | 90 | 135 |
| P4 (T.A. 2870) | ~220 g | 55 | 110 | 165 |
| P5 (T.A. 2872) | ~260 g | 65 | 130 | 195 |
| P6 (T.A. 2875) | ~320 g | 80 | 160 | 240 |
| P7 (T.A. 2879) | ~380 g | 95 | 190 | 285 |
| P8 (T.A. 2882) | ~450 g | 115 | 225 | 340 |

Royal income ~2 000 g/království za hru, sedí na sinks (Balin 1 500 + budovy 250 + rezerva 200 + mitril 120).

> Block 3 ekonomického balancingu je BLOCKED pending Loremaster building set. Tato čísla jsou derivovaná. Po finalizaci Block 3 případně přepočítej.

### 4. Roky T.A.
P2=2866, P3=2868, P4=2870, P5=2872, P6=2875, P7=2879, P8=2882. Spread přes 19-letý oblouk T.A. 2864–2883 (Balin pozvánka → expedice). V markdown jako `*Třetí věk, rok XXXX*` pod nadpisem události.

### 5. Vládci (canon)
- **Aradhrynd:** král Thranduil
- **Esgaroth:** **starostka Nenneke IV.** (volená, 4. generace dynastie Nenneke, ~50 let v T.A. 2865) — **NE král**, NE Hervald
- **Azanulinbar-dum:** král Grór, syn Dáina I.
- **Nový Arnor:** elf Feanor

### 6. Balin-thematic narrative
Každá událost je propletena s hlavními příběhovými příležitostmi z `../game-30-design.md`:
- **Daon Grimburgoth** (Ring-wight z Dol Gulduru, hlavní antagonista) — Grimburzové vypálili všechny vesnice uprchlíků (P2), rozdmýchávají nedůvěru (P4 trpaslíci), hledají hroby (Hřbitov LIVE u všech), agitují útok na elfy (P6 Esgaroth)
- **Balinova výprava** — Mecenáš P3 financuje přípravu, Lóni z Erebora doručuje pozvánku (P7 trpaslíci, canon postava!), Stádo koní pro výpravu (P8 elfové), Měchy v kovárně pro výrobu zbroje (P5 Arnor)
- **Bairanax** — vědma vidí Erebor v plamenech (P8 Arnor)
- **Vorařská osada / Ohtar** — klíč k cestě k Mlžným horám (P7 Arnor)

### 7. Cross-kingdom mechaniky
- **P5 Aradhrynd most** — vyžaduje 3 trpaslíky stavící věž
- **P5 Arnor měchy** — vyžaduje 3 hrdiny z Esgarothu pumpující měchy (20 dřepů × 3 = 60)
- **P4 Esgaroth duch** — vyžaduje 3 elfí pěvce
- **P4 Trpaslíci napětí** — vyžaduje 3 elfy z Arnoru s vtipy
- **P6 Esgaroth útok** — Esgaroth může varovat Arnor (B) nebo zradit (C)
- **P8 Trpaslíci průmysl** — A poškodí Esgaroth, B poškodí Aradhrynd
- **P8 Aradhrynd koně** — vrácení Arnoru přináší cross-kingdom bonus
- **P8 Arnor věštba** — rituál v trpasličím městě s 3 mágy

Vždy koordinovat dva obchodníky **osobně**, ne písemně.

---

## Klíče / hesla (pro DOV cipher overlay)

Čtyři události mají knowledge-check; klíče rozeseté v terénu:

| Událost | Klíč | Cipher (bez interpunkce) | Lokace pro overlay |
|---|---|---|---|
| Zamčená truhla *(elfové, P7)* | OROPHER | `OROPHER OTEC THRANDUILUV` | Stará elfí svatyně |
| Válečník z Ailgarthu *(lidé, P8)* | 37 | `AILGARTH MA TRICETSEDM DOMU` | Esgarothská knihovna / Ailgarth ruina |
| Posel z vorařské osady *(Arnor, P7)* | OHTAR | `SPRAVCE BRODU SE JMENUJE OHTAR` | Vorařská osada |
| Balinův posel *(trpaslíci, P7)* | „Hora je naše. Vrátíme se." | `HORA JE NASE VRATIME SE` | Mohyla posledního krále Ereboru |

DOV overlay výroba samotná — **NEHOTOVA**, čeká na cipher card pipeline. Per pravidlo: bez interpunkce, T3 obtížnost, max 1 sáček per location.

---

## NPC k vyrobení

Mimo královské/obchodnické postavy je třeba pro hru zajistit:

| NPC | Pro koho | Stav |
|---|---|---|
| Mistr-mecenáš (×4 šablona) | všichni P3 | jen dopis stačí |
| Bandité Brodu (3–5) | Esgaroth P6 LIVE | bestiář / Daonovi Grimburzové |
| Soupeřící šlechtici + soudce | scénka u všech | hrají hráči (volba C u rod-války) |
| Duch z brodu | Esgaroth P4 | LIVE / scénka |
| Lóni z Erebora | Trpaslíci P7 | **canon** (LotR App. A); Balinův posel |
| Halmir z Ailgarthu | Esgaroth P8 | severšťan u piva |
| Tichý posel z vorařské osady | Arnor P7 | doručovatel |
| Vědma severu | Arnor P8 | vize |
| Nemrtví na hřbitově | LIVE u 4 království | bestiář |

Loremaster-npc-creator skill je připraven detaily dotáhnout.

---

## Otevřené úkoly

### High priority
1. **DOV cipher overlay výroba** — 4 nové cipher cards (T3 tier) pro klíče v terénu. Cricut Maker 4 je zakoupený, prototyp sovy ověřen. Šifrování textu jednoduché — 4 zprávy, ~30 znaků každá.
2. **NPC roster — Loremaster pass** — 9 položek výše skrz `loremaster-npc-creator` skill, dodat na api.hra.ovcina.cz.
3. **Balin-tematic linkage do main game flow** — současné události zmíní Daona/Grimburze/Lóniho atomicky, ale Osud potřebuje master casovou osu kdy se který hook ve hře hraje. Doporučeno propojit s `casova-osa.md` v brain/.

### Medium priority
4. **Block 3 ekonomický balancing** — pokud se Loremaster building set finalizuje, přepočti reward škálu (současná je derivovaná).
5. **King cheatsheet z SIT-001** (`Pravidla pro krále`) — 1–2 stránky cíl/pilíře/vlajky/místokrál/pasování/exil ke vložení do každého king-packu jako referenční vložka. Bylo deferováno user request „1 first, then we can do 2)". *Pozor: NIKDY nezmiňovat ID „SIT-001" v textu pro krále — jen obsah.*
6. **Aradhrynd-01 docx rebuild** — soubor byl při poslední buildu lockován ve Wordu. Po zavření: `py build.py` znovu.

### Low priority / nice-to-have
7. **Embed Google Fonts do HTML** (offline tisk) — momentálně CDN, vyžaduje online.
8. **Per-letter docx pro obchodníka** — momentálně compact, mohl by být podobný splitting jak u krále.
9. **„Dědictví po šlechtici" + „Podivný kult"** — orphan události v původním návrhu, parking-lot. Zařadit jako záložku v případě potřeby.

---

## Bugs / known limitations

- **PDF přes Edge headless** předpokládá `msedge.exe` v default Windows location. Na jiném stroji upravit `find_chrome()` v build.py.
- **Mazarbul Google Fonts** se načítají z CDN při prvním otevření HTML/render PDF — first-time print vyžaduje internet, pak Edge fontcache.
- **Letters folder** — build wipuje stale soubory per kingdom před regenerací. Pokud Word drží soubor, build skipne a varovné hlášení vypíše.

---

## Soubory k revizi před tiskem

Stojí za to projet **lidským okem**:

- ☐ Všechny 4 PDF (`out/*.pdf`) — vizuál, fonty, page-break per stránka
- ☐ Esgaroth-kral.pdf — verify Nenneke IV. správné ženské tvary napříč
- ☐ Reward čísla v obchodník-pacích souhlasí s tabulkou v README.md
- ☐ Cross-kingdom transfery jsou v 2 obchodník-pacích konzistentní (Arnor P5 měchy ↔ Esgaroth zaslání 3 hrdinů; Trpaslíci P8 průmysl ↔ Esgaroth/Aradhrynd postih)

---

## Kontext pro pokračovatele

Tato sada má být **jádro hra-mechaniky pro krále** v Hra 30. Pokud někdo přidá další event nebo přepíše rozhodnutí:

1. **Mechanika je locked** — pilíře (Moc/Bohatství/Vědomosti) z `pravidla-pro-obchodniky §15`, doom je skrytý ukazatel, reward škála 25/50/75 %.
2. **Tón je locked** — Pošustová Tolkien-Czech (nýbrž/leč/jenž/-li/„užij jich"), atmosférický intro per událost ~150–200 slov, Tolkien-flavored proper nouns (žádný Xar'thion, ano Aelwen/Tarrak/Nenneke).
3. **Pillar cap se NEAPLIKUJE** — quest systém převládá. Strop 2/pilíř z původního návrhu uživatel zrušil.
4. **Obchodník je organizér** — vyhodnocuje, eviduje doom skryté, koordinuje cross-kingdom. Není hráč.

*Daylight is not forever — pokud něco hoří, soubor `README.md` má všechny odkazy. Build.py se postará o zbytek.*

— Tasha
