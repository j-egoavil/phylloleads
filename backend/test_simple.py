"""
PRUEBA SIMPLIFICADA - Scraper Mock (sin Selenium)
Simula la búsqueda de datos para mostrar exactamente cómo se estructuran
"""

import json
import os
import csv
from datetime import datetime

# Datos simulados de empresas encontradas
MOCK_COMPANIES = [
    {
        "name": "JAH PET CLINICA VETERINARIA S.A.S.",
        "url": "https://empresas.larepublica.co/colombia/bolivar/cartagena/jah-pet-clinica-veterinaria-s-a-s-901531076",
        "nit": "901531076",
        "rues": "901531076",
        "city": "cartagena",
        "is_active": True,
        "status": "Activa",
        "company_size": "Pequeña",
        "search_niche": "veterinarias",
        "scraped_at": datetime.now().isoformat(),
        "raw_html": "<a class='result-item' href='/...'>...</a>"
    },
    {
        "name": "VETERINARIA EL PARAÍSO LIMITADA",
        "url": "https://empresas.larepublica.co/colombia/bogota/usaquen/veterinaria-el-paraiso-limitada-800123456",
        "nit": "800123456",
        "rues": "800123456",
        "city": "bogota",
        "is_active": True,
        "status": "Activa",
        "company_size": "Mediana",
        "search_niche": "veterinarias",
        "scraped_at": datetime.now().isoformat(),
        "raw_html": "<a class='result-item' href='/...'>...</a>"
    },
    {
        "name": "CLÍNICA VETERINARIA MONTE VERDE S.A.",
        "url": "https://empresas.larepublica.co/colombia/antioquia/medellin/clinica-veterinaria-monte-verde-s-a-900234567",
        "nit": "900234567",
        "rues": "900234567",
        "city": "medellin",
        "is_active": True,
        "status": "Activa",
        "company_size": "Mediana",
        "search_niche": "veterinarias",
        "scraped_at": datetime.now().isoformat(),
        "raw_html": "<a class='result-item' href='/...'>...</a>"
    },
    {
        "name": "VETERINARIA CENTRAL MASCOTAS PEP",
        "url": "https://empresas.larepublica.co/colombia/valle/cali/veterinaria-central-mascotas-pep-700345678",
        "nit": "700345678",
        "rues": "700345678",
        "city": "cali",
        "is_active": False,
        "status": "Inactiva",
        "company_size": "Pequeña",
        "search_niche": "veterinarias",
        "scraped_at": datetime.now().isoformat(),
        "raw_html": "<a class='result-item' href='/...'>...</a>"
    },
    {
        "name": "VET CLINIC BARRANQUILLA DOGS & CATS",
        "url": "https://empresas.larepublica.co/colombia/atlantico/barranquilla/vet-clinic-barranquilla-800456789",
        "nit": "800456789",
        "rues": "800456789",
        "city": "barranquilla",
        "is_active": True,
        "status": "Activa",
        "company_size": "Pequeña",
        "search_niche": "veterinarias",
        "scraped_at": datetime.now().isoformat(),
        "raw_html": "<a class='result-item' href='/...'>...</a>"
    },
    {
        "name": "CENTRO VETERINARIO ESPECIALIZADO BOGOTÁ",
        "url": "https://empresas.larepublica.co/colombia/bogota/chapinero/centro-veterinario-especializado-850567890",
        "nit": "850567890",
        "rues": "850567890",
        "city": "bogota",
        "is_active": True,
        "status": "Activa",
        "company_size": "Grande",
        "search_niche": "veterinarias",
        "scraped_at": datetime.now().isoformat(),
        "raw_html": "<a class='result-item' href='/...'>...</a>"
    },
]

def test_scraper_mock():
    """
    Prueba simulada del scraper - muestra dónde quedan los datos
    """
    
    print("\n" + "="*90)
    print("🔍 SCRAPER LA REPÚBLICA - PRUEBA SIMULADA (SIN BASE DE DATOS)")
    print("="*90)
    
    # Crear carpeta de resultados
    results_dir = "test_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"\n📁 Carpeta creada: {os.path.abspath(results_dir)}")
    else:
        print(f"\n📁 Carpeta: {os.path.abspath(results_dir)}")
    
    niche = "veterinarias"
    companies = MOCK_COMPANIES
    
    print(f"\n✅ Simulada búsqueda: '{niche}'")
    print(f"✅ Empresas encontradas: {len(companies)}\n")
    
    # ========================================================================
    # 1. GUARDAR EN JSON
    # ========================================================================
    print("\n" + "-"*90)
    print("1️⃣  GUARDAR EN JSON")
    print("-"*90)
    
    json_filename = os.path.join(
        results_dir, 
        f"{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(json_filename)
    print(f"\n📄 Archivo JSON guardado:")
    print(f"   Ruta: {json_filename}")
    print(f"   Tamaño: {file_size} bytes ({file_size / 1024:.2f} KB)")
    
    # Mostrar contenido del JSON
    print(f"\n📋 Contenido (primeras 2 empresas):\n")
    with open(json_filename, 'r', encoding='utf-8') as f:
        content = json.load(f)
        print(json.dumps(content[:2], indent=2, ensure_ascii=False))
    
    # ========================================================================
    # 2. GUARDAR EN CSV
    # ========================================================================
    print("\n" + "-"*90)
    print("2️⃣  GUARDAR EN CSV")
    print("-"*90)
    
    csv_filename = os.path.join(
        results_dir,
        f"{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'nit', 'rues', 'city', 'status', 'company_size', 'url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for company in companies:
            writer.writerow({
                'name': company['name'],
                'nit': company.get('nit', 'N/A'),
                'rues': company.get('rues', 'N/A'),
                'city': company.get('city', 'N/A'),
                'status': company.get('status', 'N/A'),
                'company_size': company.get('company_size', 'N/A'),
                'url': company.get('url', 'N/A'),
            })
    
    file_size = os.path.getsize(csv_filename)
    print(f"\n📊 Archivo CSV guardado:")
    print(f"   Ruta: {csv_filename}")
    print(f"   Tamaño: {file_size} bytes ({file_size / 1024:.2f} KB)")
    
    # Mostrar contenido del CSV
    print(f"\n📋 Contenido (primeras 3 filas):\n")
    with open(csv_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:4]
        for line in lines:
            print(f"   {line.rstrip()}")
    
    # ========================================================================
    # 3. MOSTRAR DATOS EN CONSOLA
    # ========================================================================
    print("\n" + "-"*90)
    print("3️⃣  DATOS EXTRAÍDOS")
    print("-"*90)
    
    print(f"\n📊 Total: {len(companies)} empresas\n")
    
    for i, company in enumerate(companies, 1):
        print(f"{i}. {company['name']}")
        print(f"   └─ RUES: {company['rues']}")
        print(f"   └─ Ciudad: {company['city']}")
        print(f"   └─ Estado: {company['status']}")
        print(f"   └─ Tamaño: {company['company_size']}")
        print(f"   └─ URL: {company['url'][:70]}...")
        print()
    
    # ========================================================================
    # 4. ESTADÍSTICAS
    # ========================================================================
    print("-"*90)
    print("4️⃣  ESTADÍSTICAS")
    print("-"*90)
    
    active = sum(1 for c in companies if c.get('is_active'))
    inactive = len(companies) - active
    
    print(f"\n📈 Estado:")
    print(f"   ✅ Activas: {active} ({(active/len(companies)*100):.1f}%)")
    print(f"   ❌ Inactivas: {inactive} ({(inactive/len(companies)*100):.1f}%)")
    
    # Por tamaño
    sizes = {}
    for company in companies:
        size = company.get('company_size', 'Desconocida')
        sizes[size] = sizes.get(size, 0) + 1
    
    print(f"\n📏 Por tamaño:")
    for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {size}: {count} ({(count/len(companies)*100):.1f}%)")
    
    # Por ciudad
    cities = {}
    for company in companies:
        city = company.get('city', 'Desconocida')
        cities[city] = cities.get(city, 0) + 1
    
    print(f"\n🏙️  Por ciudad:")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {city}: {count} ({(count/len(companies)*100):.1f}%)")
    
    # ========================================================================
    # 5. INFORMACIÓN DE BASE DE DATOS
    # ========================================================================
    print("\n" + "-"*90)
    print("5️⃣  CON BASE DE DATOS POSTGRESQL")
    print("-"*90)
    
    print(f"""
Si tuvieras PostgreSQL corriendo, los datos se guardarían así:

📊 Tabla: companies
   Registros: {len(companies)} filas insertadas
   
   Estructura:
   ┌─────────────┬──────────────────────────────────┐
   │ Column      │ Type                             │
   ├─────────────┼──────────────────────────────────┤
   │ id          │ SERIAL PRIMARY KEY               │
   │ name        │ VARCHAR(500) - "{companies[0]['name'][:30]}..." │
   │ url         │ VARCHAR(1000) - Unique           │
   │ rues        │ VARCHAR(100)  - "{companies[0]['rues']}"  │
   │ city        │ VARCHAR(200)  - "{companies[0]['city']}"  │
   │ is_active   │ BOOLEAN       - {companies[0]['is_active']}               │
   │ status      │ VARCHAR(50)   - "{companies[0]['status']}"    │
   │ company_size│ VARCHAR(50)   - "{companies[0]['company_size']}"           │
   │ search_niche│ VARCHAR(200)  - "{companies[0]['search_niche']}"        │
   │ scraped_at  │ TIMESTAMP     - {companies[0]['scraped_at'][:19]} │
   │ created_at  │ TIMESTAMP     - Automático      │
   │ updated_at  │ TIMESTAMP     - Automático      │
   └─────────────┴──────────────────────────────────┘

Query de ejemplo:
   SELECT * FROM companies WHERE search_niche = 'veterinarias' AND is_active = true;
   → Resultado: {active} empresas activas
""")
    
    # ========================================================================
    # 6. RESUMEN FINAL
    # ========================================================================
    print("-"*90)
    print("✅ RESUMEN FINAL")
    print("-"*90)
    
    print(f"""
📁 ARCHIVOS GUARDADOS:
   
   1. JSON: {json_filename}
      └─ Estructura: Cada empresa es un objeto con todos sus campos
      └─ Uso: Para APIs, importaciones, etc.
   
   2. CSV: {csv_filename}
      └─ Estructura: Filas y columnas (Excel-compatible)
      └─ Uso: Para análisis en Excel, Power BI, etc.

📊 DATOS EN MEMORIA:
   
   - Total: {len(companies)} empresas
   - Activas: {active}
   - Inactivas: {inactive}
   - Ciudades: {len(cities)}
   - Tamaños: {len(sizes)}

🔗 EN PRODUCCIÓN (Con PostgreSQL + API REST):
   
   1. Los datos se guardan en la tabla 'companies'
   2. Se consultan vía API REST:
      - POST /api/search → Busca y guarda
      - GET /api/companies/veterinarias → Obtiene guardadas
      - GET /api/stats → Estadísticas
   3. El frontend muestra los datos en tablas filtradas

🎯 PRÓXIMOS PASOS:
   
   □ Configurar PostgreSQL
   □ Ejecutar: docker-compose up --build
   □ Hacer búsqueda real (será más lenta porque usa Selenium)
   □ Verificar datos en http://localhost:8000/docs
""")
    
    print("\n" + "="*90)
    print("✅ PRUEBA COMPLETADA")
    print("="*90 + "\n")
    
    return {
        "success": True,
        "total": len(companies),
        "json_file": json_filename,
        "csv_file": csv_filename,
        "results_dir": os.path.abspath(results_dir),
    }

if __name__ == "__main__":
    result = test_scraper_mock()
    print(f"\n📁 Abre la carpeta para ver los archivos: {result['results_dir']}")
