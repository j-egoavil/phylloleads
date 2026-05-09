"""
Consultas a Base de Datos - Ejemplos
"""

import sqlite3
import json
from tabulate import tabulate

def query_database():
    """Realiza consultas a la BD"""
    
    conn = sqlite3.connect('appdb.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*100)
    print("🔍 CONSULTAS A BASE DE DATOS")
    print("="*100)
    
    # 1. Todas las empresas
    print("\n1️⃣  TODAS LAS EMPRESAS:")
    print("-"*100)
    cursor.execute("""
        SELECT id, name, nit, city, status, company_size 
        FROM companies 
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    headers = ['ID', 'Nombre', 'NIT', 'Ciudad', 'Estado', 'Tamaño']
    data = [(row['id'], row['name'][:40], row['nit'], row['city'], row['status'], row['company_size']) 
            for row in rows]
    
    print(tabulate(data, headers=headers, tablefmt="grid"))
    
    # 2. Por estado
    print("\n2️⃣  ESTADÍSTICAS:")
    print("-"*100)
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as activas,
            SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactivas
        FROM companies
    """)
    
    row = cursor.fetchone()
    print(f"\n📊 Total de empresas: {row['total']}")
    print(f"   ✅ Activas: {row['activas']} ({row['activas']/row['total']*100:.1f}%)")
    print(f"   ❌ Inactivas: {row['inactivas']} ({row['inactivas']/row['total']*100:.1f}%)")
    
    # 3. Por ciudad
    print("\n3️⃣  EMPRESAS POR CIUDAD:")
    print("-"*100)
    cursor.execute("""
        SELECT city, COUNT(*) as count, 
               SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as activas
        FROM companies
        GROUP BY city
        ORDER BY count DESC
    """)
    
    rows = cursor.fetchall()
    headers = ['Ciudad', 'Total', 'Activas']
    data = [(row['city'], row['count'], row['activas']) for row in rows]
    print(tabulate(data, headers=headers, tablefmt="grid"))
    
    # 4. Por tamaño
    print("\n4️⃣  EMPRESAS POR TAMAÑO:")
    print("-"*100)
    cursor.execute("""
        SELECT company_size, COUNT(*) as count
        FROM companies
        GROUP BY company_size
        ORDER BY count DESC
    """)
    
    rows = cursor.fetchall()
    headers = ['Tamaño', 'Cantidad']
    data = [(row['company_size'], row['count']) for row in rows]
    print(tabulate(data, headers=headers, tablefmt="grid"))
    
    # 5. Empresas sin detalles (para Google Maps)
    print("\n5️⃣  EMPRESAS SIN DETALLES (Para scraper de Google Maps):")
    print("-"*100)
    cursor.execute("""
        SELECT c.id, c.name, c.city
        FROM companies c
        LEFT JOIN company_details cd ON c.id = cd.company_id
        WHERE cd.id IS NULL
        ORDER BY c.name
    """)
    
    rows = cursor.fetchall()
    headers = ['ID', 'Nombre', 'Ciudad']
    data = [(row['id'], row['name'][:50], row['city']) for row in rows]
    
    print(tabulate(data, headers=headers, tablefmt="grid"))
    print(f"\n💡 Estas {len(data)} empresas necesitan información de Google Maps (teléfono, web, dirección)")
    
    # 6. Exportar a JSON
    print("\n6️⃣  EXPORTANDO A JSON:")
    print("-"*100)
    cursor.execute("""
        SELECT * FROM companies 
        WHERE is_active = 1
        ORDER BY city, name
    """)
    
    rows = cursor.fetchall()
    companies_json = [dict(row) for row in rows]
    
    output_file = "empresas_activas.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(companies_json, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportadas {len(companies_json)} empresas activas a: {output_file}")
    
    print("\n" + "="*100 + "\n")
    
    conn.close()

if __name__ == "__main__":
    try:
        query_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Primero ejecuta: python setup_database.py")
