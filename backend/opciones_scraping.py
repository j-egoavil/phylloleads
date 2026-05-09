"""
Resumen de OPCIONES para obtener datos de empresas
"""

import sqlite3
from datetime import datetime

def mostrar_opciones():
    """Muestra todas las opciones disponibles"""
    
    print("\n" + "="*100)
    print("OPCIONES DISPONIBLES PARA ENRIQUECER DATOS DE EMPRESAS")
    print("="*100 + "\n")
    
    # Opción 1: Datos Mock (FUNCIONANDO AHORA)
    print("OPCION 1: USAR DATOS MOCK (IMPLEMENTADO - FUNCIONANDO)")
    print("-" * 100)
    print("✅ Estado: ACTIVO")
    print("✅ Ubicación: appdb.sqlite → company_details")
    print("✅ Datos: 5 empresas con teléfono, website, dirección")
    print("✅ Completitud: 80%")
    print("✅ Costo: GRATIS")
    print("✅ Velocidad: INSTANTÁNEO")
    print("\nUso:")
    print("  python ver_empresas_con_detalles.py")
    print("  → Ver empresas con detalles en consola")
    print("  → Exporta a JSON: empresas_con_detalles.json")
    print("  → LISTO PARA USAR EN FRONTEND")
    print("\nEndpoints API:")
    print("  GET /api/companies-with-details?niche=veterinarias")
    print("  GET /api/companies/{id}/details")
    print()
    
    # Opción 2: ChromeDriver + Selenium
    print("OPCION 2: DESCARGAR CHROMEDRIVER + SELENIUM (RECOMENDADO)")
    print("-" * 100)
    print("⏳ Estado: REQUIERE CONFIGURACIÓN")
    print("📥 Paso 1: Descargar ChromeDriver")
    print("   → https://chromedriver.chromium.org/")
    print("   → Ver: INSTALAR_CHROMEDRIVER.md")
    print()
    print("📂 Paso 2: Colocar chromedriver.exe en:")
    print("   c:/Users/davir/OneDrive/Documentos/proyectos/phylloleads/backend/")
    print()
    print("▶ Paso 3: Ejecutar scraper adaptable:")
    print("   python google_maps_scraper_adaptive.py")
    print()
    print("✅ Resultados esperados:")
    print("   - Teléfonos reales de Google Maps")
    print("   - Websites directos")
    print("   - Direcciones exactas")
    print("✅ Completitud: 90%+")
    print("✅ Costo: GRATIS")
    print("✅ Velocidad: ~10-15s por empresa")
    print()
    
    # Opción 3: APIs Pagas
    print("OPCION 3: USAR APIs PAGAS (RÁPIDO Y CONFIABLE)")
    print("-" * 100)
    print("💰 Google Maps API: $7 por 1000 búsquedas")
    print("   → Más preciso y rápido")
    print("   → Requiere: API key + configuración")
    print()
    print("💰 SerpAPI: $0.05 - $0.1 por búsqueda")
    print("   → Busca en Google automáticamente")
    print("   → Devuelve teléfono, website, dirección")
    print()
    print("💰 Clearbit API: $10-100/mes")
    print("   → Enriquecimiento de datos empresariales")
    print("   → Más información: email, empleados, etc")
    print()
    
    # Estado actual de BD
    print("\n" + "="*100)
    print("ESTADO ACTUAL DE LA BASE DE DATOS")
    print("="*100 + "\n")
    
    try:
        conn = sqlite3.connect("appdb.sqlite")
        cursor = conn.cursor()
        
        # Total empresas
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]
        
        # Empresas con detalles
        cursor.execute("SELECT COUNT(*) FROM company_details WHERE phone != 'N/A' OR website != 'N/A'")
        with_details = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM company_details WHERE phone != 'N/A'")
        with_phone = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM company_details WHERE website != 'N/A'")
        with_website = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM company_details WHERE address != 'N/A'")
        with_address = cursor.fetchone()[0]
        
        conn.close()
        
        print("Total empresas en BD: {}".format(total_companies))
        print("Empresas con detalles: {} ({:.1f}%)".format(with_details, (with_details/total_companies)*100 if total_companies > 0 else 0))
        print()
        print("Datos disponibles:")
        print("  - Con teléfono: {}".format(with_phone))
        print("  - Con website: {}".format(with_website))
        print("  - Con dirección: {}".format(with_address))
        
    except Exception as e:
        print("Error: {}".format(e))
    
    print("\n" + "="*100)
    print("RECOMENDACIÓN")
    print("="*100 + "\n")
    print("Para desarrollo local (MVP):")
    print("  → Usa OPCIÓN 1: Datos mock + API (listo ahora)")
    print()
    print("Para producción con datos reales:")
    print("  → Usa OPCIÓN 2: ChromeDriver + Selenium (mejor relación costo/calidad)")
    print()
    print("Si necesitas escalar rápido:")
    print("  → Usa OPCIÓN 3: API (costo pequeño, resultado garantizado)")
    print()
    print("="*100)


if __name__ == "__main__":
    mostrar_opciones()
