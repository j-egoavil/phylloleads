"""
SCRAPER MAESTRO - Automatiza todo el flujo
1. Extrae empresas de La República 
2. Busca enriquecimiento automático
3. Genera reporte
"""

import subprocess
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def run_command(script_name, description):
    """Ejecuta un script y retorna si fue exitoso"""
    print_section(description)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=Path(__file__).parent,
            capture_output=False,
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} tardó demasiado")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando {script_name}: {e}")
        return False

def get_db_stats():
    """Obtiene estadísticas de BD"""
    try:
        conn = sqlite3.connect('appdb.sqlite')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE phone != 'N/A' AND phone != ''
        """)
        with_phone = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE website != 'N/A' AND website != ''
        """)
        with_website = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE address != 'N/A' AND address != ''
        """)
        with_address = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total_companies,
            'with_phone': with_phone,
            'with_website': with_website,
            'with_address': with_address,
            'phone_percent': (with_phone / total_companies * 100) if total_companies > 0 else 0,
            'website_percent': (with_website / total_companies * 100) if total_companies > 0 else 0,
            'address_percent': (with_address / total_companies * 100) if total_companies > 0 else 0,
        }
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return None

def main():
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  PHYLLOLEADS - SCRAPER MAESTRO AUTOMATIZADO".center(78) + "█")
    print("█" + "  Extrae datos de La República + Enriquecimiento automático".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    inicio = datetime.now()
    pasos_completados = []
    
    # PASO 1: Extraer de La República
    if run_command(
        'scraper_la_republica.py',
        'PASO 1: Extrayendo empresas de La República'
    ):
        pasos_completados.append('✓ La República')
    else:
        pasos_completados.append('✗ La República')
    
    # PASO 2: Scraper automático
    if run_command(
        'scraper_automatico.py',
        'PASO 2: Enriquecimiento automático (Google Maps + DuckDuckGo + Páginas Amarillas)'
    ):
        pasos_completados.append('✓ Enriquecimiento automático')
    else:
        pasos_completados.append('✗ Enriquecimiento automático')
    
    # PASO 3: Mostrar datos
    if run_command(
        'ver_empresas_con_detalles.py',
        'PASO 3: Mostrando datos finales'
    ):
        pasos_completados.append('✓ Datos mostrados')
    else:
        pasos_completados.append('✗ Datos mostrados')
    
    # ESTADÍSTICAS FINALES
    print_section("ESTADÍSTICAS FINALES")
    
    stats = get_db_stats()
    if stats:
        print(f"Total empresas en BD: {stats['total']}")
        print(f"  • Con teléfono: {stats['with_phone']} ({stats['phone_percent']:.1f}%)")
        print(f"  • Con website: {stats['with_website']} ({stats['website_percent']:.1f}%)")
        print(f"  • Con dirección: {stats['with_address']} ({stats['address_percent']:.1f}%)")
    
    # RESUMEN
    print_section("RESUMEN DE EJECUCIÓN")
    for paso in pasos_completados:
        print(f"  {paso}")
    
    duracion = (datetime.now() - inicio).total_seconds()
    print(f"\nTiempo total: {duracion:.1f} segundos")
    
    print("\n" + "="*80)
    print("✅ FLUJO COMPLETADO")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
