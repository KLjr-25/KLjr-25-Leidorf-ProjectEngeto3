# Election Scraper

Tento program slouží k automatizovanému sběru dat (scrapování) výsledků parlamentních voleb z roku 2017 z webového portálu [volby.cz](https://www.volby.cz/). Program extrahuje data pro libovolný okres a ukládá je do formátu CSV pro další analýzu.

## Popis projektu

Program na základě zadaného URL odkazu (pro konkrétní okres):
1. Projde hlavní tabulku a identifikuje všechny obce.
2. Pro každou obec navštíví její detailní stránku.
3. Vyextrahuje počty registrovaných voličů, vydaných obálek, platných hlasů a počty hlasů pro jednotlivé politické kandidující strany.
4. Výsledná data uloží do přehledného souboru `.csv`.

## Požadavky

Projekt vyžaduje Python verze 3 a externí knihovny specifikované v souboru `requirements.txt`.

### Instalace potřebných knihoven

Před prvním spuštěním nainstaluj závislosti. V **PowerShellu** (pwsh) nebo jiném terminálu spusť příkaz:

```powershell
pip install -r requirements.txt

## Spuštění programu

Program se spouští z příkazové řádky (PowerShell, Terminál) a vyžaduje dva argumenty zadané v následujícím pořadí:

| Argument | Popis | Příklad |
| :--- | :--- | :--- |
| **URL** | Odkaz na výsledky konkrétního územního celku | `"https://www.volby.cz/..."` |
| **Soubor** | Název výsledného souboru s příponou .csv | `"vysledky_prostejov.csv"` |

### Příklad spuštění

V **PowerShellu** spusťte program takto (nezapomeňte na uvozovky u URL):

```powershell
python main.py "[https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xnumnuts=7103](https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xnumnuts=7103)" "vysledky_prostejov.csv"
