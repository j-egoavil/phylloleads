"""
Ejemplos de uso del scraper de empresas.larepublica.co

Este archivo contiene ejemplos prácticos de cómo usar el scraper
tanto de forma directa como a través de la API REST.
"""

import asyncio
from scraper_la_republica import EmpresasLaRepublicaScraper
import json
import os

# ============================================================================
# EJEMPLO 1: Uso Directo del Scraper (Sin API)
# ============================================================================

def ejemplo_1_uso_directo():
    """Ejemplo básico usando el scraper directamente"""
    print("\n" + "="*80)
    print("EJEMPLO 1: Uso Directo del Scraper")
    print("="*80)
    
    # Crear instancia del scraper
    scraper = EmpresasLaRepublicaScraper(
        db_host="localhost",
        db_port=5432,
        db_name="appdb",
        db_user="postgres",
        db_password="postgres"
    )
    
    # Buscar empresas (1 página)
    print("\n🔍 Buscando veterinarias...")
    result = scraper.scrape_and_save("veterinarias", pages=1)
    
    print(f"\n✅ Resultado:")
    print(f"   - Nicho: {result['niche']}")
    print(f"   - Total encontradas: {result['total_companies']}")
    print(f"   - Éxito: {result['success']}")
    
    # Mostrar primeras 3 empresas
    if result.get('companies'):
        print(f"\n📋 Primeras 3 empresas encontradas:")
        for i, company in enumerate(result['companies'][:3], 1):
            print(f"\n   {i}. {company['name']}")
            print(f"      - URL: {company['url']}")
            print(f"      - RUES: {company['rues']}")
            print(f"      - Ciudad: {company['city']}")
            print(f"      - Estado: {company['status']}")
            print(f"      - Tamaño: {company['company_size']}")


# ============================================================================
# EJEMPLO 2: Consultar Empresas Guardadas
# ============================================================================

def ejemplo_2_consultar_guardadas():
    """Ejemplo: obtener empresas que ya fueron scrapeadas"""
    print("\n" + "="*80)
    print("EJEMPLO 2: Consultar Empresas Guardadas en Base de Datos")
    print("="*80)
    
    scraper = EmpresasLaRepublicaScraper()
    
    # Obtener empresas guardadas
    niche = "veterinarias"
    print(f"\n🔍 Consultando empresas del nicho '{niche}'...")
    
    companies = scraper.get_companies_by_niche(niche)
    
    if companies:
        print(f"\n✅ Se encontraron {len(companies)} empresas:")
        print(f"\n📊 Resumen:")
        print(f"   - Total: {len(companies)}")
        
        # Contar por estado
        active = sum(1 for c in companies if c.get('is_active'))
        inactive = len(companies) - active
        print(f"   - Activas: {active}")
        print(f"   - Inactivas: {inactive}")
        
        # Mostrar por ciudad
        cities = {}
        for company in companies:
            city = company.get('city', 'Desconocida')
            cities[city] = cities.get(city, 0) + 1
        
        print(f"\n🏙️  Empresas por ciudad:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {city}: {count}")
        
        # Mostrar por tamaño
        sizes = {}
        for company in companies:
            size = company.get('company_size', 'Desconocida')
            sizes[size] = sizes.get(size, 0) + 1
        
        print(f"\n📏 Empresas por tamaño:")
        for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {size}: {count}")
        
        # Mostrar algunos detalles
        print(f"\n📋 Muestras de empresas:")
        for i, company in enumerate(companies[:5], 1):
            print(f"\n   {i}. {company['name']}")
            print(f"      Ciudad: {company['city']}, Tamaño: {company['company_size']}")
    else:
        print(f"\n⚠️  No se encontraron empresas para '{niche}'")
        print("   Intenta scrapear primero con ejemplo_1_uso_directo()")


# ============================================================================
# EJEMPLO 3: Múltiples Búsquedas
# ============================================================================

def ejemplo_3_multiples_busquedas():
    """Ejemplo: realizar múltiples búsquedas a la vez"""
    print("\n" + "="*80)
    print("EJEMPLO 3: Múltiples Búsquedas")
    print("="*80)
    
    scraper = EmpresasLaRepublicaScraper()
    
    nichos = ["veterinarias", "farmacias", "peluquerías"]
    
    results = {}
    for niche in nichos:
        print(f"\n🔍 Buscando: {niche}...")
        try:
            result = scraper.scrape_and_save(niche, pages=1)
            results[niche] = result['total_companies']
            print(f"   ✅ {result['total_companies']} empresas encontradas")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[niche] = 0
    
    print(f"\n📊 Resumen de búsquedas:")
    for niche, count in results.items():
        print(f"   - {niche}: {count} empresas")
    
    total = sum(results.values())
    print(f"\n✅ Total: {total} empresas scrapeadas")


# ============================================================================
# EJEMPLO 4: Búsqueda Múltiples Páginas
# ============================================================================

def ejemplo_4_multiples_paginas():
    """Ejemplo: scrapear múltiples páginas de resultados"""
    print("\n" + "="*80)
    print("EJEMPLO 4: Búsqueda en Múltiples Páginas")
    print("="*80)
    
    scraper = EmpresasLaRepublicaScraper()
    
    niche = "restaurantes"
    pages = 3
    
    print(f"\n🔍 Buscando '{niche}' en {pages} páginas...")
    print("   ⏳ Esto puede tomar unos minutos...")
    
    result = scraper.scrape_and_save(niche, pages=pages)
    
    print(f"\n✅ Completado:")
    print(f"   - Total empresas: {result['total_companies']}")
    print(f"   - Guardadas en base de datos: {result['success']}")
    
    # Estadísticas
    if result.get('companies'):
        companies = result['companies']
        
        active = sum(1 for c in companies if c.get('is_active'))
        inactive = len(companies) - active
        
        print(f"\n📊 Estadísticas:")
        print(f"   - Activas: {active}")
        print(f"   - Inactivas: {inactive}")
        
        # Distribución por tamaño
        sizes = {}
        for company in companies:
            size = company.get('company_size', 'Desconocida')
            sizes[size] = sizes.get(size, 0) + 1
        
        print(f"\n📏 Distribución por tamaño:")
        for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(companies)) * 100
            print(f"   - {size}: {count} ({percentage:.1f}%)")


# ============================================================================
# EJEMPLO 5: Exportar a JSON
# ============================================================================

def ejemplo_5_exportar_json():
    """Ejemplo: exportar empresas a archivo JSON"""
    print("\n" + "="*80)
    print("EJEMPLO 5: Exportar Empresas a JSON")
    print("="*80)
    
    scraper = EmpresasLaRepublicaScraper()
    
    niche = "veterinarias"
    print(f"\n📤 Exportando empresas de '{niche}' a JSON...")
    
    companies = scraper.get_companies_by_niche(niche)
    
    if companies:
        # Guardar a archivo
        filename = f"empresas_{niche}_{len(companies)}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Archivo creado: {filename}")
        print(f"   - Total de registros: {len(companies)}")
        
        # Mostrar tamaño del archivo
        size_kb = os.path.getsize(filename) / 1024
        print(f"   - Tamaño: {size_kb:.2f} KB")
    else:
        print(f"\n⚠️  No hay empresas para exportar. Intenta scrapear primero.")


# ============================================================================
# EJEMPLO 6: Filtrar por Ciudad
# ============================================================================

def ejemplo_6_filtrar_por_ciudad():
    """Ejemplo: obtener empresas de una ciudad específica"""
    print("\n" + "="*80)
    print("EJEMPLO 6: Filtrar Empresas por Ciudad")
    print("="*80)
    
    scraper = EmpresasLaRepublicaScraper()
    
    niche = "veterinarias"
    ciudad_filtro = "bogota"
    
    print(f"\n🏙️  Filtrando empresas de '{niche}' en {ciudad_filtro}...")
    
    companies = scraper.get_companies_by_niche(niche)
    
    # Filtrar por ciudad
    filtered = [c for c in companies if c.get('city', '').lower() == ciudad_filtro.lower()]
    
    print(f"\n✅ Resultados:")
    print(f"   - Total empresas en {niche}: {len(companies)}")
    print(f"   - Empresas en {ciudad_filtro}: {len(filtered)}")
    
    if filtered:
        print(f"\n📋 Empresas en {ciudad_filtro}:")
        for i, company in enumerate(filtered[:10], 1):
            print(f"\n   {i}. {company['name']}")
            print(f"      RUES: {company['rues']}")
            print(f"      Estado: {company['status']}")
            print(f"      Tamaño: {company['company_size']}")


# ============================================================================
# EJEMPLO 7: Filtrar Empresas Activas
# ============================================================================

def ejemplo_7_filtrar_activas():
    """Ejemplo: obtener solo empresas activas"""
    print("\n" + "="*80)
    print("EJEMPLO 7: Filtrar Empresas Activas/Inactivas")
    print("="*80)
    
    scraper = EmpresasLaRepublicaScraper()
    
    niche = "restaurantes"
    
    print(f"\n🔍 Analizando estado de empresas en '{niche}'...")
    
    companies = scraper.get_companies_by_niche(niche)
    
    if not companies:
        print(f"   ⚠️  No hay datos. Intenta scrapear primero.")
        return
    
    # Separar por estado
    active = [c for c in companies if c.get('is_active')]
    inactive = [c for c in companies if not c.get('is_active')]
    
    print(f"\n✅ Resultados:")
    print(f"   - Empresas activas: {len(active)} ({(len(active)/len(companies)*100):.1f}%)")
    print(f"   - Empresas inactivas: {len(inactive)} ({(len(inactive)/len(companies)*100):.1f}%)")
    
    if inactive:
        print(f"\n⚠️  Empresas inactivas encontradas:")
        for i, company in enumerate(inactive[:5], 1):
            print(f"   {i}. {company['name']} ({company['city']})")


# ============================================================================
# MAIN - Ejecutar ejemplos
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  EJEMPLOS DE USO - SCRAPER EMPRESAS LA REPÚBLICA".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n\nElige qué ejemplo ejecutar:\n")
    print("1. Uso directo del scraper")
    print("2. Consultar empresas guardadas")
    print("3. Múltiples búsquedas")
    print("4. Búsqueda en múltiples páginas")
    print("5. Exportar a JSON")
    print("6. Filtrar por ciudad")
    print("7. Filtrar empresas activas/inactivas")
    print("0. Salir")
    
    choice = input("\n¿Qué ejemplo deseas ejecutar? (0-7): ").strip()
    
    try:
        if choice == "1":
            ejemplo_1_uso_directo()
        elif choice == "2":
            ejemplo_2_consultar_guardadas()
        elif choice == "3":
            ejemplo_3_multiples_busquedas()
        elif choice == "4":
            ejemplo_4_multiples_paginas()
        elif choice == "5":
            ejemplo_5_exportar_json()
        elif choice == "6":
            ejemplo_6_filtrar_por_ciudad()
        elif choice == "7":
            ejemplo_7_filtrar_activas()
        elif choice == "0":
            print("\n👋 ¡Hasta luego!")
        else:
            print("\n❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n\n⏸️  Ejecución cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
