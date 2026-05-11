#!/usr/bin/env python3
"""
Inspecciona un resultado específico de Páginas Amarillas para entender su estructura
"""

import requests
from bs4 import BeautifulSoup
import json

url = "https://www.paginasamarillas.com.co/search?q=veterinaria&location=bogota"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get(url, headers=headers, timeout=10)

soup = BeautifulSoup(resp.text, 'html.parser')

print("="*70)
print("ANALISIS DE RESULTADOS DE PAGINAS AMARILLAS")
print("="*70)

# Encuentra elementos que podrían ser resultados
divs_result = soup.find_all('div', class_='result')
print(f"\nEncontrados {len(divs_result)} divs con class 'result'")

if divs_result:
    print(f"\nAnalizando primer resultado:")
    first_result = divs_result[0]
    
    print(f"\nEstructura HTML (primeros 2000 caracteres):")
    print(str(first_result)[:2000])
    
    print(f"\nTexto plano del primer resultado:")
    text = first_result.get_text("\n", strip=True)
    print(text[:500])
    
# Búsqueda alternativa: scripts JSON-LD
print("\n" + "="*70)
print("BUSQUEDA DE DATOS ESTRUCTURADOS (JSON-LD)")
print("="*70)

scripts = soup.find_all('script', type='application/ld+json')
print(f"Encontrados {len(scripts)} bloques JSON-LD")

if scripts:
    for i, script in enumerate(scripts[:3]):
        print(f"\nJSON-LD #{i+1}:")
        try:
            data = json.loads(script.string)
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
        except:
            print(script.string[:200])

# Búsqueda de links a empresas
print("\n" + "="*70)
print("BUSQUEDA DE LINKS A EMPRESAS")
print("="*70)

links = soup.find_all('a')
empresa_links = [l for l in links if '/empresa/' in l.get('href', '')]
print(f"Encontrados {len(empresa_links)} links de empresas")

for link in empresa_links[:5]:
    print(f"  - {link.get_text(strip=True)}: {link.get('href')}")

# Búsqueda de información de contacto
print("\n" + "="*70)
print("BUSQUEDA DE INFO DE CONTACTO")
print("="*70)

# Buscar en atributos data-
elements_with_data = soup.find_all(attrs={"data-phone": True})
print(f"Elementos con data-phone: {len(elements_with_data)}")
for elem in elements_with_data[:5]:
    print(f"  - {elem.get('data-phone')}: {elem.get_text(strip=True)[:50]}")

elements_with_url = soup.find_all(attrs={"data-url": True})
print(f"Elementos con data-url: {len(elements_with_url)}")
for elem in elements_with_url[:5]:
    print(f"  - {elem.get('data-url')}: {elem.get_text(strip=True)[:50]}")

print("\n" + "="*70)
