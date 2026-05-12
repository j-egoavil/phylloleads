#!/usr/bin/env python3
"""Clean DB and re-run scraper with improved address extraction"""

import sqlite3
import os
import sys

# Setup paths
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(backend_path))
os.chdir(os.path.dirname(backend_path))

# Limpiar BD
db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
print(f"Database path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM company_details")
    cursor.execute("DELETE FROM companies")
    conn.commit()
    conn.close()
    print("✓ Database cleaned")
except Exception as e:
    print(f"Error cleaning DB: {e}")

# Extraer empresas de La República
print("\n--- Extracting companies from La República ---")
from backend.services.scraper_la_republica import EmpresasLaRepublicaScraper
scraper = EmpresasLaRepublicaScraper(headless=True, max_sitemaps=1)
result = scraper.scrape_and_save('veterinarias', keywords=['veterinaria'])
print(f"Extracted: {result['total_companies']} companies")

# Ejecutar scraper automático
print("\n--- Running automatic scraper (improved address extraction) ---")
os.environ['PYTHONPATH'] = '/f/repos/phylloleads/backend'
from backend.services.scraper_automatico import AutomaticDataScraper
scraper_auto = AutomaticDataScraper(db_path=db_path)
result = scraper_auto.process_companies(limit=10)
print(f"Processed: {result['total']} companies")
print(f"Successful: {result['processed']}")

# Mostrar resultados
print("\n--- Results with improved extraction ---")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('''
SELECT c.id, c.name, c.is_active, cd.phone, cd.website, cd.address
FROM companies c
LEFT JOIN company_details cd ON c.id = cd.company_id
WHERE c.search_niche = "veterinarias"
ORDER BY c.id
LIMIT 10
''')

results = cursor.fetchall()
print(f"\nTotal: {len(results)} empresas\n")

websites_count = 0
address_count = 0
active_count = 0

for row in results:
    phone = row['phone'] if row['phone'] and row['phone'] != 'N/A' else 'N/A'
    website = row['website'] if row['website'] and row['website'] != 'N/A' else 'N/A'
    address = row['address'] if row['address'] and row['address'] != 'N/A' else 'N/A'
    active = "✓ Activa" if row['is_active'] else "✗ Inactiva"
    
    if website != 'N/A':
        websites_count += 1
    if address != 'N/A':
        address_count += 1
    if row['is_active']:
        active_count += 1
    
    print(f"{row['id']}. {row['name']}")
    print(f"   Estado: {active}")
    print(f"   Teléfono: {phone}")
    print(f"   Dirección: {address}")
    print()

print(f"\n--- RESUMEN ---")
print(f"Total empresas: {len(results)}")
print(f"Con dirección: {address_count} (mejorado)")
print(f"Con sitio web: {websites_count}")
print(f"Activas: {active_count}")
print(f"Inactivas: {len(results) - active_count}")

conn.close()
