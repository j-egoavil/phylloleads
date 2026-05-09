"""
Checklist - Verificación antes de ejecutar el scraper
"""

import sys
import subprocess
from pathlib import Path

def check_python():
    """Verifica versión de Python"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} (necesita 3.9+)")
            return False
    except Exception as e:
        print(f"❌ Error verificando Python: {e}")
        return False

def check_package(package_name, import_name=None):
    """Verifica si está instalado un paquete"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} (instala: pip install {package_name})")
        return False

def check_file(filepath):
    """Verifica si existe un archivo"""
    if Path(filepath).exists():
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} (no encontrado)")
        return False

def main():
    print("\n" + "="*80)
    print("CHECKLIST - VERIFICACIÓN PRE-EJECUCIÓN")
    print("="*80 + "\n")
    
    all_ok = True
    
    # PYTHON
    print("1️⃣  PYTHON")
    print("─" * 80)
    if not check_python():
        all_ok = False
    print()
    
    # PAQUETES ESENCIALES
    print("2️⃣  PAQUETES ESENCIALES")
    print("─" * 80)
    packages = [
        ("selenium", "selenium"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
    ]
    
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_ok = False
    print()
    
    # ARCHIVOS NECESARIOS
    print("3️⃣  ARCHIVOS NECESARIOS")
    print("─" * 80)
    files = [
        "scraper_la_republica.py",
        "scraper_automatico.py",
        "run_scraper_maestro.py",
        "main.py",
        "menu.py",
    ]
    
    for filepath in files:
        if not check_file(filepath):
            all_ok = False
    print()
    
    # NAVEGADORES
    print("4️⃣  NAVEGADORES (necesita al menos 1)")
    print("─" * 80)
    
    browsers_found = 0
    
    # Chrome
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]
    if any(Path(p).exists() for p in chrome_paths):
        print("✅ Chrome")
        browsers_found += 1
    else:
        print("⚠️  Chrome (no encontrado)")
    
    # Edge
    edge_paths = [
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    ]
    if any(Path(p).exists() for p in edge_paths):
        print("✅ Edge")
        browsers_found += 1
    else:
        print("⚠️  Edge (no encontrado)")
    
    # Firefox
    firefox_paths = [
        "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
    ]
    if any(Path(p).exists() for p in firefox_paths):
        print("✅ Firefox")
        browsers_found += 1
    else:
        print("⚠️  Firefox (no encontrado)")
    
    if browsers_found == 0:
        print("\n❌ ERROR: Necesitas instalar Chrome, Edge o Firefox")
        all_ok = False
    else:
        print(f"\n✅ {browsers_found} navegador(es) disponible(s)")
    
    print()
    
    # BASE DE DATOS
    print("5️⃣  BASE DE DATOS")
    print("─" * 80)
    if check_file("appdb.sqlite"):
        pass
    else:
        print("⚠️  appdb.sqlite (se creará automáticamente)")
    print()
    
    # RESULTADO FINAL
    print("=" * 80)
    print("RESULTADO")
    print("=" * 80 + "\n")
    
    if all_ok and browsers_found > 0:
        print("✅ SISTEMA LISTO")
        print("\nPuedes ejecutar uno de estos comandos:\n")
        print("  1️⃣  python menu.py")
        print("  2️⃣  python run_scraper_maestro.py")
        print("  3️⃣  python -m uvicorn main:app --reload\n")
    else:
        print("❌ FALTAN REQUISITOS")
        print("\nInstala lo necesario y vuelve a ejecutar este checklist.\n")
        
        if not all_ok:
            print("Instala los paquetes faltantes:")
            print("  pip install selenium requests beautifulsoup4 fastapi uvicorn\n")
        
        if browsers_found == 0:
            print("Instala al menos un navegador:")
            print("  • Chrome: https://www.google.com/chrome/")
            print("  • Edge: https://www.microsoft.com/edge/")
            print("  • Firefox: https://www.mozilla.org/firefox/\n")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
