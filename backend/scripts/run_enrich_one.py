#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from services.scraper_automatico import AutomaticDataScraper

COMPANY_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
DB = os.getenv('APP_DB_PATH', 'appdb.sqlite')

print(f"Conectando a BD: {DB}")
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, name, city, nit FROM companies WHERE id = ?", (COMPANY_ID,))
row = cur.fetchone()
if not row:
    print(f"Empresa con id={COMPANY_ID} no encontrada en BD")
    sys.exit(2)
company = dict(row)
print(f"Empresa encontrada: {company['name']} ({company.get('city')})\n")
conn.close()

scraper = AutomaticDataScraper(db_path=DB)
if not scraper.connect_db():
    print("Error: no se pudo conectar a la BD desde el scraper")
    sys.exit(3)

print("Ejecutando enriquecimiento (scrape_company)... esto puede tardar si requiere Selenium")
details = scraper.scrape_company(company['id'], company['name'], company.get('city',''), nit=company.get('nit'))
print('\nResultado raw:')
print(json.dumps(details, indent=2, ensure_ascii=False))

if details:
    saved = scraper.save_details(company['id'], details)
    print(f"\nGuardado en BD: {saved}")

    # Leer detalles guardados
    cur = scraper.conn.cursor()
    cur.execute("SELECT phone, website, address, scraped_at FROM company_details WHERE company_id = ?", (COMPANY_ID,))
    drow = cur.fetchone()
    print('\nDetalles en BD:')
    if drow:
        print(json.dumps(dict(drow), indent=2, ensure_ascii=False))
    else:
        print('No hay detalles guardados')

scraper.close_db()
scraper.close_browser()
print('\nHecho')
