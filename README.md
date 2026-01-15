# Election Scraper

Tento program slouží k automatizovanému sběru dat a výsledků parlamentních voleb z roku 2017 z webového portálu [volby.cz](https://www.volby.cz/). Program extrahuje data pro libovolný zvolený okres a ukládá je do formátu CSV pro další zpracování.

## Popis projektu

Program na základě zadané URL adresy:
1. Identifikuje všechny obce v rámci daného územního celku.
2. Pro každou obec navštíví její detailní stránku a stáhne výsledky (voliče, obálky, platné hlasy).
3. Vyextrahuje počty hlasů pro jednotlivé kandidující politické strany.
4. Všechna získaná data sjednotí a uloží do souboru `.csv`.

## Požadavky

Projekt vyžaduje Python verze 3 a externí knihovny specifikované v souboru `requirements.txt`.

### Instalace potřebných knihoven

Před prvním spuštěním nainstalujte závislosti. V PowerShellu (pwsh) nebo jiném terminálu spusťte:

```powershell
pip install -r requirements.txt
```

## Spuštění programu

Program se spouští z příkazové řádky a vyžaduje dva povinné argumenty v tomto pořadí:

1. **URL** – odkaz na výsledky konkrétního územního celku (vždy v uvozovkách).
2. **Soubor** – název výstupního souboru s příponou `.csv`.

**Obecný formát spuštění:**

```powershell
python main.py <URL_ADRESA> <NAZEV_SOUBORU>
```

### Příklad spuštění (pro okres Prostějov)

V PowerShellu zadejte příkaz následovně:

```powershell
python main.py "[https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xnumnuts=7103](https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xnumnuts=7103)" "vysledky_prostejov.csv"
```

## Struktura výstupního CSV

Výsledný soubor používá jako oddělovač středník (`;`) a kódování `utf-8-sig`, aby byl okamžitě čitelný v aplikaci Excel. Sloupce obsahují:

- **code**: Identifikační kód obce.
- **location**: Název obce.
- **registered**: Počet registrovaných voličů.
- **envelopes**: Počet vydaných úředních obálek.
- **valid**: Počet odevzdaných platných hlasů.
- **[Názvy stran]**: Každá kandidující strana má svůj vlastní sloupec s počtem získaných hlasů.

---
**Autor:** Květoslav Leidorf
