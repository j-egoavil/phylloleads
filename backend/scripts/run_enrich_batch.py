#!/usr/bin/env python3
import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.scraper_automatico import AutomaticDataScraper

DB = os.getenv('APP_DB_PATH', 'appdb.sqlite')
BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 5

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute(
    """
    SELECT c.id, c.name, c.city, c.nit
    FROM companies c
    LEFT JOIN company_details cd ON cd.company_id = c.id
    WHERE c.is_active = 1
    ORDER BY c.id DESC
    LIMIT ?
    """,
    (BATCH_SIZE,),
)
companies = [dict(r) for r in cur.fetchall()]
conn.close()

if not companies:
    print("No hay empresas para procesar")
    sys.exit(0)

print(f"Empresas seleccionadas: {[c['id'] for c in companies]}")

scraper = AutomaticDataScraper(db_path=DB)
if not scraper.connect_db():
    print("No se pudo conectar a la BD")
    sys.exit(2)

results = []
try:
    scraper.driver = scraper.get_browser()

    for c in companies:
        details = scraper.scrape_company(c['id'], c['name'], c.get('city') or '', nit=c.get('nit'))
        if details:
            scraper.save_details(c['id'], details)

        row = {
            'company_id': c['id'],
            'name': c['name'],
            'phone': (details or {}).get('phone'),
            'website': (details or {}).get('website'),
            'address': (details or {}).get('address'),
            'sources': (details or {}).get('sources', []),
            'status': (details or {}).get('status'),
        }
        results.append(row)

finally:
    scraper.close_db()
    scraper.close_browser()

with_address = sum(1 for r in results if r.get('address') and str(r.get('address')).strip().lower() not in ('', 'n/a', 'none'))
with_phone = sum(1 for r in results if r.get('phone') and str(r.get('phone')).strip().lower() not in ('', 'n/a', 'none'))
with_web = sum(1 for r in results if r.get('website') and str(r.get('website')).strip().lower() not in ('', 'n/a', 'none'))

print("\n=== RESUMEN ===")
print(json.dumps({
    'total': len(results),
    'with_phone': with_phone,
    'with_website': with_web,
    'with_address': with_address,
}, ensure_ascii=False, indent=2))

print("\n=== DETALLE ===")
for r in results:
    print(json.dumps(r, ensure_ascii=False))
