# Handoff — Lokace pro 30. ročník Ovčiny (Balinova pozvánka)

> Aktualizováno 2026-04-10. Pokračování práce na lokacích.

## Stav práce

### Hotovo
- Prošli jsme 12+ ICE a TOR zdrojových knih a extrahovali všechny lokace Rhovanionu
- Vybrali 77 lokací na hlavní mapu + 7 Moria lokací jako separátní finále
- Rozdělení: 4 hráčská království, 15 kolonizovatelných vesnic, 10 magických, 22 divočina (vč. NPC měst Dol + Scestov), 8 dungeonů, 2 hobití, 16 ostatních (draky, sever, východ, puzzle)
- 15 lokací dostalo vrstvené popisy (povrch/quest/hluboko) s provázanou questovou sítí
- Odmítnuté lokace uloženy zvlášť
- **Lokace rozsekaný do jednotlivých souborů** v `lokace/` (81 souborů + `index.md`)
- **„Dva bratři" (Pravdomluvný a Lhář) odstraněna** — není v indexu ani jako soubor
- **Přidána nová lokace #81 Ostrov Tol Narthad** — bývalý úkryt Bairanaxe na moři Rhûn (v indexu i jako soubor)
- **Tajné skrýše pročištěny a připraveny ke generování** → `tajne-skryse.md` (193 skrýší pro 74 lokací, bez měst #1–#4)
  - 48 existujících skrýší ⭐ přiřazeno, 145 nových vytvořeno
  - 9 duplicitních názvů opraveno (přejmenováno s novými popisy)
  - 3 nefyzické skrýše nahrazeny (Svítící lahvička→Ptačí budka, Bludný ohýnek→Dutý rákos, Přízračná záře→Kamenná maska)
  - Lanový uzel nahrazen Vyřezávaným obličejem (vizuálně výraznější)
  - Moria (19 skrýší) vyčleněna do `tajne-skryse-moria.md`
  - Každá skrýš má sekvenční ID [1]–[193] pro import do DB
  - Prompty: storybook illustration styl (od [37]), bílé pozadí, bez lokačního kontextu, jasné pro děti
  - Prompty formátovány jako code block pro snadné kopírování
  - Skrýše jsou unikátní v rámci ročníku, přenositelné mezi lokacemi

### Rozpracováno — kde jsme skončili
- **Grilování jednotlivých lokací** zatím neproběhlo (0/15 hotovo)
- První lokace k probrání: **Tichá zahrada (#24)** — otázky jsou položené, uživatel ještě neodpověděl
- Otázky ke grilování (z minulé session):
  1. Fyzická realizace v terénu
  2. NPC přítomnost
  3. Quest itemy — odkud, jaká odměna
  4. Entky (deep quest) — kdo nese poselství od entů, co entky odpovědí
  5. Propojení na questovou síť

### Co zbývá
- Progrilovat vylepšených 15 lokací (zatím 0/15 hotovo)
- Zvážit vrstvení pro další lokace kde to dává smysl
- Zapsat závěry z grilování do Loremaster knowledge-base: `.skills/ovcina-loremaster/knowledge-base/`
- Navrhnout provázanost questů mezi všemi lokacemi
- Připravit popisy pro hráče (krátké) a pro CP (detailní)
- ~~**Tajné skrýše pročistit**~~ — HOTOVO (2026-04-10)
- **Vygenerovat Midjourney kartičky** — prompty jsou připravené v `tajne-skryse.md`, stačí kopírovat z code bloků

## Klíčové soubory

| Soubor | Co obsahuje |
|---|---|
| `games/2026 05 01 Balinova pozvánka/potencialni-lokace.md` | **Master soubor** — 77 finálních lokací se strukturou a popisy (starší číslování) |
| `games/2026 05 01 Balinova pozvánka/lokace/` | **Jednotlivé soubory** — 81 lokací + 7 Moria + `index.md` (autoritativní číslování) |
| `games/2026 05 01 Balinova pozvánka/lokace/index.md` | **Index** — přehled všech lokací s odkazy na soubory |
| `games/2026 05 01 Balinova pozvánka/tajne-skryse.md` | **Tajné skrýše** — 205 skrýší s popisy a MJ prompty |
| `games/2026 05 01 Balinova pozvánka/odmitnute-lokace.md` | Odmítnuté lokace s důvody |
| `games/2026 05 01 Balinova pozvánka/handoff-lokace.md` | Tento handoff |
| `.skills/ovcina-loremaster/knowledge-base/` | Loremaster knowledge — sem se zapisují závěry z grilování |
| `brain/prompt-secret-stash-creator.md` | Prompt pro tvorbu tajných skrýší |

## Důležitá rozhodnutí uživatele

- **Beorn = Medděd** (český herní název)
- **Strayhold = Scestov** (český herní název)
- Dol a Scestov nejsou města ale divočinové/NPC lokace — jen 4 hráčská království jsou "města"
- Moria je separátní finále, nepočítá se do 77
- Úrodná pole (prázdné sloty) vyřazena — každá vesnice musí mít příběh
- Vílí palouček zůstává místo Muchomůrkového kruhu
- Leardinothova věž vyměněna za Prokletý trpasličí dům
- Nory ledových draků vyměněny za Norr-dum + Gondmaeglom
- Isildurovo pole + Pole hrdinů sloučeny do Pole padlých králů
- Vrstvený přístup k lokacím (povrch/quest/hluboko) se uživateli velmi líbí
- Lokace se propojují questovou sítí (Golemův klíč přes 3 lokace, meč z Mohyl pro Jeskyni bledého jezdce, atd.)
- Česky vždy s háčky a čárkami, žádné zkracování
- **Dva bratři (Pravdomluvný a Lhář) odstraněni** z finálního seznamu
- **Ostrov Tol Narthad (#81) přidán** — bývalý úkryt Bairanaxe na moři Rhûn
- **Tajné skrýše**: 2–3 na lokaci, zajímavá místa mimo civilizaci více. Města (#1–#4) bez skrýší. Dol a Scestov mají skrýše.
- **Midjourney V7**: oil painting, Tolkien-inspired, warm earthy palette, golden hour light, suitable for children --ar 3:4 --s 200
- **Skrýše česky** — unikátní názvy, správná gramatika

## Questová síť (zjištěná propojení)

- **Golemův klíč** (3 části): Kobka starého krále + Lesní knihovna + Ostrov čarodějnice → Golém
- **Meč Vidugaviův**: Dlouhé mohyly → (svolení od) Tvrz Vidugavia → zraní přízrak v Jeskyni bledého jezdce
- **Kamenný kruh**: rituál potřebný pro Síň přízraků + Jeskyni bledého jezdce
- **Tumon-Gabil dokumenty**: instrukce k Golemovi + slabiny Dol Gulduru
- **Skaurilovy jeskyně → Khamûl → Dol Guldur**: hlavní příběhová linie
- **Srdce hvozdu**: Nekromant ho otravuje, záchrana = záchrana celého hvozdu
- **Tichá zahrada → entky**: poselství od entů z Fangornu jako deep quest
- **Osvětlená mýtina**: elfí rituál drží hvozd naživu
- **Vlčí rokle**: vlkodlak = prokletý člověk Waldhere, prokletí lze zlomit

## Prompt pro pokračování

> Pokračujeme v práci na lokacích pro 30. ročník Ovčiny (Balinova pozvánka). Přečti si handoff v `games/2026 05 01 Balinova pozvánka/handoff-lokace.md`. Skončili jsme u tajných skrýší (hotovo, 205 skrýší v `tajne-skryse.md`). Dalším krokem je buď: (a) grilování lokací — začínáme Tichou zahradou (#24), nebo (b) pročištění tajných skrýší. Mluv česky, piš s háčky a čárkami.
