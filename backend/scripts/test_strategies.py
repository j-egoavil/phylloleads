#!/usr/bin/env python3
"""
Script para comparar estrategia 4 (URL directa) vs estrategia 1 (Selenium con búsqueda).

Prueba ambas con los URLs que mencionaste del usuario.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from services.informacolombia_scraper import InformaColombiaScraper

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Empresas de prueba (de los links que mostraste)
TEST_COMPANIES = [
    {
        'name': 'Veterinarias SAS',
        'expected_url': 'https://www.informacolombia.com/directorio-empresas/informacion-empresa/veterinarias-sas'
    },
    {
        'name': 'Distribuciones Veterinarias SA SoC',
        'expected_url': 'https://www.informacolombia.com/directorio-empresas/informacion-empresa/distribuciones-veterinarias-sa-soc'
    },
    {
        'name': 'Soluciones Veterinarias Zona Bananera SAS',
        'expected_url': 'https://www.informacolombia.com/directorio-empresas/informacion-empresa/soluciones-veterinarias-zona-bananera-sas'
    }
]

def test_strategies():
    scraper = InformaColombiaScraper()
    
    print("\n" + "="*80)
    print("🧪 PRUEBA DE ESTRATEGIAS: URL DIRECTA vs SELENIUM")
    print("="*80 + "\n")
    
    for i, company in enumerate(TEST_COMPANIES, 1):
        print(f"\n{'─'*80}")
        print(f"Empresa {i}/3: {company['name']}")
        print(f"{'─'*80}")
        
        # Generar slug esperado
        slug = scraper._name_to_slug(company['name'])
        generated_url = f"https://www.informacolombia.com/directorio-empresas/informacion-empresa/{slug}"
        
        print(f"\n📝 Slug generado: {slug}")
        print(f"🔗 URL esperada: {company['expected_url']}")
        print(f"🔗 URL generada: {generated_url}")
        print(f"✓ URLs coinciden: {company['expected_url'].lower() == generated_url.lower()}\n")
        
        # Estrategia 4: URL Directa (requests + BeautifulSoup)
        print("\n🚀 ESTRATEGIA 4: URL DIRECTA (requests + BeautifulSoup)")
        print("─" * 40)
        
        data_direct, strategy_result = scraper.scrape_by_direct_url(company['name'])
        
        if data_direct:
            print(f"✅ ÉXITO")
            print(f"   NIT: {data_direct.get('nit') or 'N/A'}")
            print(f"   Teléfono: {data_direct.get('phone') or 'N/A'}")
            print(f"   Dirección: {data_direct.get('address') or 'N/A'}")
            print(f"   Sitio web: {data_direct.get('website') or 'N/A'}")
            print(f"   Ciudad: {data_direct.get('city_info') or 'N/A'}")
            print(f"   Departamento: {data_direct.get('department') or 'N/A'}")
            print(f"   Actividad: {data_direct.get('activity') or 'N/A'}")
        else:
            print(f"❌ FALLÓ: {strategy_result}")
        
        print("\n")

    # Reporte final
    print("\n" + "="*80)
    print("📊 REPORTE DE ESTRATEGIAS")
    print("="*80)
    
    report = scraper.get_strategy_report()
    print(f"\nTotal empresas procesadas: {report['total_companies']}")
    
    direct_count = len([l for l in report['detailed_log'] if l.get('strategy') == 'direct_url'])
    print(f"\n✅ URL Directa (Estrategia 4):")
    print(f"   Éxitos: {report['direct_url_success']}/{direct_count}")
    print(f"   Tasa: {(report['direct_url_success']/direct_count*100):.1f}%" if direct_count > 0 else "   N/A")
    
    selenium_count = len([l for l in report['detailed_log'] if l.get('strategy') == 'selenium_search'])
    print(f"\n🔍 Selenium (Estrategia 1):")
    print(f"   Éxitos: {report['selenium_success']}/{selenium_count}")
    print(f"   Tasa: {(report['selenium_success']/selenium_count*100):.1f}%" if selenium_count > 0 else "   N/A")
    
    print("\n📋 Detalle por empresa:")
    for log in report['detailed_log']:
        status = "✅" if log['success'] else "❌"
        print(f"  {status} {log['company']:40} | {log['strategy']:20} | {log['result']}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_strategies()
