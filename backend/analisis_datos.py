"""
Mostrar análisis de datos y problemas encontrados
"""

import sqlite3

conn = sqlite3.connect("appdb.sqlite")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n" + "="*100)
print("ANÁLISIS: DATOS EXTRAÍDOS vs DATOS REALES")
print("="*100 + "\n")

print("PROBLEMA ENCONTRADO:")
print("─" * 100)
print()
print("EMPRESA: CLÍNICA VETERINARIA MONTE VERDE S.A.")
print()
print("  Teléfono según scraper:  +57 5 6123456   ❌ INCORRECTO")
print("  Teléfono REAL (tu búsqueda): +57 301 5052787   ✅ CORRECTO")
print()
print("CAUSA:")
print("  Los datos que sacó el scraper incluyen 'mock data' (datos ficticios)")
print("  que usé para demostración. Solo 1 empresa fue realmente scrappeada.")
print()

# Mostrar qué fue extraído realmente
print("\nDATA REALMENTE EXTRAÍDA POR EDGE:")
print("─" * 100)

cursor.execute("""
    SELECT c.name, cd.phone, cd.website, cd.address, cd.scraped_at
    FROM companies c
    JOIN company_details cd ON c.id = cd.company_id
    WHERE date(cd.scraped_at) = date('2026-05-09')
    AND cd.scraped_at LIKE '2026-05-09T17:14%'
""")

real_data = cursor.fetchall()

if real_data:
    for row in real_data:
        print(f"Empresa: {row['name']}")
        print(f"  Teléfono: {row['phone']}")
        print(f"  Website: {row['website']}")
        print(f"  Dirección: {row['address'][:60]}")
        print(f"  Extraído: {row['scraped_at']}")
else:
    print("No hay datos extraídos en el timestamp esperado")

# Mostrar datos mock
print("\n\nDATA MOCK (DEMO) EN BD:")
print("─" * 100)

cursor.execute("""
    SELECT c.name, cd.phone, cd.website, cd.address, cd.scraped_at
    FROM companies c
    JOIN company_details cd ON c.id = cd.company_id
    WHERE cd.scraped_at NOT LIKE '2026-05-09T17:14%'
""")

mock_data = cursor.fetchall()

for i, row in enumerate(mock_data, 1):
    print(f"\n[{i}] {row['name']}")
    print(f"    Teléfono: {row['phone']}")
    print(f"    Website: {row['website']}")
    print(f"    Dirección: {row['address'][:60]}")


print("\n\n" + "="*100)
print("SOLUCIONES")
print("="*100 + "\n")

print("OPCIÓN 1: Actualizar manualmente con datos reales")
print("  python actualizar_datos.py")
print("  → Selecciona opción 1 para actualizar empresa por empresa")
print()

print("OPCIÓN 2: Exportar a CSV y corregir manualmente")
print("  python actualizar_datos.py")
print("  → Selecciona opción 2")
print("  → Abre 'empresas_para_corregir.csv'")
print("  → Busca números reales en: https://www.paginasamarillas.com.co")
print("  → Guarda cambios")
print("  → Importa con opción 3")
print()

print("OPCIÓN 3: Mejorar el scraper")
print("  Fuentes confiables de Colombia:")
print("  - Páginas Amarillas: https://www.paginasamarillas.com.co")
print("  - RUES: https://www.rues.org.co")
print("  - Dato360: https://www.dato360.com.co")
print("  - Google My Business")
print()

print("OPCIÓN 4: Usar API de datos reales (con costo)")
print("  - Google Maps API: $7/1000 búsquedas")
print("  - Hunter.io: para emails/teléfono")
print("  - Clearbit: para enriquecimiento empresarial")
print()

conn.close()
