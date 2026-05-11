#!/usr/bin/env python3
"""Debug DuckDuckGo HTML structure"""
import sys
import time
import random
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup

empresa_nombre = "AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET S.A.S."
ciudad = "colombia"
search_query = f"{empresa_nombre} {ciudad} telefono contacto"
search_url = f"https://duckduckgo.com/html/?q={requests.utils.quote(search_query)}"

time.sleep(random.uniform(1, 3))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

response = requests.get(search_url, headers=headers, timeout=10)
html = response.text

print(f"[1] DuckDuckGo Response: {len(html)} bytes\n")

soup = BeautifulSoup(html, 'html.parser')
all_text = soup.get_text("\n")

print(f"[2] Extracted text: {len(all_text)} bytes\n")

print("[3] FIRST 2000 CHARS:\n")
print(all_text[:2000])
print("\n" + "="*80 + "\n")

# Look for result links
print("[4] Looking for result links:\n")
links = soup.find_all('a', href=True)
print(f"Total links: {len(links)}\n")

for i, link in enumerate(links[:10]):
    href = link.get('href', '')
    text = link.get_text(strip=True)[:50]
    if 'duckduckgo' not in href.lower():
        print(f"{i+1}. {text}")
        print(f"   {href}\n")

# Look for result containers
print("[5] Looking for result containers:\n")

# DuckDuckGo HTML uses <div class="result"> or similar
results = soup.find_all('div', class_=re.compile(r'result'))
print(f"Found {len(results)} divs with 'result' class\n")

for i, result in enumerate(results[:3]):
    print(f"Result {i+1}:\n{result.get_text(strip=True)[:200]}\n")

# Look for phone numbers in text
print("[6] Phone patterns in full text:\n")
patterns = [
    (r'\d{3}[\s\-]?\d{3,4}[\s\-]?\d{4}', '10-digit'),
    (r'\+57\s*\d{10}', '+57 format'),
    (r'\(\d{1,3}\)\s*\d{6,8}', '(XX) format'),
]

for pattern, name in patterns:
    matches = re.findall(pattern, all_text)
    if matches:
        print(f"{name}: {matches[:3]}")

# All 5+ digit sequences
print("\n[7] All number sequences:\n")
nums = re.findall(r'\d{5,}', all_text)
unique_nums = sorted(set(nums))[:10]
for num in unique_nums:
    print(f"  {num}")
