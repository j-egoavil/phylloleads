"""
Actualizar datos de empresas con información REAL
Permite corregir teléfonos y otros datos extraídos
"""

import sqlite3
from datetime import datetime

def listar_empresas():
    """Lista todas las empresas y permite actualizarlas"""
    conn = sqlite3.connect("appdb.sqlite")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*100)
    print("ACTUALIZAR DATOS DE EMPRESAS - Phylloleads")
    print("="*100 + "\n")
    
    # Obtener empresas
    cursor.execute("""
        SELECT c.id, c.name, c.nit, c.city, 
               cd.phone, cd.website, cd.address
        FROM companies c
        LEFT JOIN company_details cd ON c.id = cd.company_id
        WHERE c.is_active = 1
        ORDER BY c.name
    """)
    
    empresas = cursor.fetchall()
    
    if not empresas:
        print("No hay empresas")
        conn.close()
        return
    
    # Mostrar lista
    print("EMPRESAS ACTUALES:")
    print("-" * 100)
    
    for i, empresa in enumerate(empresas, 1):
        print(f"\n[{i}] {empresa['name']}")
        print(f"    NIT: {empresa['nit']} | Ciudad: {empresa['city']}")
        print(f"    Teléfono actual: {empresa['phone'] or 'N/A'}")
        print(f"    Website: {empresa['website'] or 'N/A'}")
        print(f"    Dirección: {(empresa['address'] or 'N/A')[:60]}")
    
    print("\n" + "="*100)
    print("ACTUALIZAR DATOS")
    print("="*100 + "\n")
    
    while True:
        try:
            empresa_id = input("Ingresa ID de empresa a actualizar (o 'q' para salir): ").strip()
            
            if empresa_id.lower() == 'q':
                break
            
            empresa_id = int(empresa_id)
            
            # Verificar que existe
            cursor.execute("SELECT id, name FROM companies WHERE id = ? AND is_active = 1", (empresa_id,))
            empresa = cursor.fetchone()
            
            if not empresa:
                print("Empresa no encontrada")
                continue
            
            print(f"\n--- Actualizando: {empresa['name']} ---\n")
            
            # Obtener datos nuevos
            telefono = input("Teléfono (dejar en blanco para no cambiar): ").strip()
            website = input("Website (dejar en blanco para no cambiar): ").strip()
            direccion = input("Dirección (dejar en blanco para no cambiar): ").strip()
            
            # Actualizar
            if telefono or website or direccion:
                cursor.execute("""
                    SELECT id FROM company_details WHERE company_id = ?
                """, (empresa_id,))
                
                if cursor.fetchone():
                    # UPDATE
                    updates = []
                    params = []
                    
                    if telefono:
                        updates.append("phone = ?")
                        params.append(telefono)
                    if website:
                        updates.append("website = ?")
                        params.append(website)
                    if direccion:
                        updates.append("address = ?")
                        params.append(direccion)
                    
                    updates.append("scraped_at = ?")
                    params.append(datetime.now().isoformat())
                    params.append(empresa_id)
                    
                    query = f"UPDATE company_details SET {', '.join(updates)} WHERE company_id = ?"
                    cursor.execute(query, params)
                else:
                    # INSERT
                    cursor.execute("""
                        INSERT INTO company_details 
                        (company_id, phone, website, address, scraped_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        empresa_id,
                        telefono or 'N/A',
                        website or 'N/A',
                        direccion or 'N/A',
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                print("\n✅ Datos actualizados\n")
            else:
                print("\nNo se ingresó información\n")
        
        except ValueError:
            print("ID inválido")
        except Exception as e:
            print(f"Error: {e}")
    
    conn.close()


def importar_csv():
    """Importar datos desde CSV"""
    print("\n" + "="*100)
    print("IMPORTAR DATOS DESDE CSV")
    print("="*100 + "\n")
    
    print("Formato del CSV:")
    print("id,telefono,website,direccion")
    print("1,+57 1 1234567,https://ejemplo.com,Carrera 5 #10-20")
    print()
    
    csv_file = input("Ruta del archivo CSV (o 'q' para cancelar): ").strip()
    
    if csv_file.lower() == 'q':
        return
    
    try:
        import csv
        
        conn = sqlite3.connect("appdb.sqlite")
        cursor = conn.cursor()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                empresa_id = int(row['id'])
                
                cursor.execute("""
                    INSERT OR REPLACE INTO company_details 
                    (company_id, phone, website, address, scraped_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    empresa_id,
                    row.get('telefono', 'N/A'),
                    row.get('website', 'N/A'),
                    row.get('direccion', 'N/A'),
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ {len(list(reader))} registros importados\n")
    
    except Exception as e:
        print(f"Error importando CSV: {e}\n")


def exportar_csv():
    """Exportar datos a CSV para corrección manual"""
    print("\n" + "="*100)
    print("EXPORTAR DATOS A CSV")
    print("="*100 + "\n")
    
    try:
        import csv
        
        conn = sqlite3.connect("appdb.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.name, c.nit, c.city,
                   COALESCE(cd.phone, '') as phone,
                   COALESCE(cd.website, '') as website,
                   COALESCE(cd.address, '') as address
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE c.is_active = 1
            ORDER BY c.name
        """)
        
        empresas = cursor.fetchall()
        
        with open('empresas_para_corregir.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'nit', 'ciudad', 'telefono_actual', 'website_actual', 'direccion_actual', 'telefono_correcto', 'website_correcto', 'direccion_correcto'])
            
            for empresa in empresas:
                writer.writerow([
                    empresa['id'],
                    empresa['name'],
                    empresa['nit'],
                    empresa['city'],
                    empresa['phone'],
                    empresa['website'],
                    empresa['address'],
                    '',  # Para llenar manualmente
                    '',
                    ''
                ])
        
        conn.close()
        
        print("✅ Archivo exportado: empresas_para_corregir.csv")
        print("   Puedes editarlo manualmente y luego importarlo\n")
    
    except Exception as e:
        print(f"Error exportando: {e}\n")


def menu_principal():
    """Menú principal"""
    while True:
        print("\n" + "="*100)
        print("HERRAMIENTA DE ACTUALIZACIÓN DE DATOS")
        print("="*100)
        print("\n1. Ver y actualizar empresas manualmente")
        print("2. Exportar a CSV para corrección manual")
        print("3. Importar desde CSV corregido")
        print("4. Ver diferencias entre datos actuales y reales")
        print("5. Salir")
        
        opcion = input("\nSelecciona opción (1-5): ").strip()
        
        if opcion == '1':
            listar_empresas()
        elif opcion == '2':
            exportar_csv()
        elif opcion == '3':
            importar_csv()
        elif opcion == '4':
            mostrar_diferencias()
        elif opcion == '5':
            break
        else:
            print("Opción inválida")


def mostrar_diferencias():
    """Muestra el problema de datos inexactos"""
    print("\n" + "="*100)
    print("ANÁLISIS: DATOS EXTRAÍDOS vs DATOS REALES")
    print("="*100 + "\n")
    
    print("El problema encontrado:")
    print()
    print("EMPRESA: CLÍNICA VETERINARIA MONTE VERDE S.A.")
    print("  Teléfono extraído por scraper: +57 5 6123456")
    print("  Teléfono REAL encontrado: +57 301 5052787")
    print()
    print("CAUSAS POSIBLES:")
    print("  1. Los datos iniciales eran 'mock data' (ficticios) para prueba")
    print("  2. El scraper necesita buscar en fuentes más precisas")
    print("  3. Google Maps requiere mejor rendering y parsing")
    print()
    print("SOLUCIONES:")
    print("  ✅ Actualizar manualmente desde información real")
    print("  ✅ Usar directorios colombianos confiables:")
    print("     - Páginas Amarillas: https://www.paginasamarillas.com.co")
    print("     - RUES: https://www.rues.org.co")
    print("     - Dato360: https://www.dato360.com.co")
    print("     - Google My Business")
    print()
    print("RECOMENDACIÓN:")
    print("  1. Exportar datos a CSV (opción 2)")
    print("  2. Buscar números reales en Páginas Amarillas")
    print("  3. Actualizar el CSV manualmente")
    print("  4. Importar datos corregidos (opción 3)")
    print()


if __name__ == "__main__":
    menu_principal()
