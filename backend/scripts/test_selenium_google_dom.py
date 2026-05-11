#!/usr/bin/env python3
"""
Test: Selenium + Google Search DOM Extraction
- Buscar en Google con Selenium
- Renderizar JavaScript
- Extraer teléfono/website/dirección del DOM
- Sin API, sin Páginas Amarillas
"""

import sys
import os
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.scraper_la_republica import EmpresasLaRepublicaScraper
from services.scraper_automatico import AutomaticDataScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    niche = 'veterinarias'
    target = 10
    
    print(f"\n{'='*70}")
    print(f"Test: Selenium + Google Search DOM")
    print(f"Pipeline: Google Web (Selenium) | Website Fallback")
    print(f"{'='*70}")
    print(f"Niche: {niche.upper()}")
    print(f"Limite: {target} empresas")
    print(f"{'='*70}\n")
    
    # PASO 1: Obtener empresas
    print(f"[1/3] Descargando {target} empresas de La Republica...")
    republica_scraper = EmpresasLaRepublicaScraper()
    companies = republica_scraper.search_niche(niche, keywords=[niche])
    
    if not companies:
        print(f"No se encontraron empresas")
        return
    
    companies = companies[:target]
    print(f"OK - {len(companies)} empresas obtenidas\n")
    
    # PASO 2: Enriquecer
    print(f"[2/3] Enriqueciendo con informacion de contacto...")
    enricher = AutomaticDataScraper()
    enriched = []
    
    for idx, company in enumerate(companies, 1):
        company_name = company.get('name', '').split('-')[0].strip()
        city = company.get('city', 'Unknown')
        
        print(f"   [{idx}/10] {company_name}...", end="", flush=True)
        
        try:
            contact_info = enricher.scrape_company(idx, company_name, city)
            
            enriched_item = {
                'name': company_name,
                'city': city,
                'phone': contact_info.get('phone') or 'N/A',
                'website': contact_info.get('website') or 'N/A',
                'address': contact_info.get('address') or 'N/A',
                'sources': contact_info.get('sources', []),
                'status': contact_info.get('status', 'partial')
            }
            enriched.append(enriched_item)
            print(f" OK")
        except Exception as e:
            print(f" ERROR - {str(e)[:30]}")
    
    # Cerrar driver
    if enricher.driver:
        enricher.driver.quit()
    
    # PASO 3: Metricas
    print(f"\n[3/3] Calculando metricas...\n")
    
    with_phone = sum(1 for e in enriched if e['phone'] != 'N/A')
    with_website = sum(1 for e in enriched if e['website'] != 'N/A')
    with_address = sum(1 for e in enriched if e['address'] != 'N/A')
    
    gestores = sum(1 for e in enriched if any(h in (e['website'] or '').lower() for h in ['gurusoluciones', 'wix', 'godaddy', 'wordpress']))
    
    sources_count = {}
    for e in enriched:
        for src in e['sources']:
            sources_count[src] = sources_count.get(src, 0) + 1
    
    summary = {
        'estrategia': 'Selenium + Google Search DOM',
        'niche': niche,
        'total': len(enriched),
        'with_phone': f"{with_phone}/{len(enriched)}",
        'with_website': f"{with_website}/{len(enriched)}",
        'with_address': f"{with_address}/{len(enriched)}",
        'gestores_detectados': gestores,
        'success_phone': f"{(with_phone/len(enriched)*100):.0f}%",
        'success_website': f"{(with_website/len(enriched)*100):.0f}%",
        'success_address': f"{(with_address/len(enriched)*100):.0f}%",
        'fuentes_utilizadas': sources_count,
        'telefonos_unicos': len(set([e['phone'] for e in enriched if e['phone'] != 'N/A'])),
        'sample': enriched[:5]
    }
    
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print(f"\n{'='*70}")
    if gestores > 0:
        print(f"ALERTA: {gestores} websites son gestores")
    else:
        print(f"OK - Sin gestores detectados")
    
    phones = [e['phone'] for e in enriched if e['phone'] != 'N/A']
    if phones:
        if len(set(phones)) == len(phones):
            print(f"OK - Todos los telefonos son unicos")
        else:
            print(f"ALERTA - Telefonos duplicados ({len(phones) - len(set(phones))} repetidos)")
    else:
        print(f"ALERTA - No se extrajeron telefonos")
    
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
