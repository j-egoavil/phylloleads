"""
Migra datos de SQLite a PostgreSQL
Uso: python migrate_sqlite_to_postgres.py [--sqlite-path appdb.sqlite]
"""

import sqlite3
import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 no está instalado. Instalar con:")
    print("pip install psycopg2-binary")
    sys.exit(1)


def migrate():
    """Migra datos de SQLite a PostgreSQL"""
    
    # Parámetros
    sqlite_path = "appdb.sqlite"  # archivo SQLite local
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "appdb")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    
    # Verificar archivo SQLite
    if not os.path.exists(sqlite_path):
        print(f"❌ Archivo SQLite no encontrado: {sqlite_path}")
        sys.exit(1)
    
    print(f"📂 Leyendo de SQLite: {sqlite_path}")
    
    # Conectar a ambas BDs
    try:
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        print("✅ Conectado a SQLite")
    except Exception as e:
        print(f"❌ Error conectando a SQLite: {e}")
        sys.exit(1)
    
    try:
        pg_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        pg_cursor = pg_conn.cursor()
        print("✅ Conectado a PostgreSQL")
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        sys.exit(1)
    
    try:
        # 1. Migrar tabla companies
        print("\n1️⃣  Migrando tabla 'companies'...")
        sqlite_cursor.execute("SELECT * FROM companies")
        companies = sqlite_cursor.fetchall()
        
        for company in companies:
            try:
                pg_cursor.execute("""
                    INSERT INTO companies 
                    (name, url, nit, rues, city, is_active, status, company_size, search_niche, scraped_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                """, (
                    company['name'],
                    company['url'],
                    company['nit'],
                    company['rues'],
                    company['city'],
                    bool(company['is_active']),
                    company['status'],
                    company['company_size'],
                    company['search_niche'],
                    company['scraped_at']
                ))
            except Exception as e:
                print(f"  ⚠️  Error insertando empresa {company['name']}: {e}")
                continue
        
        pg_conn.commit()
        print(f"   ✅ {len(companies)} empresas migradas")
        
        # 2. Migrar tabla company_details
        print("\n2️⃣  Migrando tabla 'company_details'...")
        sqlite_cursor.execute("SELECT * FROM company_details")
        details = sqlite_cursor.fetchall()
        
        for detail in details:
            try:
                pg_cursor.execute("""
                    INSERT INTO company_details 
                    (company_id, phone, website, address, latitude, longitude, google_maps_url, scraped_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (company_id) DO UPDATE SET
                        phone = EXCLUDED.phone,
                        website = EXCLUDED.website,
                        address = EXCLUDED.address,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    detail['company_id'],
                    detail['phone'],
                    detail['website'],
                    detail['address'],
                    detail['latitude'],
                    detail['longitude'],
                    detail['google_maps_url'],
                    detail['scraped_at']
                ))
            except Exception as e:
                print(f"  ⚠️  Error insertando detalles: {e}")
                continue
        
        pg_conn.commit()
        print(f"   ✅ {len(details)} detalles migrados")
        
        # 3. Verificar datos
        print("\n3️⃣  Verificando datos...")
        pg_cursor.execute("SELECT COUNT(*) FROM companies")
        companies_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM company_details WHERE phone IS NOT NULL AND phone != 'N/A'")
        details_count = pg_cursor.fetchone()[0]
        
        print(f"   📊 Total empresas en PostgreSQL: {companies_count}")
        print(f"   📊 Empresas con teléfono: {details_count}")
        
        pg_conn.commit()
        
        print("\n✅ Migración completada con éxito")
        print(f"   Base de datos: {db_host}:{db_port}/{db_name}")
        print(f"   Usuario: {db_user}")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        pg_conn.rollback()
        sys.exit(1)
    
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    migrate()
