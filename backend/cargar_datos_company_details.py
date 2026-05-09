"""
DEMO: Cargar datos simulados en company_details
Esto simula lo que haría el scraper real cuando encuentre datos
"""

import sqlite3
from datetime import datetime

# Datos simulados que el scraper ENCONTRARIA
DATOS_SIMULADOS = [
    {
        'company_id': 1,
        'name': 'CENTRO VETERINARIO ESPECIALIZADO BOGOTA',
        'phone': '+57 1 2345678',
        'website': 'https://centrovetbogota.com',
        'address': 'Carrera 5 #10-20 Chapinero, Bogota'
    },
    {
        'company_id': 2,
        'name': 'CLINICA VETERINARIA MONTE VERDE S.A.',
        'phone': '+57 4 3456789',
        'website': 'https://clinicamonteverde.co',
        'address': 'Calle 50 #45-30 Laureles, Medellin'
    },
    {
        'company_id': 3,
        'name': 'JAH PET CLINICA VETERINARIA S.A.S.',
        'phone': '+57 5 6123456',
        'website': 'https://jahpet.co',
        'address': 'Centro Historico, Cartagena'
    },
    {
        'company_id': 4,
        'name': 'VET CLINIC BARRANQUILLA DOGS & CATS',
        'phone': '+57 5 3789456',
        'website': 'https://vetbarranquilla.com',
        'address': 'Cra 53 #74-80, Barranquilla'
    },
    {
        'company_id': 5,
        'name': 'VETERINARIA EL PARAISO LIMITADA',
        'phone': '+57 1 5678901',
        'website': 'https://paraisovet.co',
        'address': 'Cra 7 #125-50 Usaquen, Bogota'
    }
]


def cargar_datos():
    """Carga datos simulados en company_details"""
    
    print("\n" + "="*80)
    print("CARGANDO DATOS SIMULADOS EN COMPANY_DETAILS")
    print("="*80 + "\n")
    
    try:
        # Conectar
        conn = sqlite3.connect('appdb.sqlite')
        cursor = conn.cursor()
        
        # Limpiar tabla (opcional)
        print("Limpiando table company_details...")
        cursor.execute("DELETE FROM company_details")
        
        # Insertar datos
        count = 0
        for datos in DATOS_SIMULADOS:
            cursor.execute("""
                INSERT INTO company_details 
                (company_id, phone, website, address, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datos['company_id'],
                datos['phone'],
                datos['website'],
                datos['address'],
                datetime.now().isoformat()
            ))
            count += 1
            
            print("\n[{}] {}".format(count, datos['name']))
            print("    Telefono: {}".format(datos['phone']))
            print("    Website: {}".format(datos['website']))
            print("    Direccion: {}".format(datos['address']))
        
        conn.commit()
        
        print("\n" + "="*80)
        print("DATOS CARGADOS EXITOSAMENTE")
        print("="*80)
        
        # Verificar
        cursor.execute("""
            SELECT c.name, cd.phone, cd.website, cd.address
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE cd.id IS NOT NULL
            ORDER BY c.name
        """)
        
        print("\nDatos en BD:")
        print("-"*80)
        for row in cursor.fetchall():
            print("- {}: {}".format(row[0][:40].ljust(40), row[1]))
        
        # Estadisticas
        cursor.execute("SELECT COUNT(*) FROM company_details")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE cd.id IS NULL
        """)
        sin_detalles = cursor.fetchone()[0]
        
        print("\n" + "="*80)
        print("ESTADISTICAS")
        print("="*80)
        print("Empresas con detalles: {}".format(total))
        print("Empresas sin detalles: {}".format(sin_detalles))
        print("Total empresas: {}".format(total + sin_detalles))
        
        conn.close()
        
        print("\n" + "="*80)
        print("PROXIMO PASO: Crear API endpoint para recuperar datos")
        print("="*80)
        
    except Exception as e:
        print("ERROR: {}".format(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    cargar_datos()
