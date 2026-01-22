#!/usr/bin/env python3
"""
wash-dryer-patents
Scarica 100 brevetti Wash & Dryer (CPC=D06F) da Espacenet
1 req/s per rispettare anti-bot
Log token ScraperAPI
"""
import os, csv, time, requests
from bs4 import BeautifulSoup
from tqdm import tqdm

API_KEY     = "812a8b6c95bb3ef874aef839dcaad57f"   # <--- la tua ScraperAPI key
CSV_FILE    = "wash_dryer_100.csv"
FIELDS      = ["publication_number","title","abstract","filing_date",
             "publication_date","applicant","inventor","cpc","ipc",
             "country","kind","citation_count","family_size","pdf_url"]
RATE        = 1.0                                      # 1 req/s
PAGE_SIZE   = 100
TOTAL       = 100                                      # per test
BASE        = "https://worldwide.espacenet.com/search"

def get_token_usage():
    """Restituisce crediti usati e rimanenti da ScraperAPI"""
    url = "https://api.scraperapi.com/account"
    r = requests.get(url, params={"api_key": API_KEY}, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["request_count"], data["request_limit"]

def get_page(page):
    """Scarica una pagina HTML via ScraperAPI"""
    url = f"{BASE}?q=CPC%3DD06F&page={page}&pageSize={PAGE_SIZE}"
    payload = {"api_key": API_KEY, "url": url, "render": "false"}
    r = requests.get("http://api.scraperapi.com", params=payload, timeout=60)
    r.raise_for_status()
    return r.text

def parse_html(html):
    """Parsa HTML Espacenet -> lista dict"""
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for card in soup.select("div.publication-content"):
        pn  = card.select_one("span.publication-number").get_text(strip=True)
        ttl = card.select_one("span.title").get_text(strip=True)
        # --- estrai gli altri campi con la stessa logica ---
        rows.append({
            "publication_number": pn,
            "title": ttl,
            "abstract": "",          # placeholder: Espacenet non espone abstract in HTML
            "filing_date": "",       # placeholder
            "publication_date": "",  # placeholder
            "applicant": "",
            "inventor": "",
            "cpc": "D06F",
            "ipc": "",
            "country": pn[:2],
            "kind": pn[-2:],
            "citation_count": 0,
            "family_size": 1,
            "pdf_url": f"https://patentimages.storage.googleapis.com/{pn}.pdf"
        })
    return rows

def main():
    used, limit = get_token_usage()
    print(f"START → used: {used}, remaining: {limit - used}")
    with open(CSV_FILE, "w", newline='', encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for page in tqdm(range(1, (TOTAL // PAGE_SIZE) + 1), desc="Espacenet pages"):
            html = get_page(page)
            rows = parse_html(html)
            for r in rows:
                writer.writerow(r)
            time.sleep(RATE)        # 1 secondo ESATTO
    used_end, limit_end = get_token_usage()
    print(f"DONE → used: {used_end}, remaining: {limit_end - used_end}, consumed: {used_end - used}")

if __name__ == "__main__":
    main()
