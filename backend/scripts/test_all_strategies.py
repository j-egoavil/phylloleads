#!/usr/bin/env python3
"""
🧪 TEST COMPARATIVO: 3 ESTRATEGIAS
- Estrategia 4: URL Directa (sin búsqueda)
- Estrategia 2: Búsqueda con requests + BeautifulSoup
- Estrategia 1: Búsqueda + Selenium
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
import time
from services.informacolombia_scraper import InformaColombiaScraper

logging.basicConfig(level=logging.INFO, format='%(message)s')

TEST_COMPANIES = [
    {'name': 'Veterinarias SAS'},
    {'name': 'Distribuciones Veterinarias SA SoC'},
    {'name': 'Soluciones Veterinarias Zona Bananera SAS'},
]

def test_all_strategies():
    scraper = InformaColombiaScraper()
    
    print("\n" + "="*120)
    print("🧪 TEST COMPARATIVO: 3 ESTRATEGIAS ANTI-CAPTCHA")
    print("="*120)
    
    results = {
        'e4_success': 0,
        'e4_failed': 0,
        'e2_success': 0,
        'e2_failed': 0,
        'e1_success': 0,
        'e1_failed': 0,
    }
    
    for i, company in enumerate(TEST_COMPANIES, 1):
        print(f"\n{'─'*120}")
        print(f"Empresa {i}/3: {company['name']}")
        print(f"{'─'*120}\n")
        
        # ESTRATEGIA 4: URL DIRECTA
        print("  🚀 E4: URL Directa (sin búsqueda, sin Selenium)")
        start = time.time()
        data_e4, result_e4 = scraper.scrape_by_direct_url(company['name'])
        time_e4 = time.time() - start
        
        if data_e4:
            print(f"     ✅ ÉXITO en {time_e4:.2f}s | NIT: {data_e4.get('nit') or '❌'} | Tel: {data_e4.get('phone') or '❌'}")
            results['e4_success'] += 1
        else:
            print(f"     ❌ FALLÓ ({result_e4})")
            results['e4_failed'] += 1
        
        # ESTRATEGIA 2: BÚSQUEDA CON REQUESTS
        print("\n  🚀 E2: Búsqueda con requests + BeautifulSoup")
        start = time.time()
        data_e2, result_e2 = scraper.scrape_by_search_requests(company['name'])
        time_e2 = time.time() - start
        
        if data_e2:
            print(f"     ✅ ÉXITO en {time_e2:.2f}s | NIT: {data_e2.get('nit') or '❌'} | Tel: {data_e2.get('phone') or '❌'}")
            results['e2_success'] += 1
        else:
            print(f"     ❌ FALLÓ ({result_e2})")
            results['e2_failed'] += 1
        
        print()
    
    print("\n" + "="*120)
    print("📊 RESUMEN FINAL")
    print("="*120 + "\n")
    
    total_e4 = results['e4_success'] + results['e4_failed']
    total_e2 = results['e2_success'] + results['e2_failed']
    
    print(f"  ESTRATEGIA 4 (URL Directa):")
    print(f"    ✅ Éxitos: {results['e4_success']}/{total_e4} ({(results['e4_success']/total_e4*100):.0f}%)")
    
    print(f"\n  ESTRATEGIA 2 (Búsqueda Requests):")
    print(f"    ✅ Éxitos: {results['e2_success']}/{total_e2} ({(results['e2_success']/total_e2*100):.0f}%)")
    
    print(f"\n  ESTRATEGIA 1 (Selenium) - ver orquestador")
    
    total_combined = results['e4_success'] + results['e2_success']
    print(f"\n  ✨ ÉXITO HÍBRIDO (E4 + E2): {total_combined}/3 ({(total_combined/3*100):.0f}%)")
    
    print("\n" + "="*120)

if __name__ == '__main__':
    test_all_strategies()
