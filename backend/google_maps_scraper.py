"""
Scraper de Google Maps - Obtiene teléfono, web y dirección
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    """
    Scraper de Google Maps para obtener:
    - Teléfono
    - Página web
    - Dirección
    - Coordenadas (lat/long)
    """
    
    def __init__(self, db_path: str = "appdb.sqlite"):
        """
        Inicializa el scraper
        
        Args:
            db_path: Ruta a la BD SQLite
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Conecta a la BD"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"✅ Conectado a {self.db_path}")
    
    def get_companies_without_details(self):
        """Obtiene empresas sin detalles de Google Maps"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.city, c.url, c.nit
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE cd.id IS NULL
            AND c.is_active = 1
            ORDER BY c.name
            LIMIT 50
        """)
        
        return cursor.fetchall()
    
    def save_company_details(self, company_id: int, details: Dict[str, Any]) -> bool:
        """
        Guarda detalles de empresa
        
        Args:
            company_id: ID de la empresa
            details: Dict con phone, website, address, lat, long, url
            
        Returns:
            True si se guardó, False si hubo error
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO company_details 
                (company_id, phone, website, address, latitude, longitude, google_maps_url, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                details.get('phone'),
                details.get('website'),
                details.get('address'),
                details.get('latitude'),
                details.get('longitude'),
                details.get('google_maps_url'),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error guardando detalles: {e}")
            return False
    
    def scrape_company(self, company_name: str, city: str) -> Optional[Dict[str, Any]]:
        """
        Scrape información de una empresa desde Google Maps
        
        ⚠️ NOTA: Esta es una versión DEMO sin Selenium
        En producción usarías:
        - Selenium con Chrome
        - Beautiful Soup para parsear
        - APIs de Google Maps
        
        Args:
            company_name: Nombre de la empresa
            city: Ciudad
            
        Returns:
            Dict con detalles o None
        """
        
        # IMPORTANTE: Esta es una versión MOCK para demostración
        # En producción necesitarías:
        # 1. Selenium para navegador
        # 2. Google Maps API
        # 3. Lógica de parsing HTML
        
        logger.info(f"🔍 Buscando en Google Maps: '{company_name}' en {city}")
        
        # Simular extracción
        # En realidad usarías Selenium así:
        """
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        
        driver = webdriver.Chrome()
        driver.get("https://maps.google.com")
        
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(f"{company_name} {city}")
        search_box.send_keys(Keys.RETURN)
        
        # ... parsear resultados ...
        """
        
        # Por ahora retornamos estructura mock
        details = {
            'phone': 'N/A',
            'website': 'N/A',
            'address': 'N/A',
            'latitude': None,
            'longitude': None,
            'google_maps_url': f"https://maps.google.com/maps?q={company_name}+{city}",
            'status': 'pending'  # Pendiente de scrape real
        }
        
        return details
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de detalles"""
        cursor = self.conn.cursor()
        
        # Total con detalles
        cursor.execute("SELECT COUNT(*) FROM company_details")
        with_details = cursor.fetchone()[0]
        
        # Total sin detalles
        cursor.execute("""
            SELECT COUNT(*) FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE cd.id IS NULL AND c.is_active = 1
        """)
        without_details = cursor.fetchone()[0]
        
        # Con teléfono
        cursor.execute("SELECT COUNT(*) FROM company_details WHERE phone != 'N/A' AND phone IS NOT NULL")
        with_phone = cursor.fetchone()[0]
        
        # Con website
        cursor.execute("SELECT COUNT(*) FROM company_details WHERE website != 'N/A' AND website IS NOT NULL")
        with_website = cursor.fetchone()[0]
        
        return {
            'con_detalles': with_details,
            'sin_detalles': without_details,
            'con_telefono': with_phone,
            'con_website': with_website
        }
    
    def close(self):
        """Cierra conexión"""
        if self.conn:
            self.conn.close()

def main():
    """Main"""
    
    print("\n" + "="*80)
    print("🗺️  SCRAPER DE GOOGLE MAPS")
    print("="*80)
    
    scraper = GoogleMapsScraper()
    scraper.connect()
    
    # Obtener estadísticas
    print("\n📊 ESTADÍSTICAS:")
    print("-"*80)
    stats = scraper.get_statistics()
    
    print(f"\n✅ Con detalles: {stats['con_detalles']}")
    print(f"❌ Sin detalles: {stats['sin_detalles']}")
    print(f"📞 Con teléfono: {stats['con_telefono']}")
    print(f"🌐 Con website: {stats['con_website']}")
    
    # Obtener empresas sin detalles
    print("\n🔍 EMPRESAS SIN DETALLES DE GOOGLE MAPS:")
    print("-"*80)
    companies = scraper.get_companies_without_details()
    
    if not companies:
        print("\n✅ ¡Todas las empresas tienen detalles!")
        scraper.close()
        return
    
    print(f"\n📝 Encontradas {len(companies)} empresas sin detalles:\n")
    
    for i, company in enumerate(companies[:5], 1):
        print(f"{i}. {company['name']}")
        print(f"   └─ Ciudad: {company['city']}")
        print(f"   └─ NIT: {company['nit']}")
        print(f"   └─ URL La República: {company['url'][:60]}...")
    
    if len(companies) > 5:
        print(f"\n... y {len(companies) - 5} más")
    
    # Información sobre el scraper de Google Maps
    print("\n" + "-"*80)
    print("📌 INFORMACIÓN SOBRE SCRAPER DE GOOGLE MAPS:")
    print("-"*80)
    print("""
Para scrapear Google Maps, necesitaremos:

1️⃣  OPCIONES DE SCRAPING:

   A) Usar API oficial de Google Maps (recomendado)
      - Requiere API Key
      - Costo: ~$7 por 1000 búsquedas
      - Datos: Exactos y confiables
      
   B) Web Scraping con Selenium + BeautifulSoup
      - Requiere: Chrome/Chromium
      - Más lento: ~5-10 segundos por empresa
      - Riesgo de bloqueo por Google
      
   C) Usar búsqueda combinada
      - Google Maps para ubicación
      - LinkedIn/Páginas Web para contacto
      - WhatsApp Business para teléfono

2️⃣  DATOS A EXTRAER:

   ✅ Teléfono (de Google Maps o WhatsApp)
   ✅ Website/Página Web (si tiene)
   ✅ Dirección completa
   ✅ Horario de atención
   ✅ Coordenadas (lat/long)
   ✅ Link a Google Maps

3️⃣  ESTRUCTURA EN BD:

   Tabla: company_details
   ┌──────────────────┬─────────────┐
   │ company_id       │ 1           │
   │ phone            │ +57 123...  │
   │ website          │ https://... │
   │ address          │ Calle 5...  │
   │ latitude         │ 10.3898     │
   │ longitude        │ -75.5244    │
   │ google_maps_url  │ https://m.. │
   └──────────────────┴─────────────┘

¿Cuál opción prefieres?
""")
    
    print("\n" + "="*80 + "\n")
    
    scraper.close()

if __name__ == "__main__":
    main()
