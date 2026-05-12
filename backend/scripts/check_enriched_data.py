#!/usr/bin/env python3
"""Script para ver datos enriquecidos de las 10 empresas veterinarias"""

import sqlite3
import os

db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
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
print(f"Total: {len(results)} empresas\n")

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
    print(f"   Sitio web: {website}")
    print(f"   Dirección: {address}")
    print()

print(f"\n--- RESUMEN ---")
print(f"Total empresas: {len(results)}")
print(f"Con sitio web: {websites_count}")
print(f"Con dirección: {address_count}")
print(f"Activas: {active_count}")
print(f"Inactivas: {len(results) - active_count}")

conn.close()
