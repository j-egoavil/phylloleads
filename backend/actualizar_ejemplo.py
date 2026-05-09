"""
Ejemplo: Actualizar Clínica Veterinaria Monte Verde con número correcto
"""

import sqlite3
from datetime import datetime

# Conectar BD
conn = sqlite3.connect("appdb.sqlite")
cursor = conn.cursor()

print("\n" + "="*100)
print("ACTUALIZANDO DATOS CON INFORMACIÓN CORRECTA")
print("="*100 + "\n")

# Actualizar Clínica Veterinaria Monte Verde
empresa_id = 3  # ID de la empresa
telefono_correcto = "+57 301 5052787"
nombre_empresa = "CLÍNICA VETERINARIA MONTE VERDE S.A."

print(f"Actualizando: {nombre_empresa}")
print(f"  Teléfono anterior: +57 5 6123456 ❌")
print(f"  Teléfono nuevo: {telefono_correcto} ✅\n")

cursor.execute("""
    UPDATE company_details
    SET phone = ?, scraped_at = ?
    WHERE company_id = ?
""", (telefono_correcto, datetime.now().isoformat(), empresa_id))

conn.commit()
print("✅ Datos actualizados en BD\n")

# Verificar
cursor.execute("""
    SELECT c.name, cd.phone, cd.website, cd.address
    FROM companies c
    JOIN company_details cd ON c.id = cd.company_id
    WHERE c.id = ?
""", (empresa_id,))

row = cursor.fetchone()
if row:
    print("NUEVO REGISTRO:")
    print(f"  Empresa: {row[0]}")
    print(f"  Teléfono: {row[1]}")
    print(f"  Website: {row[2]}")
    print(f"  Dirección: {row[3]}\n")

print("="*100)
print("HERRAMIENTAS DISPONIBLES")
print("="*100 + "\n")

print("Para actualizar más empresas, ejecuta:")
print("  python actualizar_datos.py\n")

print("Opciones disponibles:")
print("  1. Actualizar manualmente empresa por empresa")
print("  2. Exportar a CSV para corrección en Excel")
print("  3. Importar desde CSV corregido")
print("  4. Ver diferencias")
print()

conn.close()

# Actualizar JSON exportado
print("Regenerando archivo JSON con datos actualizados...\n")

conn = sqlite3.connect("appdb.sqlite")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT c.id, c.name, c.nit, c.city, c.company_size,
           cd.phone, cd.website, cd.address, cd.scraped_at
    FROM companies c
    LEFT JOIN company_details cd ON c.id = cd.company_id
    WHERE c.is_active = 1
    ORDER BY c.name
""")

empresas = cursor.fetchall()

import json

data_export = []
for empresa in empresas:
    data_export.append({
        "id": empresa['id'],
        "nombre": empresa['name'],
        "nit": empresa['nit'],
        "ciudad": empresa['city'],
        "estado": "Activa",
        "tamaño": empresa['company_size'] or "Desconocido",
        "contacto": {
            "telefono": empresa['phone'] if empresa['phone'] and empresa['phone'] != 'N/A' else None,
            "website": empresa['website'] if empresa['website'] and empresa['website'] != 'N/A' else None,
            "direccion": empresa['address'] if empresa['address'] and empresa['address'] != 'N/A' else None
        },
        "actualizado": empresa['scraped_at']
    })

with open('empresas_con_detalles.json', 'w', encoding='utf-8') as f:
    json.dump(data_export, f, ensure_ascii=False, indent=2)

print("✅ Archivo 'empresas_con_detalles.json' regenerado con datos actualizados")

conn.close()

print("\n" + "="*100)
print("NUEVO DATO")
print("="*100 + "\n")

print("CLÍNICA VETERINARIA MONTE VERDE S.A.")
print("  Teléfono: +57 301 5052787 ✅")
print("  Website: https://jahpet.co")
print("  Dirección: Centro Historico, Cartagena")
print()
