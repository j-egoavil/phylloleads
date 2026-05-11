#!/usr/bin/env python3
"""
Debug avanzado: Ver qué HTML devuelven Google Maps y Google Web
"""

import sys
import requests
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_google_maps():
    """Inspecciona HTML de Google Maps"""
    print("\n" + "="*70)
    print("TEST: Google Maps HTML")
    print("="*70)
    
    company = "ANIMAL CARE CENTRO DE ESPECIALIDADES VETERINARIAS"
    city = "Bogota"
    search_query = f"{company} {city}"
    
    url = f"https://www.google.com/maps/search/{requests.utils.quote(search_query)}"
    print(f"URL: {url}\n")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Content-Length: {len(resp.text)} bytes")
        
        # Ver primeras 500 caracteres
        print(f"\nPrimeros 500 caracteres del HTML:")
        print(resp.text[:500])
        
        # Buscar patrones
        if "phone" in resp.text.lower() or "tel" in resp.text.lower():
            print("\n✓ Se encontraron referencias a teléfono")
        else:
            print("\n✗ No hay referencias a teléfono en el HTML")
        
        # Detectar si es contenido dinámico
        if "window.__INITIAL_STATE__" in resp.text or "json" in resp.text[:1000].lower():
            print("✓ Parece contener datos dinámicos/JSON")
        else:
            print("✗ HTML es principalmente estático")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def test_google_web():
    """Inspecciona HTML de búsqueda web de Google"""
    print("\n" + "="*70)
    print("TEST: Google Web Search HTML")
    print("="*70)
    
    company = "ANIMAL CARE CENTRO DE ESPECIALIDADES VETERINARIAS"
    city = "Bogota"
    query = f"{company} {city} telefono contacto site:.co"
    
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    print(f"URL: {url}\n")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Content-Length: {len(resp.text)} bytes")
        
        # Ver primeros 500 caracteres
        print(f"\nPrimeros 500 caracteres del HTML:")
        print(resp.text[:500])
        
        # Detectar si es un error
        if "unusual traffic" in resp.text.lower() or "not showing" in resp.text.lower():
            print("\n⚠️ Google está bloqueando la búsqueda (unusual traffic)")
        elif "did not match" in resp.text.lower():
            print("\n✗ No hay resultados para la búsqueda")
        else:
            print("\n✓ Búsqueda devolvió resultados")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def test_paginas_amarillas():
    """Inspecciona Páginas Amarillas"""
    print("\n" + "="*70)
    print("TEST: Páginas Amarillas")
    print("="*70)
    
    company = "ANIMAL CARE"
    city = "bogota"
    
    url = f"https://www.paginasamarillas.com.co/search?q={company}&location={city}"
    print(f"URL: {url}\n")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Content-Length: {len(resp.text)} bytes")
        
        # Buscar teléfono
        if re.search(r'\+?\d{1,3}\s?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}', resp.text):
            print("✓ Se encontraron patrones de teléfono")
        else:
            print("✗ No hay patrones de teléfono detectados")
        
        # Buscar gestor
        if "gurusoluciones" in resp.text.lower():
            print("⚠️ Se encontraron referencias a gurusoluciones (gestor de sitios)")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"\nEstructura de página:")
        print(f"  - Títulos (h1-h6): {len(soup.find_all(['h1','h2','h3','h4','h5','h6']))}")
        print(f"  - Links: {len(soup.find_all('a'))}")
        print(f"  - Divs: {len(soup.find_all('div'))[:100]}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    import re
    test_google_maps()
    test_google_web()
    test_paginas_amarillas()
