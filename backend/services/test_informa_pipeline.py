#!/usr/bin/env python3
"""
Test completo del flujo: La República -> Informa Colombia -> DuckDuckGo
Valida la extracción de 10 empresas del nicho 'veterinarias'.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Añadir el backend al path para poder importar los servicios
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.scraper_la_republica import EmpresasLaRepublicaScraper
from services.scraper_automatico import AutomaticDataScraper

# Configuración de logs limpia para el test
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_full_test():
    niche = 'veterinarias'
    limit = 10
    
    print("\n" + "="*80)
    print(f"INICIANDO TEST DE FLUJO COMPLETO: {niche.upper()}")
    print("Fuentes: La República (Sitemaps) -> Informa Colombia (Directorio) -> DuckDuckGo")
    print("="*80)
    
    # 1. Obtener empresas base desde La República
    print(f"\n[1/2] Buscando empresas base en La República...")
    republica = EmpresasLaRepublicaScraper()
    # search_niche ya filtra por palabras clave
    companies_found = republica.search_niche(niche)
    
    if not companies_found:
        print("❌ No se encontraron empresas en La República.")
        return

    test_batch = companies_found[:limit]
    print(f"✅ Encontradas {len(companies_found)} empresas. Procesando las primeras {len(test_batch)}...")
    
    # 2. Enriquecer con AutomaticDataScraper (que ahora usa Informa Colombia)
    print("\n[2/2] Enriqueciendo datos con Informa Colombia y Fallbacks...")
    enricher = AutomaticDataScraper()
    
    final_results = []
    
    for i, company in enumerate(test_batch, 1):
        raw_name = company.get('name', 'N/A')
        # Limpiar nombre para la búsqueda (quitar NIT si está pegado)
        name = raw_name.split('-')[0].strip()
        city = company.get('city', 'Colombia')
        
        print(f"\n---> [{i}/{len(test_batch)}] {name} ({city})")
        
        try:
            # Llamada al scraper que orquesta la búsqueda en Informa y DuckDuckGo
            data = enricher.scrape_company(i, name, city)
            
            lead = {
                "nro": i,
                "empresa": name,
                "ciudad": city,
                "telefono": data.get('phone') or 'N/A',
                "nit": data.get('nit') or 'N/A',
                "website": data.get('website') or 'N/A',
                "actividad": data.get('activity') or 'N/A',
                "empleados": data.get('employees') or 'N/A',
                "estado_legal": data.get('legal_status') or 'N/A',
                "fuentes": data.get('sources', [])
            }
            final_results.append(lead)
            
            print(f"     📱 Tel: {lead['telefono']} |  NIT: {lead['nit']}")
            print(f"     🏢 Act: {lead['actividad'][:60]}...")
            print(f"     👥 Emp: {lead['empleados']} | ⚖️ Estado: {lead['estado_legal']}")
            print(f"     🔍 Fuentes: {', '.join(lead['fuentes'])}")
            
        except Exception as e:
            print(f"     ⚠️ Error: {e}")

    print("\n" + "="*80)
    print("REPORTE FINAL DE DATOS EXTRAÍDOS")
    print("="*80)
    print(json.dumps(final_results, indent=2, ensure_ascii=False))
    print("="*80 + "\n")

if __name__ == "__main__":
    run_full_test()