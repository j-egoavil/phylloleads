"""
Google Maps Scraper - Web Scraping con Selenium
Extrae: Telefono, Website, Direccion, Coordenadas
"""

import sqlite3
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
import re
import urllib.parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Advertencia: Selenium no esta instalado")

from bs4 import BeautifulSoup


class GoogleMapsScraper:
    """Scraper de Google Maps usando Selenium"""
    
    def __init__(self, db_path: str = "appdb.sqlite", headless: bool = True):
        """Inicializa el scraper"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium no esta disponible")
        
        self.db_path = db_path
        self.headless = headless
        self.driver = None
        self.conn = None
        self.base_url = "https://maps.google.com/maps"
    
    def connect_db(self):
        """Conecta a la BD"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info("Conectado a BD")
    
    def init_driver(self):
        """Inicializa el driver de Selenium"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium no disponible")
        
        logger.info("Iniciando navegador Chrome...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        chrome_options.add_argument("--start-maximized")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Navegador iniciado")
            return True
        except Exception as e:
            logger.error("Error iniciando navegador: {}".format(e))
            return False
    
    def close_driver(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()
            logger.info("Navegador cerrado")
    
    def extract_phone(self, html: str) -> Optional[str]:
        """Extrae numero de telefono del HTML"""
        patterns = [
            r'\+57\s*\d{1,3}\s*\d{3,4}\s*\d{4}',
            r'\+57\s*\d{10}',
            r'\(\d{1,3}\)\s*\d{3,4}\s*\d{4}',
            r'\d{7,10}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(0).strip()
        
        return None
    
    def extract_website(self, html: str) -> Optional[str]:
        """Extrae website del HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            if 'http' in href and 'google' not in href and 'maps' not in href:
                if href.startswith('http'):
                    cleaned = href.split('&')[0]
                    if len(cleaned) > 15:
                        return cleaned
        
        url_pattern = r'https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+'
        match = re.search(url_pattern, html)
        if match:
            return match.group(0)
        
        return None
    
    def extract_address(self, html: str) -> Optional[str]:
        """Extrae direccion del HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text()
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 15 and len(line) < 150:
                if any(char.isdigit() for char in line):
                    if not any(word in line.lower() for word in ['lunes', 'martes', 'abierto', 'cerrado']):
                        return line
        
        return None
    
    def extract_coordinates(self, google_maps_url: str) -> tuple:
        """Extrae coordenadas del URL de Google Maps"""
        try:
            if '@' in google_maps_url:
                coords_part = google_maps_url.split('@')[1].split('z')[0]
                lat, lng = coords_part.split(',')[:2]
                return float(lat), float(lng)
        except:
            pass
        
        return None, None
    
    def scrape_company(self, company_name: str, city: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Scrape informacion de una empresa desde Google Maps"""
        
        for attempt in range(retries):
            try:
                logger.info("Buscando: '{}' en {}".format(company_name, city))
                
                search_query = "{} {} Colombia".format(company_name, city)
                encoded_query = urllib.parse.quote(search_query)
                search_url = "{}?q={}".format(self.base_url, encoded_query)
                
                self.driver.get(search_url)
                time.sleep(3)
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "Nj2zr"))
                    )
                except TimeoutException:
                    logger.warning("Timeout esperando resultados")
                    continue
                
                html = self.driver.page_source
                
                phone = self.extract_phone(html)
                website = self.extract_website(html)
                address = self.extract_address(html)
                
                lat, lng = self.extract_coordinates(self.driver.current_url)
                
                details = {
                    'phone': phone or 'N/A',
                    'website': website or 'N/A',
                    'address': address or 'N/A',
                    'latitude': lat,
                    'longitude': lng,
                    'google_maps_url': self.driver.current_url,
                    'status': 'completed'
                }
                
                logger.info("Datos encontrados para '{}'".format(company_name))
                return details
            
            except Exception as e:
                logger.warning("Error en intento {}: {}".format(attempt + 1, e))
                if attempt < retries - 1:
                    time.sleep(2)
                continue
        
        logger.error("No se pudo obtener informacion para '{}'".format(company_name))
        return None
    
    def get_pending_companies(self, limit: int = 50) -> list:
        """Obtiene empresas sin detalles"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.city
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE cd.id IS NULL
            AND c.is_active = 1
            ORDER BY c.name
            LIMIT ?
        """, (limit,))
        
        return cursor.fetchall()
    
    def save_details(self, company_id: int, details: Dict[str, Any]) -> bool:
        """Guarda detalles de empresa en BD"""
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
            logger.error("Error guardando: {}".format(e))
            return False
    
    def process_companies(self, limit: int = 5) -> Dict[str, Any]:
        """Procesa empresas sin detalles"""
        
        self.connect_db()
        
        if not self.init_driver():
            return {'success': False, 'error': 'No se pudo inicializar Selenium'}
        
        companies = self.get_pending_companies(limit)
        
        if not companies:
            logger.info("Todas las empresas tienen detalles")
            self.close_driver()
            return {
                'success': True,
                'total': 0,
                'processed': 0,
                'message': 'Todas las empresas tienen detalles'
            }
        
        logger.info("PROCESANDO {} EMPRESAS".format(len(companies)))
        
        processed = 0
        successful = 0
        
        try:
            for i, company in enumerate(companies, 1):
                try:
                    print("\n{}. {}".format(i, company['name']))
                    
                    details = self.scrape_company(company['name'], company['city'])
                    
                    if details:
                        saved = self.save_details(company['id'], details)
                        
                        if saved:
                            print("   GUARDADO EN BD")
                            print("   Telefono: {}".format(details.get('phone')))
                            print("   Website: {}".format(details.get('website')))
                            print("   Direccion: {}".format(details.get('address')[:60] if details.get('address') else 'N/A'))
                            successful += 1
                        else:
                            print("   ERROR AL GUARDAR")
                    else:
                        print("   SIN DATOS")
                    
                    processed += 1
                    time.sleep(2)
                
                except Exception as e:
                    logger.error("Error procesando empresa {}: {}".format(i, e))
                    processed += 1
                    continue
        
        finally:
            self.close_driver()
            if self.conn:
                self.conn.close()
        
        print("\nPROCESAMIENTO COMPLETADO")
        print("   Total procesadas: {}".format(processed))
        print("   Exitosas: {}".format(successful))
        print("   Fallidas: {}".format(processed - successful))
        
        return {
            'success': True,
            'total': len(companies),
            'processed': processed,
            'successful': successful,
            'failed': processed - successful
        }
    
    def close(self):
        """Limpia recursos"""
        self.close_driver()
        if self.conn:
            self.conn.close()


def main():
    """Main"""
    
    print("\n" + "="*80)
    print("GOOGLE MAPS SCRAPER - WEB SCRAPING CON SELENIUM")
    print("="*80)
    
    if not SELENIUM_AVAILABLE:
        print("\nError: Selenium no esta instalado")
        print("Instala con: pip install selenium")
        return
    
    scraper = GoogleMapsScraper(headless=False)
    
    try:
        result = scraper.process_companies(limit=3)
        
        if result['success']:
            print("\nScraping completado")
        else:
            print("\nError: {}".format(result.get('error')))
    
    except KeyboardInterrupt:
        print("\n\nScraping cancelado por el usuario")
    except Exception as e:
        logger.error("Error: {}".format(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
