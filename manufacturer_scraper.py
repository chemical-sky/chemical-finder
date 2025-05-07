import requests
from bs4 import BeautifulSoup
import json
import re
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}

EXCLUDE_KEYWORDS = ["tci", "sigma", "aldrich", "santa cruz", "otto"]

def get_google_results(cas_number):
    query = f"{cas_number} manufacturer site:chemicalbook.com OR site:buyersguidechem.com"
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for g in soup.find_all('a'):
        href = g.get('href')
        if href and '/url?q=' in href:
            clean_url = re.split('&', href.replace('/url?q=', ''))[0]
            if any(domain in clean_url for domain in ['chemicalbook.com', 'buyersguidechem.com']):
                links.append(clean_url)
    return links[:3]

def build_entry(cas_number):
    links = get_google_results(cas_number)
    entry = {
        "casNo": cas_number,
        "manufacturer": [],
        "country": [],
        "website": []
    }
    for url in links:
        mfg = url.split('/')[2].replace('www.', '').split('.')[0]
        if any(ex in mfg.lower() for ex in EXCLUDE_KEYWORDS):
            continue
        entry['website'].append(url)
        if 'chemicalbook.com' in url:
            if 'china' in url:
                entry['country'].append("China")
        elif 'buyersguidechem.com' in url:
            if 'en/chemical-supplier' in url:
                entry['country'].append("Global")
        else:
            entry['country'].append("Unknown")
        entry['manufacturer'].append(mfg.title())
    return entry

def process_cas_list(cas_list):
    results = []
    seen_cas = set()
    failed_cas = []

    for i, cas in enumerate(cas_list):
        if cas in seen_cas:
            continue
        print(f"[{i+1}/{len(cas_list)}] Processing CAS: {cas}")
        seen_cas.add(cas)
        try:
            data = build_entry(cas)
            results.append(data)
        except Exception as e:
            print(f"Error processing {cas}: {e}")
            failed_cas.append(cas)
        if (i + 1) % 100 == 0:
            with open("partial_enriched.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"💾 중간 저장 완료: {i+1}개 처리됨")
        time.sleep(2)  # 요청 사이 대기

    if failed_cas:
        with open("failed_cas_log.txt", "w", encoding="utf-8") as f:
            for cas in failed_cas:
                f.write(f"{cas}\n")

    return results

if __name__ == "__main__":
    with open("registered_chemicals.json", encoding="utf-8") as f:
        raw_data = json.load(f)
    cas_numbers = [item['casNo'] for item in raw_data]
    data = process_cas_list(cas_numbers)
    with open("registered_chemicals_enriched.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ 전체 완료: registered_chemicals_enriched.json에 저장됨")
