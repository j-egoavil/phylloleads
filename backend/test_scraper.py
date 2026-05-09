"""
SCRIPT DE PRUEBA - Scraper sin Base de Datos
Este script demuestra el scraper SIN PostgreSQL, guardando resultados en JSON
para que veas exactamente dónde quedan los datos
"""

import json
import os
from datetime import datetime
from scraper_la_republica import EmpresasLaRepublicaScraper

def test_scraper_no_db():
    """
    Prueba del scraper sin necesidad de BD
    Guarda resultados en JSON en la carpeta 'test_results'
    """
    
    print("\n" + "="*80)
    print("🔍 SCRAPER LA REPÚBLICA - PRUEBA SIN BASE DE DATOS")
    print("="*80)
    
    # Crear carpeta de resultados
    results_dir = "test_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"\n📁 Carpeta creada: {results_dir}")
    
    # Crear scraper (sin intentar conectar a BD)
    print("\n⚙️  Inicializando scraper...")
    scraper = EmpresasLaRepublicaScraper(headless=True)
    
    # Búsqueda pequeña (1 página, pocos resultados para prueba)
    niche = "veterinarias"
    pages = 1
    
    print(f"\n🔍 Buscando: '{niche}' ({pages} página)")
    print("⏳ Esto puede tomar 30-60 segundos (respetando el servidor)...")
    
    try:
        # Obtener empresas
        companies = scraper.search_niche(niche, pages)
        
        if not companies:
            print("\n❌ No se encontraron empresas")
            return
        
        print(f"\n✅ ¡Encontradas {len(companies)} empresas!\n")
        
        # Guardar en JSON
        json_filename = os.path.join(
            results_dir, 
            f"{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Guardado en: {json_filename}")
        print(f"   Tamaño: {os.path.getsize(json_filename) / 1024:.2f} KB")
        
        # Mostrar datos
        print("\n" + "="*80)
        print("📋 DATOS EXTRAÍDOS:")
        print("="*80)
        
        for i, company in enumerate(companies[:5], 1):
            print(f"\n{i}. {company['name']}")
            print(f"   └─ RUES: {company['rues']}")
            print(f"   └─ Ciudad: {company['city']}")
            print(f"   └─ Estado: {company['status']}")
            print(f"   └─ Tamaño: {company['company_size']}")
            print(f"   └─ URL: {company['url']}")
            print(f"   └─ Scrapeado: {company['scraped_at']}")
        
        if len(companies) > 5:
            print(f"\n... y {len(companies) - 5} empresas más")
        
        # Estadísticas
        print("\n" + "="*80)
        print("📊 ESTADÍSTICAS:")
        print("="*80)
        
        active = sum(1 for c in companies if c.get('is_active'))
        inactive = len(companies) - active
        print(f"\n✅ Activas: {active}")
        print(f"❌ Inactivas: {inactive}")
        
        # Por tamaño
        sizes = {}
        for company in companies:
            size = company.get('company_size', 'Desconocida')
            sizes[size] = sizes.get(size, 0) + 1
        
        print(f"\n📏 Por tamaño:")
        for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {size}: {count}")
        
        # Por ciudad (top 5)
        cities = {}
        for company in companies:
            city = company.get('city', 'Desconocida')
            cities[city] = cities.get(city, 0) + 1
        
        print(f"\n🏙️  Top ciudades:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {city}: {count}")
        
        # Generar CSV también
        csv_filename = os.path.join(
            results_dir,
            f"{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        import csv
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'rues', 'city', 'status', 'company_size', 'url'
            ])
            writer.writeheader()
            for company in companies:
                writer.writerow({
                    'name': company['name'],
                    'rues': company.get('rues', 'N/A'),
                    'city': company.get('city', 'N/A'),
                    'status': company.get('status', 'N/A'),
                    'company_size': company.get('company_size', 'N/A'),
                    'url': company.get('url', 'N/A'),
                })
        
        print(f"\n📄 También guardado en CSV: {csv_filename}")
        
        print("\n" + "="*80)
        print("✅ PRUEBA COMPLETADA")
        print("="*80)
        print(f"\n📁 Archivos guardados en: {os.path.abspath(results_dir)}")
        print(f"   - {os.path.basename(json_filename)} (JSON)")
        print(f"   - {os.path.basename(csv_filename)} (CSV)")
        
        print("\n🎯 Con Base de Datos:")
        print("   Estos mismos datos se guardarían en PostgreSQL en la tabla 'companies'")
        print("   Y podrían consultarse por API REST")
        
        return {
            "success": True,
            "total": len(companies),
            "json_file": json_filename,
            "csv_file": csv_filename,
            "companies": companies
        }
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = test_scraper_no_db()
    print("\n")
