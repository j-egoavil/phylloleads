#!/usr/bin/env python3
"""End-to-end: limpiar, extraer y enriquecer 10 empresas (veterinarias)."""
import os
import sys
import sqlite3
from pathlib import Path

# Asegurar imports desde backend
backend_dir = str(Path(__file__).resolve().parents[1])
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('APP_DB_PATH', str(Path.cwd() / 'appdb.sqlite'))

def ensure_tables(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # companies table may already exist from scraper; ensure company_details exists
    cur.execute('''
    CREATE TABLE IF NOT EXISTS company_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER UNIQUE,
        phone TEXT,
        website TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL,
        google_maps_url TEXT,
        source TEXT,
        scraped_at TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    conn.commit()
    conn.close()


def clean_tables(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # create companies if not exists minimal (only if not present) to allow inserts
    cur.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT,
        nit TEXT,
        city TEXT,
        is_active INTEGER DEFAULT 1,
        status TEXT,
        company_size TEXT,
        search_niche TEXT,
        scraped_at TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    conn.commit()
    # Clean existing data to start fresh
    cur.execute('DELETE FROM company_details')
    cur.execute('DELETE FROM companies')
    conn.commit()
    conn.close()


def extract_companies(niche='veterinarias'):
    from services.scraper_la_republica import EmpresasLaRepublicaScraper
    scraper = EmpresasLaRepublicaScraper(headless=True, max_sitemaps=1)
    result = scraper.scrape_and_save(niche, keywords=[niche])
    return result


def enrich_companies(limit=10):
    from services.scraper_automatico import AutomaticDataScraper
    db_path = os.getenv('APP_DB_PATH')
    scraper = AutomaticDataScraper(db_path=db_path)
    return scraper.process_companies(limit=limit)


def show_summary(limit=10):
    db_path = os.getenv('APP_DB_PATH')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
    SELECT c.id, c.name, c.is_active, cd.phone, cd.website, cd.address
    FROM companies c
    LEFT JOIN company_details cd ON c.id = cd.company_id
    WHERE c.search_niche = ?
    ORDER BY c.id
    LIMIT ?
    ''', ('veterinarias', limit))
    rows = cur.fetchall()
    total = len(rows)
    websites = sum(1 for r in rows if r['website'] and r['website'] != 'N/A')
    addresses = sum(1 for r in rows if r['address'] and r['address'] != 'N/A')
    active = sum(1 for r in rows if r['is_active'])

    print(f"\n--- RESUMEN FINAL (primeras {total} empresas) ---")
    print(f"Con sitio web: {websites}")
    print(f"Con dirección: {addresses}")
    print(f"Activas: {active} | Inactivas: {total - active}")
    print('\nMUESTRA:')
    for r in rows:
        phone = r['phone'] if r['phone'] and r['phone'] != 'N/A' else 'N/A'
        web = r['website'] if r['website'] and r['website'] != 'N/A' else 'N/A'
        addr = r['address'] if r['address'] and r['address'] != 'N/A' else 'N/A'
        status = 'Activa' if r['is_active'] else 'Inactiva'
        print(f"- {r['name']} | {status} | Tel: {phone} | Dir: {addr} | Web: {web}")
    conn.close()


if __name__ == '__main__':
    db_path = os.getenv('APP_DB_PATH')
    print('DB path:', db_path)
    ensure_tables(db_path)
    clean_tables(db_path)
    print('\nExtrayendo empresas (La República)...')
    res = extract_companies('veterinarias')
    print(f"Extraídas: {res.get('total_companies', 0)} empresas")
    print('\nEnriqueciendo empresas (scraper automático)...')
    enr = enrich_companies(limit=10)
    print(f"Procesadas: {enr.get('total', 0)} | Exitosas: {enr.get('processed', 0)}")
    show_summary(limit=10)
