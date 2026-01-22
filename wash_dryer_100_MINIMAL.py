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

API_KEY   = "812a8b6c95bb3ef874aef839dcaad57f"
CSV_FILE  = "wash_dryer_100.csv"
FIELDS    = ["publication_number","title","country","kind","pdf_url"]
RATE      = 1.0
PAGE_SIZE = 100
TOTAL     = 100

BASE = "https://worldwide.espacenet.com/search"

def get_page(page):
    url = f"{BASE}?q=CPC%3DD06F&page={page}&pageSize={PAGE_SIZE}"
    payload = {"api_key": API_KEY, "url": url, "render": "false"}
    r = requests.get("http://api.scraperapi.com", params=payload, timeout=60)
    r.raise_for_status()
    return r.text

def parse_html(html):
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for card in soup.select("div.publication-content"):
        pn  = card.select_one("span.publication-number")
