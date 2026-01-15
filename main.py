"""
main.py: Třetí projekt do Engeto Online Python Akademie Election Scraper
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
    # Tabulky s daty obcí mají třídu "table"
    tables = soup.find_all("table", {"class": "table"})
    
    for table in tables:
        rows = table.find_all("tr")[2:]  # Přeskočení hlaviček
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 3 or tds[0].text == "-": 
                continue
            
            code = tds[0].text
            location = tds[1].text
            # Odkaz na detail obce
            link_suffix = tds[0].find("a")["href"]
            full_link = f"https://www.volby.cz/pls/ps2017nss/{link_suffix}"
            
            towns.append({"code": code, "location": location, "link": full_link})
    return towns

def get_town_data(url: str) -> Dict[str, Any]:
    """Scrapuje data o hlasování z detailu konkrétní obce."""
    soup = get_soup(url)
    data = {}
    
    # Základní data o voličích
    data["registered"] = soup.find("td", {"headers": "sa2"}).text.replace("\xa0", "")
    data["envelopes"] = soup.find("td", {"headers": "sa3"}).text.replace("\xa0", "")
    data["valid"] = soup.find("td", {"headers": "sa6"}).text.replace("\xa0", "")
    
    # Hlasy pro politické strany (ve dvou tabulkách t1 a t2)
    for i in [1, 2]:
        table = soup.find("div", {"id": f"t{i}"})
        if not table:
            continue
        rows = table.find_all("tr")[2:]
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 3 or tds[1].text == "-":
                continue
            party_name = tds[1].text
            votes = tds[2].text.replace("\xa0", "")
            data[party_name] = votes
            
    return data

def main() -> None:
    check_arguments()
    url = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"STAHUJI DATA Z VYBRANÉHO URL: {url}")
    main_soup = get_soup(url)
    towns = get_town_links(main_soup)
    
    results = []
    
    for index, town in enumerate(towns):
        print(f"ZPRACOVÁVÁM OBEC ({index + 1}/{len(towns)}): {town['location']}")
        town_info = get_town_data(town["link"])
        
        # Spojení základních info o obci a výsledků hlasování
        full_row = {
            "code": town["code"],
            "location": town["location"],
            **town_info
        }
        results.append(full_row)

    # Zápis do CSV
    if results:
        header = results[0].keys()
        with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter=";")
            writer.writeheader()
            writer.writerows(results)
        print(f"HOTOVO. DATA ULOŽENA DO: {output_file}")

# Spuštění hlavní smyčky programu
if __name__ == "__main__":
    main()
