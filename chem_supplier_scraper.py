import requests
from bs4 import BeautifulSoup
import time
import json
import os


def get_buyersguidechem_suppliers(cas_number):
    url = f"https://www.buyersguidechem.com/chemical_supplier/products?cas={cas_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ BuyersGuideChem 연결 실패: {cas_number} → {e}")
        return []

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    supplier_cards = soup.select(".searchresult div.card")
    for card in supplier_cards:
        name_tag = card.select_one("h5.card-title")
        website_tag = card.select_one("a[href^='http']")
        country_tag = card.select_one("div.card-body > p")

        name = name_tag.text.strip() if name_tag else "Unknown"
        website = website_tag['href'].strip() if website_tag else ""
        country = country_tag.text.strip().split("|")[-1].strip() if country_tag else ""

        EXCLUDE_KEYWORDS = ["sigma", "aladdin", "tci", "otto", "fisher"]
        if any(keyword in name.lower() for keyword in EXCLUDE_KEYWORDS):
            continue

        results.append({
            "manufacturer": name,
            "country": country,
            "website": website
        })

    return results


def get_chemblink_suppliers(cas_number):
    url = f"http://www.chemblink.com/products/{cas_number}.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ ChemBlink 연결 실패: {cas_number} → {e}")
        return []

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    table = soup.find("table", attrs={"cellpadding": "2"})
    if not table:
        return []

    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            name = cols[0].text.strip()
            website_tag = cols[0].find("a", href=True)
            website = website_tag['href'].strip() if website_tag else ""
            country = ""

            EXCLUDE_KEYWORDS = ["sigma", "aladdin", "tci", "otto", "fisher"]
            if any(keyword in name.lower() for keyword in EXCLUDE_KEYWORDS):
                continue

            results.append({
                "manufacturer": name,
                "country": country,
                "website": website
            })

    return results


if __name__ == "__main__":
    with open("registered_chemicals_enriched.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        cas_list = [item["casNo"] for item in raw_data if item["casNo"] != "-"]

    progress_file = "merged_suppliers_progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as pf:
            final_result = json.load(pf)
    else:
        final_result = {}

    start_index = len(final_result)
    batch_size = 100

    for i, cas in enumerate(cas_list[start_index:], start=start_index):
        print(f"[{i+1}/{len(cas_list)}] Processing {cas}...")

        bchem = get_buyersguidechem_suppliers(cas)
        cblink = get_chemblink_suppliers(cas)

        all_suppliers = bchem + cblink

        seen = set()
        unique_suppliers = []
        for s in all_suppliers:
            if s['manufacturer'] not in seen:
                seen.add(s['manufacturer'])
                unique_suppliers.append(s)

        final_result[cas] = unique_suppliers

        if (i + 1) % batch_size == 0:
            with open(progress_file, "w", encoding="utf-8") as pf:
                json.dump(final_result, pf, ensure_ascii=False, indent=2)
            print(f"💾 중간 저장 완료: {i + 1}개 처리됨")

        time.sleep(2)

    with open("merged_suppliers.json", "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print("✅ 전체 크롤링 완료! merged_suppliers.json 저장됨.")
