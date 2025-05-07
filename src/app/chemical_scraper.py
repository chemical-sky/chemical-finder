import requests
from bs4 import BeautifulSoup
import json

base_url = "https://en.wikipedia.org/wiki/List_of_CAS_numbers_by_chemical_compound"
response = requests.get(base_url)
soup = BeautifulSoup(response.content, "html.parser")

chemicals = []

# find all tables in the page
tables = soup.find_all("table", class_="wikitable")

for table in tables:
    rows = table.find_all("tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 2:
            chemical_name = cols[0].text.strip()
            cas_no = cols[1].text.strip()
            if chemical_name and cas_no:
                chemicals.append({
                    "chemicalName": chemical_name,
                    "casNo": cas_no,
                    "manufacturer": "",
                    "country": "",
                    "website": ""
                })

# save as JSON
with open("chemical_data_AtoC.json", "w", encoding="utf-8") as f:
    json.dump(chemicals, f, indent=2, ensure_ascii=False)

print(f"Saved {len(chemicals)} chemicals to chemical_data_AtoC.json")
