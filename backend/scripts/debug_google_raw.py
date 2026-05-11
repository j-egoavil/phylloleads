#!/usr/bin/env python3
"""
Debug: Inspect raw Google HTML for embedded JSON or structured data
"""
import sys
import os
import time
import random
import re
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup

def debug_google_raw():
    """Check raw Google response for embedded data"""
    
    empresa_nombre = "AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET S.A.S."
    ciudad = "colombia"
    search_query = f"{empresa_nombre} {ciudad} telefono contacto direccion"
    search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
    
    delay = random.uniform(2, 5)
    time.sleep(delay)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-CO,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
    }
    
    response = requests.get(search_url, headers=headers, timeout=15)
    html = response.text
    
    print(f"[1] Response size: {len(html)} bytes\n")
    
    # Check for JSON data in script tags
    print("[2] Searching for JSON-LD or embedded data...\n")
    
    # Look for script tags with JSON
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(scripts)} script tags\n")
    
    for idx, script in enumerate(scripts[:3]):  # First 3
        if len(script) > 50:
            print(f"Script {idx} (first 200 chars):")
            print(script[:200])
            print("...\n")
    
    # Look for window data
    print("[3] Searching for window.___data___ or similar patterns...\n")
    
    if 'window.__data__' in html:
        print("Found: window.__data__")
    if 'window.jwplayer' in html:
        print("Found: window.jwplayer")
    if 'AF_initDataCallback' in html:
        print("Found: AF_initDataCallback")
    if 'window[\'gtm.uniqueEventId\']' in html:
        print("Found: Google Tag Manager data")
    
    # Try to find actual search result links
    print("\n[4] Searching for actual result links (href patterns)...\n")
    
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    print(f"Found {len(links)} total links\n")
    
    # Filter for result links (not navigation)
    result_links = [l for l in links if '/url?' in l.get('href', '')]
    print(f"Found {len(result_links)} /url? links (likely results)\n")
    
    for i, link in enumerate(result_links[:5]):
        href = link.get('href', '')
        text = link.get_text(strip=True)[:50]
        print(f"{i+1}. {text}")
        print(f"   {href[:80]}\n")
    
    # Check what kind of response we got
    print("[5] Response analysis:\n")
    
    if 'Haz clic' in html or 'click here' in html or 'redirecciona' in html:
        print("⚠ Getting REDIRECT PAGE (JavaScript required)")
    
    if 'recaptcha' in html.lower():
        print("⚠ CAPTCHA DETECTED")
    
    if result_links:
        print(f"✓ Found {len(result_links)} search result links")
    else:
        print("✗ No search result links found")
    
    print(f"\n[6] HTML STRUCTURE - First 1500 chars:\n")
    print(html[:1500])

if __name__ == "__main__":
    debug_google_raw()
