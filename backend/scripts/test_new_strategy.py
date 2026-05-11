#!/usr/bin/env python3
"""
Test script para validar la nueva estrategia de scraping:
- Google Maps → Google Web → La República (Sin Páginas Amarillas)
- Solo 10 empresas para pruebas rápidas
- Valida que no uses gestores de sitios
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.scraper_la_republica import EmpresasLaRepublicaScraper
from services.scraper_automatico import AutomaticDataScraper
from services.lead_scorer import LeadScorer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    niche = 'veterinarias'
    target = 10  # Solo 10 empresas
    
    print(f"\n{'='*70}")
    print(f"Test: Nueva Estrategia de Scraping - {niche.upper()}")
    print(f"{'='*70}")
    
    # PASO 1: Obtener empresas de La República
    print(f"\n[1/3] 📥 Descargando {target} empresas de La República...")
    republica_scraper = EmpresasLaRepublicaScraper()
    companies = republica_scraper.search_niche(niche, keywords=[niche])
    
    if not companies:
        print(f"❌ No se encontraron empresas")
        return
    
    # Limitar a 10
    companies = companies[:target]
    print(f"✓ {len(companies)} empresas obtenidas\n")
    
    # PASO 2: Enriquecer con contacto
    print(f"[2/3] 🔍 Enriqueciendo con información de contacto...")
    enricher = AutomaticDataScraper()
    enriched = []
    
    for idx, company in enumerate(companies, 1):
        company_name = company.get('name', '').split('-')[0].strip()
        city = company.get('city', 'Unknown')
        url = company.get('url', '')
        
        print(f"   [{idx}/10] {company_name}...", end="", flush=True)
        
        try:
            # NUEVA ESTRATEGIA: pasar URL de La República
            contact_info = enricher.scrape_company(
                idx,
                company_name,
                city,
                url  # ← URL de La República
            )
            
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
            print(f" ✓")
        except Exception as e:
            print(f" ⚠️ {str(e)[:30]}")
    
    # PASO 3: Calcular métricas
    print(f"\n[3/3] 📊 Calculando métricas...")
    
    with_phone = sum(1 for e in enriched if e['phone'] != 'N/A')
    with_website = sum(1 for e in enriched if e['website'] != 'N/A')
    with_address = sum(1 for e in enriched if e['address'] != 'N/A')
    
    # Contar gestores
    host_providers = ['gurusoluciones.com', 'wix.com', 'godaddy.com', 'wordpress.com']
    gestores = sum(1 for e in enriched if any(h in (e['website'] or '').lower() for h in host_providers))
    
    summary = {
        'niche': niche,
        'total': len(enriched),
        'with_phone': with_phone,
        'with_website': with_website,
        'with_address': with_address,
        'gestores_detectados': gestores,
        'success_rate_phone': f"{(with_phone/len(enriched)*100):.0f}%" if enriched else "0%",
        'success_rate_website': f"{(with_website/len(enriched)*100):.0f}%" if enriched else "0%",
        'sample': enriched[:3]
    }
    
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Avisar si hay gestores
    if gestores > 0:
        print(f"\n⚠️ ALERTA: {gestores} websites son de gestores de sitios (deben filtrarse)")
    else:
        print(f"\n✅ Ningún website de gestor detectado")

if __name__ == '__main__':
    main()
