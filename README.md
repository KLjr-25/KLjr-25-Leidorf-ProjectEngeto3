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
