"""
Script de inicialización de Base de Datos
Instala PostgreSQL si es necesario y crea las tablas
"""

import subprocess
import sys
import platform
import time

def install_postgresql_windows():
    """Instala PostgreSQL en Windows usando chocolatey o descarga manual"""
    print("\n⚠️  PostgreSQL no está instalado")
    print("🔧 Instalando PostgreSQL...")
    
    # Verificar si chocolatey está disponible
    try:
        result = subprocess.run(["choco", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n📦 Usando Chocolatey para instalar PostgreSQL...")
            subprocess.run(["choco", "install", "postgresql", "-y"], check=True)
            print("✅ PostgreSQL instalado exitosamente")
            return True
    except FileNotFoundError:
        pass
    
    # Si no tiene chocolatey, descargar desde el sitio oficial
    print("\n💡 PostgreSQL debe instalarse manualmente")
    print("   Descarga desde: https://www.postgresql.org/download/windows/")
    print("   - Versión recomendada: 16 (igual a docker-compose.yaml)")
    print("   - Configura contraseña postgres = 'postgres'")
    print("   - Instala en: C:\\Program Files\\PostgreSQL\\16\\")
    
    input("\n📌 Presiona Enter cuando hayas instalado PostgreSQL...")
    return True

def main():
    """Iniciador principal"""
    
    print("\n" + "="*80)
    print("🗄️  INICIALIZACIÓN DE BASE DE DATOS")
    print("="*80)
    
    system = platform.system()
    
    if system == "Windows":
        print("\n🖥️  Sistema: Windows")
        # Verificar si PostgreSQL está instalado
        try:
            subprocess.run(["psql", "--version"], capture_output=True, check=True)
            print("✅ PostgreSQL detectado")
        except FileNotFoundError:
            print("❌ PostgreSQL no encontrado")
            install_postgresql_windows()
    
    elif system == "Darwin":
        print("\n🖥️  Sistema: macOS")
        print("💡 Instalá PostgreSQL con: brew install postgresql")
    
    elif system == "Linux":
        print("\n🖥️  Sistema: Linux")
        print("💡 Instala PostgreSQL con: sudo apt-get install postgresql")
    
    print("\n" + "="*80)
    print("✅ PRÓXIMOS PASOS:")
    print("="*80)
    print("""
1. Asegúrate de que PostgreSQL esté corriendo:
   - En Windows: Services → PostgreSQL
   - En Mac/Linux: brew services start postgresql

2. Verifica la conexión:
   psql -U postgres -d postgres

3. Luego ejecuta:
   python setup_database.py

4. O usa Docker Compose (recomendado):
   docker-compose up -d db
    """)

if __name__ == "__main__":
    main()
