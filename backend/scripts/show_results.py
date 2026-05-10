"""
Mostrar resultados finales de empresas con detalles
Script para visualizar los datos después del scraping
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path

def show_companies_with_details():
    """Muestra todas las empresas con detalles"""
    
    # Obtener ruta de BD
    db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
    if not os.path.isabs(db_path):
        db_path = str(Path(__file__).parent / db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener empresas
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.city,
                cd.phone,
                cd.website,
                cd.address,
                cd.scraped_at
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE c.is_active = 1
            ORDER BY c.name
            LIMIT 50
        """)
        
        companies = cursor.fetchall()
        
        if not companies:
            print("\n====================================================================================================")
            print("NO HAY EMPRESAS CON DETALLES")
            print("====================================================================================================\n")
            return True
        
        # Mostrar tabla
        print("\n====================================================================================================")
        print("TABLA DE EMPRESAS CON DETALLES")
        print("----------------------------------------------------------------------------------------------------")
        print(f"{'NOMBRE':<40} {'CIUDAD':<15} {'TELEFONO':<20} {'WEBSITE':<20}")
        print("----------------------------------------------------------------------------------------------------")
        
        for row in companies:
            name = row['name'][:40] if row['name'] else 'N/A'
            city = row['city'][:15] if row['city'] else 'N/A'
            phone = row['phone'][:20] if row['phone'] else 'N/A'
            website = row['website'][:20] if row['website'] else 'N/A'
            print(f"{name:<40} {city:<15} {phone:<20} {website:<20}")
        
        print("----------------------------------------------------------------------------------------------------\n")
        
        # Estadísticas
        cursor.execute("SELECT COUNT(*) FROM companies WHERE is_active = 1")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE phone IS NOT NULL AND phone != 'N/A'
        """)
        with_phone = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE website IS NOT NULL AND website != 'N/A'
        """)
        with_website = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE address IS NOT NULL AND address != 'N/A'
        """)
        with_address = cursor.fetchone()[0]
        
        print("====================================================================================================")
        print("ESTADISTICAS")
        print("====================================================================================================\n")
        print(f"Total de empresas: {total}\n")
        print("Datos disponibles:")
        pct_phone = (with_phone / total * 100) if total > 0 else 0
        pct_website = (with_website / total * 100) if total > 0 else 0
        pct_address = (with_address / total * 100) if total > 0 else 0
        print(f"  - Con teléfono: {with_phone} ({pct_phone:.1f}%)")
        print(f"  - Con website: {with_website} ({pct_website:.1f}%)")
        print(f"  - Con dirección: {with_address} ({pct_address:.1f}%)")
        print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error mostrando resultados: {e}")
        return False

if __name__ == "__main__":
    success = show_companies_with_details()
    exit(0 if success else 1)
