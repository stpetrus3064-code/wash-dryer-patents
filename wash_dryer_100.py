#!/usr/bin/env python3
"""
wash-dryer-patents
Scarica 100 brevetti Wash & Dryer (CPC=D06F) da Espacenet
1 req/s per rispettare anti-bot
NO token check (free trial safe)
"""

import os, csv, time, requests
from bs4 import BeautifulSoup
from tqdm import tqdm

API_KEY   = os.getenv("SCRAPERAPI_KEY", "812a8b6c95bb3ef874aef839dcaad57f")
CSV_FILE  = "wash_dryer_100.csv"
FIELDS    = ["publication_number","title","filing_date","publication_date",
             "applicant","inventor","cpc","ipc","country","kind",
             "citation_count","family_size","pdf_url"]
RATE      = 1.0          # 1 secondo ESATTO
PAGE_SIZE = 100
TOTAL     = 100          # batch di test

BASE = "https://worldwide.espacenet.com/search"

def get_page(page):
    """Scarica HTML via ScraperAPI (anti-bot bypass)"""
    url = f"{BASE}?q=CPC%3DD06F&page={page}&pageSize={PAGE_SIZE}"
    payload = {"api_key": API_KEY, "url": url, "render": "false"}
    r = requests.get("http://api.scraperapi.com", params=payload, timeout=60)
    r.raise_for_status()
    return r.text

def parse_html(html):
    """Parsa HTML Espacenet -> lista dict (robusto)"""
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for card in soup.select("div.publication-content"):
        pn  = card.select_one("span.publication-number")
        ttl = card.select_one("span.title")
        if not (pn and ttl):                       # salta se mancano dati
            continue
        rows.append({
            "publication_number": pn.get_text(strip=True),
            "title": ttl.get_text(strip=True),
            "filing_date": "",        # placeholder
            "publication_date": "",
            "applicant": "",
            "inventor": "",
            "cpc": "D06F",
            "ipc": "",
            "country": pn.get_text(strip=True)[:2],
            "kind": pn.get_text(strip=True)[-2:],
            "citation_count": 0,
            "family_size": 1,
            "pdf_url": f"https://patentimages.storage.googleapis.com/{pn.get_text(strip=True)}.pdf"
        })
    return rows

def main():
    print("START → extraction 100 patents (1 req/s)")
    written = 0
    with open(CSV_FILE, "w", newline='', encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for page in tqdm(range(1, (TOTAL // PAGE_SIZE) + 1), desc="Espacenet pages"):
            html = get_page(page)
            rows = parse_html(html)
            for r in rows:
                writer.writerow(r)
                written += 1
            time.sleep(RATE)        # 1 secondo ESATTO
    print(f"DONE → saved {written} rows in {CSV_FILE}")

if __name__ == "__main__":
    main()
