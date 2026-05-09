"""
Mostrar datos actualizados
"""
import json

print("\n" + "="*100)
print("DATOS ACTUALIZADOS EN BD")
print("="*100 + "\n")

with open('empresas_con_detalles.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
    for i, empresa in enumerate(data, 1):
        print(f"[{i}] {empresa['nombre']}")
        print(f"    NIT: {empresa['nit']} | Ciudad: {empresa['ciudad']}")
        print(f"    Teléfono: {empresa['contacto']['telefono'] or 'N/A'}")
        print(f"    Website: {empresa['contacto']['website'] or 'N/A'}")
        print(f"    Dirección: {(empresa['contacto']['direccion'] or 'N/A')[:50]}")
        print()

print("="*100)
print("CAMBIOS REALIZADOS")
print("="*100 + "\n")

print("✅ CLÍNICA VETERINARIA MONTE VERDE S.A.")
print("   Anterior: +57 5 6123456")
print("   Actual:   +57 301 5052787")
print()
