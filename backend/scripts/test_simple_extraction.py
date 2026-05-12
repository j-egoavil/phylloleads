#!/usr/bin/env python3
"""Simple test of improved address extraction"""

import os
import sys
import sqlite3

# Setup paths
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(backend_path))
os.chdir(os.path.dirname(backend_path))

# Run scraper
os.environ['PYTHONPATH'] = backend_path
from services.scraper_automatico import AutomaticDataScraper

db_path = "appdb.sqlite"
print(f"Database: {db_path}\n")

scraper = AutomaticDataScraper(db_path=db_path)
result = scraper.process_companies(limit=10)

print(f"\n✓ Processed: {result['total']} companies")
print(f"✓ Successful: {result['processed']}\n")

# Show results
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    cursor.execute('''
    SELECT c.id, c.name, c.is_active, cd.phone, cd.website, cd.address
    FROM companies c
    LEFT JOIN company_details cd ON c.id = cd.company_id
    WHERE c.search_niche = "veterinarias"
    ORDER BY c.id
    LIMIT 10
    ''')

    results = cursor.fetchall()
    print(f"=== Results with Improved Address Extraction ===\n")
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
        print(f"   Tel: {phone}")
        print(f"   Dir: {address[:60] + '...' if len(str(address)) > 60 else address}")
        print()

    print(f"\n--- SUMMARY ---")
    print(f"Total empresas: {len(results)}")
    print(f"Con dirección: {address_count} (✓ IMPROVED)")
    print(f"Con sitio web: {websites_count}")
    print(f"Activas: {active_count}")

except Exception as e:
    print(f"Error querying results: {e}")

conn.close()
