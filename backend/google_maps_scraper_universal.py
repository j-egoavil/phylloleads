"""
Google Maps Scraper - Versión UNIVERSAL
Detecta automáticamente: Chrome, Opera, Firefox, Edge
Usa el que encuentre disponible
"""

import sqlite3
import logging
import time
import re
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class UniversalMapsScraper:
    """Scraper que usa el navegador disponible"""
    
    def __init__(self, db_path: str = "appdb.sqlite"):
        self.db_path = db_path
        self.conn = None
        self.driver = None
        self.browser_name = None
        self.use_browser = False
        
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9',
        }
        self.session.headers.update(self.headers)
        
        self._detect_browser()
    
    def _detect_browser(self):
        """Detecta qué navegador está disponible"""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium no instalado. Instala con: pip install selenium")
            return
        
        browsers = [
            {
                'name': 'Opera',
                'paths': [
                    r"C:\Program Files\Opera\opera.exe",
                    r"C:\Program Files (x86)\Opera\opera.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\opera.exe"),
                ],
                'driver_class': 'Opera'
            },
            {
                'name': 'Chrome',
                'paths': [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                ],
                'driver_class': 'Chrome'
            },
            {
                'name': 'Firefox',
                'paths': [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                    os.path.expandvars(r"%PROGRAMFILES%\Mozilla Firefox\firefox.exe"),
                ],
                'driver_class': 'Firefox'
            },
            {
                'name': 'Edge',
                'paths': [
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
                ],
                'driver_class': 'Edge'
            },
        ]
        
        logger.info("Buscando navegadores disponibles...")
        
        for browser in browsers:
            for path in browser['paths']:
                if os.path.exists(path):
                    logger.info("Encontrado: {} en {}".format(browser['name'], path))
                    
                    if self._init_browser(browser['driver_class'], browser['name']):
                        return
        
        logger.error("Ningún navegador encontrado.")
        logger.info("Navegadores soportados: Opera, Chrome, Firefox, Edge")
        logger.info("Descarga uno desde:")
        logger.info("  - Opera: https://www.opera.com/")
        logger.info("  - Chrome: https://www.google.com/chrome/")
        logger.info("  - Firefox: https://www.mozilla.org/firefox/")
        logger.info("  - Edge: https://www.microsoft.com/edge/")
    
    def _init_browser(self, driver_class: str, browser_name: str) -> bool:
        """Inicializa el navegador"""
        try:
            logger.info("Inicializando {}Driver...".format(driver_class))
            
            # Configurar opciones
            if driver_class == 'Opera':
                from selenium.webdriver.opera.options import Options
                options = Options()
            elif driver_class == 'Chrome':
                from selenium.webdriver.chrome.options import Options
                options = Options()
            elif driver_class == 'Firefox':
                from selenium.webdriver.firefox.options import Options
                options = Options()
            elif driver_class == 'Edge':
                from selenium.webdriver.edge.options import Options
                options = Options()
            
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            
            # Crear driver
            if driver_class == 'Opera':
                self.driver = webdriver.Opera(options=options)
            elif driver_class == 'Chrome':
                self.driver = webdriver.Chrome(options=options)
            elif driver_class == 'Firefox':
                self.driver = webdriver.Firefox(options=options)
            elif driver_class == 'Edge':
                self.driver = webdriver.Edge(options=options)
            
            self.browser_name = browser_name
            self.use_browser = True
            logger.info("{} ACTIVADO".format(browser_name))
            return True
        
        except Exception as e:
            logger.warning("Error con {}: {}".format(driver_class, str(e)[:80]))
            return False
    
    def connect_db(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info("Conectado a BD")
            return True
        except Exception as e:
            logger.error("Error BD: {}".format(e))
            return False
    
    def close_db(self):
        if self.conn:
            self.conn.close()
    
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def search_with_browser(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca con el navegador disponible"""
        if not self.use_browser:
            return None
        
        try:
            logger.info("   [{}] Buscando en Google Maps...".format(self.browser_name))
            
            search_query = "{} {} Colombia".format(company_name, city)
            url = "https://www.google.com/maps/search/{}".format(urllib.parse.quote(search_query))
            
            self.driver.get(url)
            time.sleep(4)
            
            page_source = self.driver.page_source
            
            results = {
                'phone': self.extract_phone(page_source),
                'website': None,
                'address': self.extract_address(page_source)
            }
            
            # Buscar website
            website_matches = re.findall(r'href="(https?://[^"]+)"', page_source)
            for match in website_matches:
                if not any(x in match for x in ['google', 'maps', 'youtube']):
                    results['website'] = match
                    break
            
            if any(results.values()):
                logger.info("   Datos encontrados")
                for key, value in results.items():
                    if value:
                        logger.info("        -> {}: {}".format(key.capitalize(), str(value)[:50]))
            
            return results
        
        except Exception as e:
            logger.warning("   Error: {}".format(str(e)[:80]))
            return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        patterns = [
            r'\+57\s*[1-9]\s*[\d\s\-\(\)]{7,10}',
            r'\+57\d{10}',
            r'(?:tel|telefono|phone)[\s:]*\+?57[\s\-]?[\d\s\-\(\)]{10,}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = re.sub(r'[^\d\+\-\(\)\s]', '', match.group(0))
                if len(re.sub(r'\D', '', phone)) >= 10:
                    return phone.strip()
        return None
    
    def extract_address(self, text: str) -> Optional[str]:
        pattern = r'(?:cra|carrera|calle|av|avenida|diagonal|transversal)\s+\#?\d+[\s\#\-]*\d+[\s\-]*[^,\n]{0,30}'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            address = match.group(0).strip()
            if 15 < len(address) < 150:
                return address
        return None
    
    def scrape_company(self, company_name: str, city: str) -> Dict[str, Any]:
        print("\n=== Buscando: {} ({})".format(company_name, city))
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'sources': [],
            'status': 'partial'
        }
        
        if self.use_browser:
            logger.info("1. Buscando con {}...".format(self.browser_name))
            data = self.search_with_browser(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append(self.browser_name.lower())
                time.sleep(2)
        
        if results['phone'] or results['website'] or results['address']:
            results['status'] = 'completed' if all(results.values()) else 'partial'
        
        logger.info("   Estado: {}".format(results['status']))
        logger.info("   Fuentes: {}".format(', '.join(results['sources']) or 'ninguna'))
        return results
    
    def get_pending_companies(self, limit: int = 50) -> List[Tuple]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.city, c.nit
                FROM companies c
                LEFT JOIN company_details cd ON c.id = cd.company_id
                WHERE cd.id IS NULL
                AND c.is_active = 1
                ORDER BY c.name
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            logger.info("Encontradas {} empresas sin detalles".format(len(results)))
            return results
        except Exception as e:
            logger.error("Error: {}".format(e))
            return []
    
    def save_details(self, company_id: int, details: Dict[str, Any]) -> bool:
        try:
            cursor = self.conn.cursor()
            
            if not any([details.get('phone'), details.get('website'), details.get('address')]):
                logger.warning("   No hay datos para guardar")
                return False
            
            cursor.execute("""
                INSERT OR REPLACE INTO company_details 
                (company_id, phone, website, address, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                company_id,
                details.get('phone') or 'N/A',
                details.get('website') or 'N/A',
                details.get('address') or 'N/A',
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            logger.info("   Datos guardados")
            return True
        except Exception as e:
            logger.error("   Error: {}".format(e))
            return False
    
    def process_companies(self, limit: int = 5) -> Dict[str, Any]:
        if not self.connect_db():
            return {'success': False, 'error': 'No se pudo conectar a BD'}
        
        companies = self.get_pending_companies(limit)
        
        if not companies:
            self.close_db()
            self.close_driver()
            return {
                'success': True,
                'total': 0,
                'processed': 0,
                'message': 'Todas las empresas tienen detalles'
            }
        
        logger.info("\n" + "="*80)
        logger.info("PROCESANDO {} EMPRESAS CON {}".format(len(companies), self.browser_name or "REQUESTS"))
        logger.info("="*80 + "\n")
        
        successful = 0
        
        try:
            for i, company in enumerate(companies, 1):
                try:
                    print("\n[{}/{}] {}".format(i, len(companies), company['name']))
                    print("      NIT: {} | Ciudad: {}".format(company['nit'], company['city']))
                    
                    details = self.scrape_company(company['name'], company['city'])
                    
                    if details and self.save_details(company['id'], details):
                        successful += 1
                
                except Exception as e:
                    logger.error("Error: {}".format(e))
                
                time.sleep(3)
        
        finally:
            self.close_db()
            self.close_driver()
        
        logger.info("\n" + "="*80)
        logger.info("COMPLETADO: {} de {} empresas".format(successful, len(companies)))
        logger.info("="*80)
        
        return {
            'success': True,
            'total': len(companies),
            'processed': successful,
            'message': '{} de {} empresas enriquecidas'.format(successful, len(companies))
        }


def main():
    print("\n" + "="*80)
    print("SCRAPER UNIVERSAL - Detecta navegador automáticamente")
    print("="*80)
    
    scraper = UniversalMapsScraper()
    
    if not scraper.use_browser:
        print("\nNingún navegador encontrado.")
        print("\nInstala uno de estos:")
        print("  - Opera: https://www.opera.com/")
        print("  - Chrome: https://www.google.com/chrome/")
        print("  - Firefox: https://www.mozilla.org/firefox/")
        print("  - Edge: https://www.microsoft.com/edge/")
        return
    
    result = scraper.process_companies(limit=1)
    
    print("\nResultado:")
    print("  Navegador: {}".format(scraper.browser_name))
    print("  Procesadas: {}".format(result['total']))
    print("  Exitosas: {}".format(result['processed']))


if __name__ == "__main__":
    main()
