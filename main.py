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

def check_arguments() -> None:
    """Kontrola, zda byly zadány oba argumenty příkazové řádky."""
    if len(sys.argv) != 3:
        print("Error: Two arguments required (URL and output file name).")
        print("Example: python main.py \"URL_ADDRESS\" \"vysledky.csv\"")
        sys.exit(1)

def get_soup(url: str) -> BeautifulSoup:
    """Stáhne HTML obsah a vrátí BeautifulSoup objekt."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        sys.exit(1)

def get_town_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Získá kódy obcí, názvy a jejich unikátní odkazy na detaily."""
    towns = []
    tables = soup.find_all("table", {"class": "table"})
    
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            # Pokud je řádek prázdný nebo obsahuje jen "-"
            if len(tds) < 3 or tds[0].text.strip() == "-": 
                continue
            
            code = tds[0].text.strip()
            location = tds[1].text.strip()
            
            # Oprava skládání odkazu - bereme href z prvního <td>
            link_tag = tds[0].find("a")
            if not link_tag:
                continue
                
            link_suffix = link_tag["href"]
            full_link = f"https://www.volby.cz/pls/ps2017nss/{link_suffix}"
            
            towns.append({"code": code, "location": location, "link": full_link})
    return towns

def get_parties_list(url: str) -> List[str]:
    """Získá seznam všech kandidujících stran z detailu první obce."""
    soup = get_soup(url)
    parties = []
    # Strany jsou v tabulkách s id t1sb2 a t2sb2 (nebo t1 a t2)
    tables = soup.find_all("table", {"class": "table"})
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            if len(tds) >= 2:
                name = tds[1].text.strip()
                # Vyfiltrování řádků, které nejsou názvy stran
                if name and name not in ["-", "Celkem"] and not name.isnumeric():
                    parties.append(name)
    return parties

def get_town_data(url: str, all_parties: List[str]) -> Dict[str, Any]:
    """Scrapuje data o hlasování a mapuje je na kompletní seznam stran."""
    soup = get_soup(url)
    data = {}
    
    # Základní data (voliči, obálky, platné)
    data["registered"] = soup.find("td", {"headers": "sa2"}).text.replace("\xa0", "").strip()
    data["envelopes"] = soup.find("td", {"headers": "sa3"}).text.replace("\xa0", "").strip()
    data["valid"] = soup.find("td", {"headers": "sa6"}).text.replace("\xa0", "").strip()
    
    # Naplnění stran
    tables = soup.find_all("table", {"class": "table"})
    # Projdeme všechny tabulky s výsledky stran
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            if len(tds) >= 3:
                party_name = tds[1].text.strip()
                if party_name in all_parties:
                    data[party_name] = tds[2].text.replace("\xa0", "").strip()
            
    # Doplnění nul pro strany, které v dané obci neměly hlasy
    for party in all_parties:
        if party not in data:
            data[party] = "0"
            
    return data

def main() -> None:
    check_arguments()
    url = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"STAHUJI DATA Z VYBRANÉHO URL: {url}")
    main_soup = get_soup(url)
    towns = get_town_links(main_soup)
    
    if not towns:
        print("Nebyla nalezena žádná data o obcích. Zkontrolujte URL.")
        return

    print("ZJIŠŤUJI SEZNAM KANDIDUJÍCÍCH STRAN...")
    all_parties = get_parties_list(towns[0]["link"])
    
    results = []
    for index, town in enumerate(towns):
        print(f"ZPRACOVÁVÁM OBEC ({index + 1}/{len(towns)}): {town['location']}")
        town_results = get_town_data(town["link"], all_parties)
        
        full_row = {
            "code": town["code"],
            "location": town["location"],
            **town_results
        }
        results.append(full_row)

    # Zápis do CSV
    if results:
        header = ["code", "location", "registered", "envelopes", "valid"] + all_parties
        with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter=";")
            writer.writeheader()
            writer.writerows(results)
        print(f"HOTOVO. DATA ULOŽENA DO: {output_file}")

if __name__ == "__main__":
    main()
