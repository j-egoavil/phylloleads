#!/usr/bin/env python3
"""
Analiza la estructura HTML de Páginas Amarillas para extraer correctamente
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.paginasamarillas.com.co/search?q=ANIMAL%20CARE&location=bogota"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get(url, headers=headers, timeout=10)

soup = BeautifulSoup(resp.text, 'html.parser')

print("="*70)
print("ESTRUCTURA DE PAGINAS AMARILLAS")
print("="*70)

# Encontrar estructuras de resultados
print("\n1. Búsqueda de posibles contenedores de resultados:")
containers = [
    soup.find_all('div', class_='business-card'),
    soup.find_all('div', class_='business-item'),
    soup.find_all('div', class_='result'),
    soup.find_all('li', class_=re.compile('result|item|business')),
    soup.find_all('article'),
]

for i, cont_list in enumerate(containers):
    if cont_list:
        print(f"   ✓ Encontrados {len(cont_list)} elementos tipo {i}")

# Análisis de texto para encontrar teléfonos
print("\n2. Patrones de teléfono en la página:")
phone_pattern = r'\+?\d{1,3}\s?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}'
phones = re.findall(phone_pattern, resp.text)
print(f"   Teléfonos encontrados: {len(set(phones))}")
for phone in list(set(phones))[:5]:
    print(f"      - {phone}")

# Análisis de websites
print("\n3. URLs/Websites en la página:")
url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]*'
urls = re.findall(url_pattern, resp.text)
unique_urls = list(set(urls))
print(f"   URLs encontradas: {len(unique_urls)}")
for url_item in unique_urls[:10]:
    if len(url_item) < 60:
        print(f"      - {url_item}")

# Búsqueda de gestores
print("\n4. Detección de gestores:")
gestores = ['gurusoluciones', 'wix', 'godaddy', 'wordpress', 'blogger', 'weebly']
for gestor in gestores:
    count = resp.text.lower().count(gestor)
    if count > 0:
        print(f"   {gestor}: {count} referencias")

# Análisis de estructura HTML
print("\n5. Estructura HTML completa (primeros 3000 caracteres):")
print(resp.text[:3000])

print("\n" + "="*70)
