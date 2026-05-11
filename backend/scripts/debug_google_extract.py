#!/usr/bin/env python3
"""
Debug script: Inspect actual Google search HTML and phone extraction
Uses HTTP requests instead of Selenium to avoid detection
"""
import sys
import os
import re
import time
import random
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.scraper_automatico import AutomaticDataScraper
from bs4 import BeautifulSoup
import requests

def debug_google_search():
    """Debug a single Google search via HTTP and inspect the HTML"""
    
    scraper = AutomaticDataScraper()
    
    # Test company
    empresa_nombre = "AYUDAS DIAGNOSTICAS VETERINARIAS IMAVET S.A.S."
    ciudad = "colombia"
    search_query = f"{empresa_nombre} {ciudad} telefono contacto direccion"
    search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
    
    print(f"\n[1] URL: {search_url}\n")
    
    # Delay to avoid immediate blocking
    delay = random.uniform(2, 5)
    print(f"[2] Waiting {delay:.1f}s before request...\n")
    time.sleep(delay)
    
    # Headers realistas
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-CO,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("[3] Making HTTP request...\n")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        html = response.text
        print(f"[4] Response: {response.status_code} | Size: {len(html)} bytes\n")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        all_text = soup.get_text("\n")
        
        print(f"[5] Extracted text: {len(all_text)} bytes\n")
        
        # Show first 3000 chars
        print("[6] FIRST 3000 CHARS OF EXTRACTED TEXT:")
        print("=" * 80)
        print(all_text[:3000])
        print("=" * 80)
        print()
        
        # Check for blocking
        if 'recaptcha' in html.lower() or 'unusual traffic' in html.lower():
            print("[!] BLOCKED: Google returning CAPTCHA\n")
            return
        
        print("[7] SEARCHING FOR PHONE PATTERNS:\n")
        
        patterns = [
            (r'\+57\s*[1-9]\s*[\d\s\-\(\)]{8,}', '+57 format'),
            (r'\(?\d{1,3}\)?\s*[\d\s\-\(\)]{8,12}', '(1) format'),
            (r'\d{3}[\s\-]?\d{3,4}[\s\-]?\d{4}', 'XXX-XXXX format'),
            (r'\+\d{1,3}\s*\d{8,}', 'International +'),
        ]
        
        for pattern, name in patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                print(f"  {name}: {matches[:3]}")
            else:
                print(f"  {name}: NO MATCHES")
        
        print()
        print("[8] TESTING extract_phone_from_text METHOD:\n")
        
        phone = scraper.extract_phone_from_text(all_text)
        print(f"Result: {phone}")
        
        print("\n[9] UNIQUE NUMBER SEQUENCES (5+ digits):\n")
        number_sequences = re.findall(r'\d{5,}', all_text)
        unique_sequences = sorted(set(number_sequences))[:15]
        for seq in unique_sequences:
            print(f"  {seq}")
            
    except requests.exceptions.RequestException as e:
        print(f"[!] REQUEST ERROR: {e}\n")
        return

if __name__ == "__main__":
    debug_google_search()

