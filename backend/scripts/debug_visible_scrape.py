#!/usr/bin/env python3
import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.scraper_automatico import AutomaticDataScraper

COMPANY_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 722
DB = os.getenv('APP_DB_PATH', 'appdb.sqlite')


def wait_step(message: str):
    print(f"\n=== {message} ===")
    input("Presiona Enter para continuar...")


conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, name, city, nit FROM companies WHERE id = ?", (COMPANY_ID,))
row = cur.fetchone()
if not row:
    print(f"No existe company_id={COMPANY_ID}")
    sys.exit(2)
company = dict(row)
conn.close()

print(f"Empresa: {company['name']} | Ciudad: {company.get('city')} | NIT: {company.get('nit')}")

scraper = AutomaticDataScraper(db_path=DB)
if not scraper.connect_db():
    print("No se pudo conectar a BD")
    sys.exit(3)

try:
    wait_step("Paso 1: abrir navegador visible")
    scraper.driver = scraper.get_browser(headless=False)
    if not scraper.driver:
        print("No se pudo abrir navegador")
        sys.exit(4)
    print("Navegador abierto")

    wait_step("Paso 2: ejecutar scrape_company")
    details = scraper.scrape_company(company['id'], company['name'], company.get('city', ''), nit=company.get('nit'))
    print("\nResultado raw:")
    print(json.dumps(details, indent=2, ensure_ascii=False))

    wait_step("Paso 3: guardar en BD si hay datos")
    if details:
        saved = scraper.save_details(company['id'], details)
        print(f"Guardado: {saved}")

    wait_step("Paso 4: leer resultado guardado")
    cur = scraper.conn.cursor()
    cur.execute("SELECT * FROM company_details WHERE company_id = ?", (COMPANY_ID,))
    drow = cur.fetchone()
    print(json.dumps(dict(drow) if drow else None, indent=2, ensure_ascii=False))

finally:
    scraper.close_db()
    scraper.close_browser()
    print("\nFin")
