#!/usr/bin/env python3
"""
Debug: Inspecciona HTML renderizado de Paginas Amarillas con Selenium
para entender estructura y mejorar extracción
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

def get_firefox_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    return webdriver.Firefox(options=options)

driver = get_firefox_driver()

# Buscar algo simple
company = "ANIMAL CARE"
city = "bogota"

url = f"https://www.paginasamarillas.com.co/search?q={requests.utils.quote(company)}&location={requests.utils.quote(city)}"

print("="*70)
print("DEBUG: HTML RENDERIZADO DE PAGINAS AMARILLAS")
print("="*70)
print(f"URL: {url}\n")

driver.set_page_load_timeout(20)
driver.get(url)

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='result'], [class*='item']"))
    )
except:
    pass

time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

print(f"HTML size: {len(html)} bytes\n")

# Análisis 1: Todos los links
print("="*70)
print("1. TODOS LOS LINKS EN LA PAGINA:")
print("="*70)
links = soup.find_all('a', href=True)
print(f"Total de links: {len(links)}\n")

unique_links = {}
for link in links:
    href = link.get('href', '').strip()
    if href and href.startswith('http'):
        if href not in unique_links:
            unique_links[href] = link.get_text(strip=True)

print("Links únicos:")
for i, (href, text) in enumerate(list(unique_links.items())[:20]):
    print(f"  {i+1}. {text[:40]:40s} -> {href[:60]}")

# Análisis 2: Texto con teléfono
print("\n" + "="*70)
print("2. BUSQUEDA DE TELEFONOS:")
print("="*70)
all_text = soup.get_text("\n")
phone_pattern = r'\+?\d{1,3}\s?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}'
phones = re.findall(phone_pattern, all_text)
unique_phones = list(set(phones))
print(f"Telefonos encontrados: {len(unique_phones)}")
for phone in unique_phones[:10]:
    print(f"  - {phone}")

# Análisis 3: Estructura de divs con datos
print("\n" + "="*70)
print("3. DIVS Y CONTENEDORES:")
print("="*70)

# Buscar divs con atributos data-*
divs_with_data = soup.find_all('div', attrs={'data-testid': True})
print(f"Divs con data-testid: {len(divs_with_data)}")
for div in divs_with_data[:5]:
    print(f"  - data-testid: {div.get('data-testid')}")

# Análisis 4: JSON-LD
print("\n" + "="*70)
print("4. DATOS ESTRUCTURADOS (JSON-LD):")
print("="*70)
scripts = soup.find_all('script', type='application/ld+json')
print(f"Bloques JSON-LD: {len(scripts)}")
if scripts:
    import json
    for i, script in enumerate(scripts[:3]):
        print(f"\nJSON-LD #{i+1}:")
        try:
            data = json.loads(script.string)
            print(json.dumps(data, indent=2, ensure_ascii=False)[:300])
        except:
            print(script.string[:100])

# Análisis 5: Primeros 5000 caracteres HTML
print("\n" + "="*70)
print("5. PRIMEROS 5000 CARACTERES DEL HTML:")
print("="*70)
print(html[:5000])

driver.quit()
