#!/usr/bin/env python3
"""
Script E2E para probar el scraper con ambas estrategias en contexto de orquestador.

Prueba 10 empresas y muestra:
- Estrategia usada
- Datos extraídos
- Tiempo de ejecución
- Tasa de éxito
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
import time
import json
from services.informacolombia_scraper import InformaColombiaScraper

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Empresas de prueba variadas
TEST_COMPANIES = [
    {'name': 'Veterinarias SAS', 'city': 'Bogotá'},
    {'name': 'Distribuciones Veterinarias SA SoC', 'city': 'Medellín'},
    {'name': 'Soluciones Veterinarias Zona Bananera SAS', 'city': 'Magdalena'},
    {'name': 'Farmacia Santa María', 'city': 'Cali'},
    {'name': 'Repuestos Auto Directo', 'city': 'Barranquilla'},
    {'name': 'Consultora Empresarial Colombia', 'city': 'Bogotá'},
    {'name': 'Tecnologías de la Información S.A.', 'city': 'Bogotá'},
    {'name': 'Servicios de Limpieza Integral', 'city': 'Medellín'},
    {'name': 'Transportes Nacionales Ltda', 'city': 'Cali'},
    {'name': 'Alimentos Frescos del Cauca', 'city': 'Popayán'},
]

def test_e2e():
    scraper = InformaColombiaScraper()
    
    print("\n" + "="*100)
    print("🧪 PRUEBA E2E: SCRAPER CON AMBAS ESTRATEGIAS")
    print("="*100 + "\n")
    
    results_summary = {
        'total': len(TEST_COMPANIES),
        'success': 0,
        'partial': 0,
        'failed': 0,
        'strategies_used': {'direct_url': 0, 'selenium_search': 0},
        'total_time': 0,
        'companies': []
    }
    
    for i, company in enumerate(TEST_COMPANIES, 1):
        print(f"\n{'─'*100}")
        print(f"Empresa {i}/{len(TEST_COMPANIES)}: {company['name']} ({company['city']})")
        print(f"{'─'*100}")
        
        start_time = time.time()
        data = scraper.scrape_company(company['name'], company['city'])
        elapsed = time.time() - start_time
        
        strategy = scraper.last_used_strategy or "unknown"
        
        if data:
            # Contar datos extraídos
            extracted_fields = sum(1 for v in data.values() if v and isinstance(v, str))
            print(f"\n✅ ÉXITO ({extracted_fields} campos extraídos en {elapsed:.2f}s)")
            print(f"   Estrategia: {strategy}")
            print(f"   NIT: {data.get('nit') or '❌'}")
            print(f"   Teléfono: {data.get('phone') or '❌'}")
            print(f"   Dirección: {data.get('address') or '❌'}")
            print(f"   Ciudad: {data.get('city_info') or '❌'}")
            print(f"   Departamento: {data.get('department') or '❌'}")
            print(f"   Actividad: {data.get('activity') or '❌'}")
            print(f"   Legal: {data.get('legal_status') or '❌'}")
            print(f"   Sitio web: {data.get('website') or '❌'}")
            
            results_summary['success'] += 1
            results_summary['companies'].append({
                'name': company['name'],
                'status': 'success',
                'strategy': strategy,
                'time': elapsed,
                'fields': extracted_fields
            })
            
            if 'direct_url' in strategy.lower():
                results_summary['strategies_used']['direct_url'] += 1
            else:
                results_summary['strategies_used']['selenium_search'] += 1
        else:
            print(f"\n❌ FALLÓ ({elapsed:.2f}s)")
            print(f"   Estrategia: {strategy}")
            results_summary['failed'] += 1
            results_summary['companies'].append({
                'name': company['name'],
                'status': 'failed',
                'strategy': strategy,
                'time': elapsed,
                'fields': 0
            })
        
        results_summary['total_time'] += elapsed

    # Reporte final
    print("\n" + "="*100)
    print("📊 RESUMEN FINAL")
    print("="*100)
    
    print(f"\n📈 Estadísticas:")
    print(f"   Total procesadas: {results_summary['total']}")
    print(f"   Éxitos: {results_summary['success']} ({results_summary['success']/results_summary['total']*100:.1f}%)")
    print(f"   Fallos: {results_summary['failed']} ({results_summary['failed']/results_summary['total']*100:.1f}%)")
    print(f"   Tiempo total: {results_summary['total_time']:.2f}s")
    print(f"   Tiempo promedio: {results_summary['total_time']/results_summary['total']:.2f}s/empresa")
    
    print(f"\n🎯 Estrategias usadas:")
    print(f"   URL Directa: {results_summary['strategies_used']['direct_url']}")
    print(f"   Selenium: {results_summary['strategies_used']['selenium_search']}")
    
    print(f"\n📋 Detalle por empresa:")
    print(f"{'Empresa':<40} {'Status':<10} {'Estrategia':<30} {'Campos':<8} {'Tiempo':<8}")
    print(f"{'-'*40} {'-'*10} {'-'*30} {'-'*8} {'-'*8}")
    for comp in results_summary['companies']:
        status_icon = "✅" if comp['status'] == 'success' else "❌"
        strategy_short = "Direct URL" if "direct_url" in comp['strategy'].lower() else "Selenium"
        print(f"{comp['name']:<40} {status_icon:<10} {strategy_short:<30} {comp['fields']:<8} {comp['time']:<8.2f}s")
    
    print("\n" + "="*100)
    
    # Log para análisis
    with open('backend/scripts/e2e_results.json', 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Resultados guardados en backend/scripts/e2e_results.json")

if __name__ == '__main__':
    test_e2e()
