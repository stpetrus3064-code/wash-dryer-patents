#!/usr/bin/env python3
"""
wash-dryer-patents
Scarica 100 brevetti Wash & Dryer (CPC=D06F) da Espacenet
1 req/s per rispettare anti-bot
LOG DETTAGLIATO
"""

import os, csv, time, requests
from bs4 import BeautifulSoup

API_KEY   = "812a8b6c95bb3ef874aef839dcaad57f"
CSV_FILE  = "wash_dryer_100.csv"
FIELDS    = ["publication_number","title","country","kind","pdf_url"]
RATE      = 1.0
PAGE_SIZE = 100
TOTAL     = 100

BASE = "https://worldwide.espacenet.com/search"

def get_page(page):
    print(f"[GET] page {page} via ScraperAPI …")
    url = f"{BASE}?q=CPC%3DD06F&page={page}&pageSize={PAGE_SIZE}"
    payload = {"api_key": API_KEY, "url": url, "render": "false"}
    r = requests.get("http://api.scraperapi.com", params=payload, timeout=60)
    r.raise_for_status()
    print(f"[GET] page {page} → HTTP {r.status_code}")
    return r.text

def parse_html(html):
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.publication-content")
    print(f"[PARSE] found {len(cards)} cards")
    rows = []
    for card in cards:
        pn  = card.select_one("span.publication-number")
        ttl = card.select_one("span.title")
        if not (pn and ttl): continue
        pn_txt = pn.get_text(strip=True)
        rows.append({
            "publication_number": pn_txt,
            "title": ttl.get_text(strip=True),
            "country": pn_txt[:2],
            "kind": pn_txt[-2:],
            "pdf_url": f"https://patentimages.storage.googleapis.com/{pn_txt}.pdf"
        })
    return rows

def main():
    print("START → 100 patents (1 req/s, log dettagliato)")
    written = 0
    with open(CSV_FILE, "w", newline='', encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for page in range(1, (TOTAL // PAGE_SIZE) + 1):
            html = get_page(page)
            rows = parse_html(html)
            for r in rows:
                writer.writerow(r)
                written += 1
            print(f"[CSV] page {page} → {len(rows)} rows written (total {written})")
            time.sleep(RATE)
    print(f"DONE → saved {written} rows in {CSV_FILE}")

if __name__ == "__main__":
    main()
