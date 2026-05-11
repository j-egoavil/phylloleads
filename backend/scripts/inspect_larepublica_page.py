#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

url = 'https://empresas.larepublica.co/colombia/boyaca/garagoa/soluciones-agricolas-y-veterinarias-integrales-sostenibles-de-colombia-sas-901004993'

print(f"Fetching: {url}\n")
resp = requests.get(url, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Extract all text
full_text = soup.get_text()

# Look for phone patterns
phone_pattern = r'\+57[0-9\s\-()]{8,}|(\d{1,4})\s*[\-\s]?(\d{3,4})\s*[\-\s]?(\d{4})'
phones = re.findall(phone_pattern, full_text)
print("Teléfonos encontrados:")
for p in set([str(x) for x in phones]):
    print(f"  - {p}")

# Look for common contact sections
print("\nBuscando secciones de contacto:")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
    text = h.get_text(strip=True).lower()
    if any(keyword in text for keyword in ['contacto', 'telefono', 'dirección', 'ubicación', 'email', 'información']):
        # Get next few siblings
        print(f"\n{h.get_text(strip=True)}:")
        next_elem = h.find_next(['p', 'div', 'span', 'a'])
        if next_elem:
            print(f"  Content: {next_elem.get_text(strip=True)[:150]}")

# Look for links with tel: protocol
print("\nLinks tel: encontrados:")
for link in soup.find_all('a', href=re.compile(r'^tel:', re.IGNORECASE)):
    print(f"  - {link.get('href')}")
    print(f"    Text: {link.get_text(strip=True)}")

print("\nPrimeros 500 caracteres del HTML:")
print(resp.text[:500])
