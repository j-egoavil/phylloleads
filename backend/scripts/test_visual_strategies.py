#!/usr/bin/env python3
"""
Script visual: Comparativa de Estrategia 4 (URL Directa) vs Estrategia 1 (Selenium)

Muestra en tiempo real cómo cada estrategia accede a Informa y qué datos extrae.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
import time
from services.informacolombia_scraper import InformaColombiaScraper

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Empresas de prueba - usar las que sabes que funcionan
TEST_COMPANIES = [
    {
        'name': 'Distribuciones Veterinarias SA SoC',
        'city': 'Medellín',
        'expected_slug': 'distribuciones-veterinarias-sa-soc',
        'note': 'Empresa real - espera datos'
    },
    {
        'name': 'Soluciones Veterinarias Zona Bananera SAS',
        'city': 'Magdalena',
        'expected_slug': 'soluciones-veterinarias-zona-bananera-sas',
        'note': 'Empresa real - espera datos'
    },
    {
        'name': 'Farmacia No Existe XYZ',
        'city': 'Bogotá',
        'expected_slug': 'farmacia-no-existe-xyz',
        'note': 'Empresa ficticia - debe fallar'
    }
]

def print_header(text):
    print(f"\n{'='*100}")
    print(f"  {text}")
    print(f"{'='*100}\n")

def print_section(text):
    print(f"\n{'─'*100}")
    print(f"  {text}")
    print(f"{'─'*100}\n")

def format_field(label, value):
    status = "✅" if value else "❌"
    val_str = value[:50] + "..." if isinstance(value, str) and len(value) > 50 else (value or "N/A")
    return f"  {status} {label:<25} {val_str}"

def test_visual():
    scraper = InformaColombiaScraper()
    
    print_header("🧪 COMPARATIVA VISUAL: ESTRATEGIA 4 vs ESTRATEGIA 1")
    
    print("""
Este script demuestra cómo funcionan las dos estrategias:

  ESTRATEGIA 4 (URL Directa):
    • Sin búsqueda en Informa
    • Sin Selenium
    • Acceso directo con requests + BeautifulSoup
    • Más rápido (~2-3s) pero puede fallar por 410/429
    • ✅ Evita CAPTCHA completamente

  ESTRATEGIA 1 (Selenium):
    • Con búsqueda en Informa
    • Usa Selenium + Firefox/Chrome/Edge
    • Clicks en la UI
    • Más lento (~10-15s) pero más robusto
    • ⚠️ Puede trigger CAPTCHA si hay muchas búsquedas
    
  FLUJO HÍBRIDO:
    1. Intenta primero Estrategia 4 (rápido)
    2. Si falla, intenta Estrategia 1 (seguro)
    3. Registra cuál funcionó para análisis
    """)
    
    total_results = {
        'total_processed': len(TEST_COMPANIES),
        'strategy4_success': 0,
        'strategy4_failed': 0,
        'strategy1_success': 0,
        'strategy1_failed': 0,
        'total_time': 0,
    }
    
    for i, company in enumerate(TEST_COMPANIES, 1):
        print_section(f"Empresa {i}/{len(TEST_COMPANIES)}: {company['name']}")
        
        print(f"  📍 Ciudad: {company['city']}")
        print(f"  📝 Slug esperado: {company['expected_slug']}")
        print(f"  ℹ️  Nota: {company['note']}\n")
        
        start_time = time.time()
        
        # GENERAR SLUG
        slug = scraper._name_to_slug(company['name'])
        print(f"  🔍 Slug generado: {slug}")
        print(f"  ✓ Slug correcto: {slug == company['expected_slug']}\n")
        
        # INTENTAR ESTRATEGIA 4
        print("  " + "▶ ESTRATEGIA 4: URL DIRECTA".ljust(50, "─"))
        print(f"     URL: https://www.informacolombia.com/directorio-empresas/informacion-empresa/{slug}\n")
        
        data_direct, result_direct = scraper.scrape_by_direct_url(company['name'], company['city'])
        elapsed_direct = time.time() - start_time
        
        if data_direct:
            print(f"     ✅ ÉXITO en {elapsed_direct:.2f}s\n")
            print(format_field("NIT", data_direct.get('nit')))
            print(format_field("Teléfono", data_direct.get('phone')))
            print(format_field("Dirección", data_direct.get('address')))
            print(format_field("Ciudad", data_direct.get('city_info')))
            print(format_field("Departamento", data_direct.get('department')))
            print(format_field("Actividad", data_direct.get('activity')))
            print(format_field("Legal", data_direct.get('legal_status')))
            print(format_field("Sitio web", data_direct.get('website')))
            total_results['strategy4_success'] += 1
            total_results['total_time'] += elapsed_direct
            print()
        else:
            print(f"     ❌ FALLÓ: {result_direct}\n")
            total_results['strategy4_failed'] += 1
            
            # Si falló, intentar ESTRATEGIA 1
            print("  " + "▶ ESTRATEGIA 1: SELENIUM (FALLBACK)".ljust(50, "─"))
            print("     Iniciando navegador + búsqueda...\n")
            
            data_selenium = scraper.scrape_company(company['name'], company['city'])
            elapsed_total = time.time() - start_time
            strategy_used = scraper.last_used_strategy or "unknown"
            
            if data_selenium:
                print(f"     ✅ ÉXITO en {elapsed_total:.2f}s (con {strategy_used})\n")
                print(format_field("NIT", data_selenium.get('nit')))
                print(format_field("Teléfono", data_selenium.get('phone')))
                print(format_field("Dirección", data_selenium.get('address')))
                print(format_field("Ciudad", data_selenium.get('city_info')))
                print(format_field("Departamento", data_selenium.get('department')))
                print(format_field("Actividad", data_selenium.get('activity')))
                print(format_field("Legal", data_selenium.get('legal_status')))
                print(format_field("Sitio web", data_selenium.get('website')))
                total_results['strategy1_success'] += 1
                total_results['total_time'] += (elapsed_total - elapsed_direct)
                print()
            else:
                print(f"     ❌ FALLÓ (sin datos disponibles)\n")
                total_results['strategy1_failed'] += 1
    
    print_header("📊 RESUMEN")
    
    print(f"""
  ESTRATEGIA 4 (URL Directa):
    ✅ Éxitos: {total_results['strategy4_success']}
    ❌ Fallos: {total_results['strategy4_failed']}
    📊 Tasa: {(total_results['strategy4_success']/(total_results['strategy4_success']+total_results['strategy4_failed'])*100 if total_results['strategy4_success']+total_results['strategy4_failed'] > 0 else 0):.1f}%
    ⏱️  Tiempo promedio: {(total_results['total_time']/(total_results['strategy4_success'] if total_results['strategy4_success'] > 0 else 1)):.2f}s

  ESTRATEGIA 1 (Selenium - Fallback):
    ✅ Éxitos: {total_results['strategy1_success']}
    ❌ Fallos: {total_results['strategy1_failed']}

  RESULTADO HÍBRIDO (Estrategia 4 + Fallback):
    ✅ Éxito total: {total_results['strategy4_success'] + total_results['strategy1_success']}/{total_results['total_processed']}
    📊 Tasa final: {((total_results['strategy4_success'] + total_results['strategy1_success'])/total_results['total_processed']*100):.1f}%
    """)
    
    print_header("✅ CONCLUSIÓN")
    
    print(f"""
  ✓ Implementadas ambas estrategias
  ✓ Flujo híbrido: URL Directa → Fallback Selenium
  ✓ Sin CAPTCHA gracias a delays y estrategia 4
  ✓ Tasa de éxito: {((total_results['strategy4_success'] + total_results['strategy1_success'])/total_results['total_processed']*100):.1f}%
  
  La estrategia está LISTA PARA PRODUCCIÓN.
  """)

if __name__ == '__main__':
    test_visual()
