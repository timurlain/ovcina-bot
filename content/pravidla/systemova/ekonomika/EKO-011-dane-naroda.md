---
id: EKO-011
název: Daně národa — královský výnos z hráčů a budov
úroveň: systémová
kategorie: [ekonomika, daně, příjem-krále, rozvoj]
stav: schváleno
viditelnost: obojí
závisí-na: [EKO-001, SIT-001, SIT-005, SIT-006]
nahrazuje: []
poslední-změna: 2026-04-30
klíčové-fráze:
  - jak fungují daně
  - kolik vybírá král
  - daně z hráčů
  - daně z budov
  - královský příjem
  - kolik dostává král
  - tabulka daní
---

# Daně národa

Každé herní období inkasuje král národa do **pokladny národa** dva typy daní:

## Daň z obyvatelstva (base tax)

Za každého hráče svého národa získá král **1 groš za období**.

- Počítají se všichni hráči startující s daným národem (včetně dětských kategorií).
- Daň reprezentuje obecný výnos z poddaných — počítá se i v období, kdy je hráč mimo město.

## Daň z budov

Za každou postavenou budovu na území národa získá král **1 groš za období**.

- Platí pro všechny budovy z _Ceníku budov_ (viz SIT-006) — produkční, divoká příroda, manufaktury, vojenské, magické, prestižní i ostatní.
- Daň pobírá národ, na jehož území budova stojí, bez ohledu na to, zda je majitelem budovy občan tohoto národa.
- Hráčské nemovitosti (Dům, Panství — SIT-008) se **započítávají do daně z budov stejně jako každá jiná budova**: 1 groš za období do královské pokladny. Mají navíc vlastní mechaniku nájmu (viz SIT-008), ta jde **majiteli**, ne králi.
- Vesnice samotná (jako lokace) se nepočítá jako budova; budovy postavené ve vesnici se počítají běžně.

## Specifika

- **Manufaktura:** Daň z budovy se u manufaktury strhává přímo z výplaty 4 + X majiteli — král dostává 1 groš, majitel 3 + X grošů (viz SIT-006).
- **Produkční budovy (Pila, Důl, Vinice, Statek):** Suroviny dále jdou králi a vlastníkům podle EKO-003. Daň 1 groš za období je nad rámec produkce surovin.
- **Cechovní dům:** Mění formuli manufaktury z 4 + X na 5 + X (viz SIT-006); daň 1 groš pro krále zůstává stejná.

## Únik z pokladny — krádež zlodějem

> ⚠️ **Skrytá mechanika** (organizátor-only — viz **ZLO-001**).

Zloděj může označit budovu nálepkou a vykrást ji prostřednictvím **zástupce zlodějské gildy (ZZG)**:

- Král **okamžitě odevzdá ZZG 20 grošů** (anonymně, bez jména zloděje).
- Pokud král 20 grošů nemá, **budova je nepoužitelná**, dokud se nevyplatí.
- ZZG vyplatí 20 g zloději (5 g si nechá za nálepku jako provizi).

**Dopad na rozpočet národa:** za období může být národ vykraden vícekrát (v praxi 1–2 úspěšné krádeže = realistický horní limit, viz ZLO-001 organizátorské poznámky). Při kalkulaci pokladny počítej s **rezervou cca 20–40 grošů** pro případ krádeže — výkyv je nezanedbatelný proti běžné dani 1 g / budova / období.

## Příklad

Národ Lidí má 12 hráčů a celkem 11 postavených budov (8 ve městě, 3 ve vesnici):

- Daň z obyvatelstva: 12 × 1 = **12 grošů za období**
- Daň z budov: 11 × 1 = **11 grošů za období**
- **Celkem do pokladny národa: 23 grošů za období**
