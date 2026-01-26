"""
main.py: Třetí projekt Elections Scraper do Engeto Online Python Akademie
author: Květoslav Leidorf
email: k.leidorf@gmail.com
discord: kvetos_95684
"""

import sys
import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Konstanta pro základní URL, aby se zabránilo hardkódování uvnitř funkcí
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"


def check_arguments() -> None:
    """Kontrola, zda byly zadány oba argumenty příkazové řádky."""
    if len(sys.argv) != 3:
        print("Error: Two arguments required (URL and output file name).")
        print("Example: python main.py \"URL_ADDRESS\" \"vysledky.csv\"")
        sys.exit(1)


def get_soup(url: str) -> BeautifulSoup:
    """Stáhne HTML obsah a vrátí BeautifulSoup objekt s ošetřením chyb."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        sys.exit(1)


def get_town_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Získá kódy obcí, názvy a jejich unikátní odkazy.
    Index [2:] přeskakuje první dva řádky tabulek (záhlaví a prázdné oddělovače).
    Funkce předpokládá specifickou strukturu tabulek na volby.cz.
    """
    towns = []
    tables = soup.find_all("table", {"class": "table"})
    
    for table in tables:
        # Přeskakujeme první 2 řádky (th záhlaví), které neobsahují data obcí
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            
            # Ošetření prázdných řádků nebo řádků bez dat
            if len(tds) < 3 or tds[0].text.strip() == "-": 
                continue
            
            code = tds[0].text.strip()
            location = tds[1].text.strip()
            
            link_tag = tds[0].find("a")
            if not link_tag:
                continue
                
            # Skládání plné URL z relativního odkazu href
            full_link = f"{BASE_URL}{link_tag['href']}"
            
            towns.append({
                "code": code, 
                "location": location, 
                "link": full_link
            })
            
    return towns


def get_parties_list(url: str) -> List[str]:
    """
    Získá seznam všech kandidujících stran z detailu obce.
    Spoléhá na to, že struktura tabulek pro strany je na webu konzistentní.
    """
    soup = get_soup(url)
    parties = []
    tables = soup.find_all("table", {"class": "table"})
    
    for table in tables:
        # Index [2:] opět přeskakuje záhlaví tabulky stran
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            if len(tds) >= 2:
                name = tds[1].text.strip()
                # Filtrujeme pouze reálné názvy stran (ne součty nebo pomlčky)
                if name and name not in ["-", "Celkem"] and not name.isnumeric():
                    parties.append(name)
                    
    return parties


def get_town_data(url: str, all_parties: List[str]) -> Dict[str, Any]:
    """
    Scrapuje data o hlasování v konkrétní obci.
    Využívá specifické 'headers' atributy (sa2, sa3, sa6) pro přesné zacílení dat.
    """
    soup = get_soup(url)
    data = {}
    
    # Atributy 'headers' jsou specifické pro tento web a mohou se při změně webu změnit
    try:
        data["registered"] = soup.find("td", {"headers": "sa2"}).text.replace("\xa0", "").strip()
        data["envelopes"] = soup.find("td", {"headers": "sa3"}).text.replace("\xa0", "").strip()
        data["valid"] = soup.find("td", {"headers": "sa6"}).text.replace("\xa0", "").strip()
    except AttributeError:
        print(f"Varování: Nepodařilo se najít základní data na {url}. Struktura HTML se mohla změnit.")
    
    # Mapování hlasů pro jednotlivé strany
    tables = soup.find_all("table", {"class": "table"})
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            if len(tds) >= 3:
                party_name = tds[1].text.strip()
                if party_name in all_parties:
                    data[party_name] = tds[2].text.replace("\xa0", "").strip()
    
    # Ošetření stran s nulovým ziskem v dané obci
    for party in all_parties:
        if party not in data:
            data[party] = "0"
            
    return data


def save_to_csv(results: List[Dict], all_parties: List[str], filename: str) -> None:
    """Samostatná funkce pro zápis výsledků do CSV souboru."""
    if not results:
        print("Žádná data k zápisu.")
        return

    header = ["code", "location", "registered", "envelopes", "valid"] + all_parties
    
    try:
        with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter=";")
            writer.writeheader()
            writer.writerows(results)
        print(f"HOTOVO. DATA ULOŽENA DO: {filename}")
    except IOError as e:
        print(f"Chyba při zápisu do souboru: {e}")


def main() -> None:
    """Hlavní řídicí funkce scraperu."""
    check_arguments()
    url = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"STAHUJI DATA Z VYBRANÉHO URL: {url}")
    main_soup = get_soup(url)
    towns = get_town_links(main_soup)
    
    if not towns:
        print("Nebyla nalezena žádná data o obcích. Zkontrolujte URL.")
        return

    # Předpokládáme, že první obec obsahuje kompletní seznam stran pro daný územní celek
    print("ZJIŠŤUJI SEZNAM KANDIDUJÍCÍCH STRAN...")
    all_parties = get_parties_list(towns[0]["link"])
    
    results = []
    for index, town in enumerate(towns, start=1):
        print(f"ZPRACOVÁVÁM OBEC ({index}/{len(towns)}): {town['location']}")
        town_results = get_town_data(town["link"], all_parties)
        
        full_row = {
            "code": town["code"],
            "location": town["location"],
            **town_results
        }
        results.append(full_row)

    save_to_csv(results, all_parties, output_file)


if __name__ == "__main__":
    main()
