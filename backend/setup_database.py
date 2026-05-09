"""
Setup de Base de Datos - Soporta PostgreSQL y SQLite
"""

import os
import json
import sqlite3
from datetime import datetime

class DatabaseSetup:
    """Configuración de BD con soporte para PostgreSQL y SQLite"""
    
    def __init__(self, db_type="sqlite"):
        """
        Args:
            db_type: "postgres" o "sqlite"
        """
        self.db_type = db_type
        self.conn = None
    
    def connect_sqlite(self):
        """Conecta a SQLite (sin instalación necesaria)"""
        db_path = "appdb.sqlite"
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"✅ Conectado a SQLite: {os.path.abspath(db_path)}")
        return self.conn
    
    def connect_postgres(self):
        """Conecta a PostgreSQL"""
        try:
            import psycopg2
            self.conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="postgres",  # Conecta a BD default primero
                user="postgres",
                password="postgres"
            )
            print("✅ Conectado a PostgreSQL")
            return self.conn
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            print("   Usando SQLite como fallback...")
            return self.connect_sqlite()
    
    def create_tables_sqlite(self):
        """Crea tablas en SQLite"""
        cursor = self.conn.cursor()
        
        # Tabla companies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT UNIQUE,
                nit TEXT,
                rues TEXT,
                city TEXT,
                is_active BOOLEAN DEFAULT 1,
                status TEXT,
                company_size TEXT,
                search_niche TEXT,
                scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla company_details (para Google Maps)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER UNIQUE,
                phone TEXT,
                website TEXT,
                address TEXT,
                latitude REAL,
                longitude REAL,
                google_maps_url TEXT,
                scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );
        """)
        
        # Tabla search_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT NOT NULL,
                total_companies INTEGER,
                pages_scraped INTEGER,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT
            );
        """)
        
        self.conn.commit()
        print("✅ Tablas creadas en SQLite")
    
    def create_tables_postgres(self):
        """Crea tablas en PostgreSQL"""
        cursor = self.conn.cursor()
        
        # Crear BD appdb
        try:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'appdb'")
            if not cursor.fetchone():
                cursor.execute("CREATE DATABASE appdb")
                print("✅ Base de datos 'appdb' creada")
        except Exception as e:
            print(f"⚠️  {e}")
        
        cursor.close()
        self.conn.close()
        
        # Conectar a appdb
        import psycopg2
        self.conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="appdb",
            user="postgres",
            password="postgres"
        )
        cursor = self.conn.cursor()
        
        # Tabla companies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(500) NOT NULL,
                url VARCHAR(1000) UNIQUE,
                nit VARCHAR(100),
                rues VARCHAR(100),
                city VARCHAR(200),
                is_active BOOLEAN DEFAULT true,
                status VARCHAR(50),
                company_size VARCHAR(50),
                search_niche VARCHAR(200),
                scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla company_details
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_details (
                id SERIAL PRIMARY KEY,
                company_id INTEGER UNIQUE,
                phone VARCHAR(20),
                website VARCHAR(500),
                address TEXT,
                latitude FLOAT,
                longitude FLOAT,
                google_maps_url VARCHAR(1000),
                scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );
        """)
        
        # Tabla search_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id SERIAL PRIMARY KEY,
                niche VARCHAR(200) NOT NULL,
                total_companies INTEGER,
                pages_scraped INTEGER,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status VARCHAR(50)
            );
        """)
        
        self.conn.commit()
        print("✅ Tablas creadas en PostgreSQL")
    
    def import_json_data(self, json_file):
        """Importa datos de archivo JSON a la BD"""
        if not os.path.exists(json_file):
            print(f"⚠️  Archivo no encontrado: {json_file}")
            return False
        
        with open(json_file, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        print(f"\n📥 Importando {len(companies)} empresas...")
        
        cursor = self.conn.cursor()
        
        for i, company in enumerate(companies, 1):
            try:
                if self.db_type == "sqlite":
                    cursor.execute("""
                        INSERT OR REPLACE INTO companies 
                        (name, url, nit, rues, city, is_active, status, company_size, search_niche, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        company.get('name'),
                        company.get('url'),
                        company.get('nit'),
                        company.get('rues'),
                        company.get('city'),
                        company.get('is_active', True),
                        company.get('status'),
                        company.get('company_size'),
                        company.get('search_niche'),
                        company.get('scraped_at')
                    ))
                else:  # PostgreSQL
                    cursor.execute("""
                        INSERT INTO companies 
                        (name, url, nit, rues, city, is_active, status, company_size, search_niche, scraped_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (url) 
                        DO UPDATE SET 
                            name = EXCLUDED.name,
                            is_active = EXCLUDED.is_active,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        company.get('name'),
                        company.get('url'),
                        company.get('nit'),
                        company.get('rues'),
                        company.get('city'),
                        company.get('is_active', True),
                        company.get('status'),
                        company.get('company_size'),
                        company.get('search_niche'),
                        company.get('scraped_at')
                    ))
            except Exception as e:
                print(f"⚠️  Error importando empresa {i}: {e}")
                continue
        
        self.conn.commit()
        print(f"✅ {len(companies)} empresas importadas exitosamente")
        return True
    
    def close(self):
        """Cierra conexión"""
        if self.conn:
            self.conn.close()

def main():
    """Main"""
    
    print("\n" + "="*80)
    print("🗄️  SETUP DE BASE DE DATOS")
    print("="*80)
    
    # Usar SQLite por defecto (más simple, sin instalación)
    print("\n1️⃣  Conectando a SQLite...")
    db = DatabaseSetup(db_type="sqlite")
    db.connect_sqlite()
    
    # Crear tablas
    print("\n2️⃣  Creando tablas...")
    db.create_tables_sqlite()
    
    # Importar datos
    print("\n3️⃣  Importando datos del test...")
    test_data_file = "test_results/veterinarias_20260509_165002.json"
    
    if os.path.exists(test_data_file):
        db.import_json_data(test_data_file)
    else:
        print(f"⚠️  No se encontró: {test_data_file}")
        print("   Generando datos de prueba...")
        # Generar JSON de prueba
        import subprocess
        import sys
        subprocess.run([sys.executable, "test_simple.py"], check=True)
        # Buscar el archivo más reciente
        import glob
        files = glob.glob("test_results/*.json")
        if files:
            latest_file = max(files, key=os.path.getctime)
            db.import_json_data(latest_file)
    
    # Mostrar estadísticas
    print("\n4️⃣  Estadísticas de BD...")
    cursor = db.conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    count = cursor.fetchone()[0]
    print(f"   📊 Total de empresas: {count}")
    
    cursor.execute("SELECT COUNT(DISTINCT city) FROM companies")
    cities = cursor.fetchone()[0]
    print(f"   🏙️  Ciudades únicas: {cities}")
    
    cursor.execute("SELECT COUNT(*) FROM companies WHERE is_active = 1")
    active = cursor.fetchone()[0]
    print(f"   ✅ Empresas activas: {active}")
    
    # Mostrar ubicación de BD
    print("\n" + "="*80)
    print(f"💾 Base de datos SQLite: {os.path.abspath('appdb.sqlite')}")
    print("="*80 + "\n")
    
    db.close()

if __name__ == "__main__":
    main()
