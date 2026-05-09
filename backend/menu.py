"""
PHYLLOLEADS - Menú Principal
Opciones para ejecutar el scraper automático
"""

import os
import subprocess
import sys
from pathlib import Path

def print_header():
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  PHYLLOLEADS - SCRAPER AUTOMÁTICO".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")

def print_menu():
    print("=" * 80)
    print("SELECCIONA UNA OPCIÓN:")
    print("=" * 80)
    print()
    print("  [1] ⚡ EJECUTAR SCRAPER COMPLETO (Recomendado)")
    print("       → Extrae de La República")
    print("       → Enriquece datos automáticamente")
    print("       → Muestra estadísticas")
    print("       Tiempo: ~5-10 minutos")
    print()
    print("  [2] 🌐 INICIAR API (Ejecución vía HTTP)")
    print("       → Inicia servidor en http://localhost:8000")
    print("       → Documentación en http://localhost:8000/docs")
    print("       → Ejecutar scraper vía POST")
    print("       → Ideal para integración")
    print()
    print("  [3] 📊 PASO A PASO (Depuración)")
    print("       → Ejecutar cada fase manualmente")
    print("       → Paso 1: La República")
    print("       → Paso 2: Enriquecimiento")
    print("       → Paso 3: Mostrar datos")
    print()
    print("  [4] 📋 VER DATOS ACTUALES")
    print("       → Muestra empresas con detalles en BD")
    print("       → Estadísticas de cobertura")
    print()
    print("  [5] 🔧 ACTUALIZAR DATOS MANUALMENTE")
    print("       → Menú interactivo para editar")
    print("       → Exportar/Importar CSV")
    print()
    print("  [0] ❌ SALIR")
    print()
    print("=" * 80)
    print()

def option_1_run_complete():
    """Ejecutar scraper completo"""
    print("\n⚡ Iniciando scraper completo...\n")
    try:
        result = subprocess.run(
            [sys.executable, "run_scraper_maestro.py"],
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            print("\n✅ Scraper completado exitosamente")
        else:
            print("\n❌ Error durante ejecución")
    except Exception as e:
        print(f"❌ Error: {e}")

def option_2_start_api():
    """Iniciar API"""
    print("\n🌐 Iniciando API...\n")
    print("Endpoint: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Logs: http://localhost:8000/logs")
    print("\nPara ejecutar scraper vía API:")
    print("  POST http://localhost:8000/api/scraper/enrich-automatic")
    print("  GET http://localhost:8000/api/scraper/status")
    print("\n(Presiona Ctrl+C para detener)\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
            cwd=Path(__file__).parent
        )
    except KeyboardInterrupt:
        print("\n\n✅ API detenida")
    except Exception as e:
        print(f"❌ Error: {e}")

def option_3_step_by_step():
    """Ejecutar paso a paso"""
    print("\n📊 Ejecutar por pasos\n")
    
    steps = [
        ("Paso 1: Extraer de La República", "scraper_la_republica.py"),
        ("Paso 2: Enriquecimiento automático", "scraper_automatico.py"),
        ("Paso 3: Mostrar datos", "ver_empresas_con_detalles.py"),
    ]
    
    for step_name, script in steps:
        print("=" * 80)
        print(f"\n{step_name}...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, script],
                cwd=Path(__file__).parent,
                input=b'\n',  # Auto-confirm
                timeout=300
            )
            if result.returncode == 0:
                print(f"✅ {step_name} completado\n")
            else:
                print(f"⚠️  {step_name} con advertencias\n")
        except subprocess.TimeoutExpired:
            print(f"⏱️  {step_name} tardó demasiado\n")
        except Exception as e:
            print(f"❌ Error en {step_name}: {e}\n")

def option_4_view_data():
    """Ver datos actuales"""
    print("\n📋 Ver datos actuales\n")
    try:
        subprocess.run(
            [sys.executable, "ver_empresas_con_detalles.py"],
            cwd=Path(__file__).parent
        )
    except Exception as e:
        print(f"❌ Error: {e}")

def option_5_update_data():
    """Actualizar datos manualmente"""
    print("\n🔧 Menú de actualización de datos\n")
    try:
        subprocess.run(
            [sys.executable, "actualizar_datos.py"],
            cwd=Path(__file__).parent
        )
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    os.chdir(Path(__file__).parent)
    
    while True:
        print_header()
        print_menu()
        
        try:
            opcion = input("Selecciona opción (0-5): ").strip()
            
            if opcion == "1":
                option_1_run_complete()
            elif opcion == "2":
                option_2_start_api()
            elif opcion == "3":
                option_3_step_by_step()
            elif opcion == "4":
                option_4_view_data()
            elif opcion == "5":
                option_5_update_data()
            elif opcion == "0":
                print("\n👋 ¡Hasta luego!\n")
                break
            else:
                print("❌ Opción inválida. Por favor selecciona 0-5\n")
            
            input("\nPresiona ENTER para continuar...")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
