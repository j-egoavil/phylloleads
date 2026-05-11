#!/usr/bin/env python3
"""
Debug script para inspeccionar qué devuelven Google Maps y Google Web
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.scraper_automatico import AutomaticDataScraper
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_search():
    scraper = AutomaticDataScraper()
    
    # Test 1: Google Maps
    print("\n" + "="*70)
    print("TEST 1: Google Maps Search")
    print("="*70)
    company = "ANIMAL CARE CENTRO DE ESPECIALIDADES VETERINARIAS"
    city = "Bogota"
    
    print(f"\nBuscando: {company} en {city}")
    print(f"Esperando: Teléfono, website, dirección")
    
    result = scraper.search_google_maps(company, city)
    print(f"\nResultado:")
    print(f"  Type: {type(result)}")
    print(f"  Value: {result}")
    
    # Test 2: Google Web
    print("\n" + "="*70)
    print("TEST 2: Google Web Search")
    print("="*70)
    
    print(f"\nBuscando: {company} en {city}")
    print(f"Esperando: Teléfono, website, dirección")
    
    result = scraper.search_google_web(company, city)
    print(f"\nResultado:")
    print(f"  Type: {type(result)}")
    print(f"  Value: {result}")
    
    # Test 3: Website extraction
    print("\n" + "="*70)
    print("TEST 3: Website Search para obtener URL")
    print("="*70)
    
    company2 = "Veterinaria Medellín"
    print(f"\nBuscando website para: {company2}")
    result = scraper.search_google_web(company2, "Medellin")
    if result and result.get('website'):
        print(f"Website encontrado: {result['website']}")
        
        # Intenta extraer del website
        print(f"\nDescargando website...")
        import requests
        resp = requests.get(result['website'], timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Content-Length: {len(resp.text)}")
        print(f"Primera línea del HTML:")
        print(resp.text[:200])

if __name__ == '__main__':
    debug_search()
