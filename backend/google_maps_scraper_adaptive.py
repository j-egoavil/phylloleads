"""
Google Maps Scraper - Versión Adaptable
Intenta usar Selenium + ChromeDriver primero
Si no está disponible, usa métodos alternativos
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
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium no disponible, usando métodos alternativos")


class AdaptiveMapsScraper:
    """Scraper que se adapta según recursos disponibles"""
    
    def __init__(self, db_path: str = "appdb.sqlite", force_requests: bool = False):
        """
        Inicializa el scraper
        
        Args:
            db_path: Ruta a BD SQLite
            force_requests: Forzar usar requests en lugar de Selenium
        """
        self.db_path = db_path
        self.conn = None
        self.driver = None
        self.use_selenium = False
        self.force_requests = force_requests
        
        # Configurar sesion de requests
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9',
        }
        self.session.headers.update(self.headers)
        
        # Detectar ChromeDriver
        self._detect_chromedriver()
    
    def _detect_chromedriver(self):
        """Detecta si ChromeDriver está disponible"""
        if self.force_requests:
            logger.info("Forzando uso de requests (sin Selenium)")
            return
        
        if not SELENIUM_AVAILABLE:
            logger.info("Selenium no disponible, usando requests")
            return
        
        chromedriver_paths = [
            './chromedriver.exe',
            './chromedriver',
            '/usr/local/bin/chromedriver',
            '/opt/chromedriver',
        ]
        
        for path in chromedriver_paths:
            if os.path.exists(path):
                try:
                    logger.info("ChromeDriver encontrado en: {}".format(path))
                    options = Options()
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--start-maximized')
                    
                    self.driver = webdriver.Chrome(path, options=options)
                    self.use_selenium = True
                    logger.info("Selenium + ChromeDriver ACTIVADO")
                    return
                
                except Exception as e:
                    logger.warning("Error inicializando ChromeDriver: {}".format(e))
                    continue
        
        logger.info("ChromeDriver no encontrado, usando requests + BeautifulSoup")
    
    def connect_db(self) -> bool:
        """Conecta a BD"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info("Conectado a BD: {}".format(self.db_path))
            return True
        except Exception as e:
            logger.error("Error conectando a BD: {}".format(e))
            return False
    
    def close_db(self):
        """Cierra BD"""
        if self.conn:
            self.conn.close()
    
    def close_driver(self):
        """Cierra Selenium"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    # ==================== BÚSQUEDA CON SELENIUM ====================
    
    def search_with_selenium(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca con Selenium + Chrome"""
        if not self.use_selenium:
            return None
        
        try:
            logger.info("   [Selenium] Buscando en Google Maps...")
            
            search_query = "{} {} Colombia".format(company_name, city)
            url = "https://www.google.com/maps/search/{}".format(urllib.parse.quote(search_query))
            
            self.driver.get(url)
            time.sleep(3)  # Esperar a que cargue
            
            # Extraer teléfono del DOM
            page_source = self.driver.page_source
            
            results = {
                'phone': self.extract_phone(page_source),
                'website': None,
                'address': self.extract_address(page_source)
            }
            
            # Buscar website
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, 'a[href^="http"]')
                if website_elem:
                    results['website'] = website_elem.get_attribute('href')
            except:
                pass
            
            if any(results.values()):
                logger.info("   Datos encontrados con Selenium")
                for key, value in results.items():
                    if value:
                        logger.info("        -> {}: {}".format(key.capitalize(), str(value)[:50]))
            
            return results
        
        except Exception as e:
            logger.warning("   [Selenium] Error: {}".format(str(e)[:80]))
            return None
    
    # ==================== BÚSQUEDA CON REQUESTS ====================
    
    def search_with_requests(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca con requests + BeautifulSoup"""
        try:
            logger.info("   [Requests] Buscando...")
            
            search_query = "{} {} Colombia telefono".format(company_name, city)
            
            # Intentar búsqueda en Google
            url = "https://www.google.com/search"
            params = {
                'q': search_query,
                'num': 5
            }
            
            response = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Combinar todos los textos
            text = soup.get_text()
            
            results = {
                'phone': self.extract_phone(text),
                'website': None,
                'address': self.extract_address(text)
            }
            
            # Buscar links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and 'google' not in href:
                    results['website'] = href
                    break
            
            if any(results.values()):
                logger.info("   Datos encontrados con Requests")
                for key, value in results.items():
                    if value:
                        logger.info("        -> {}: {}".format(key.capitalize(), str(value)[:50]))
            
            return results
        
        except Exception as e:
            logger.warning("   [Requests] Error: {}".format(str(e)[:80]))
            return None
    
    # ==================== EXTRACCIÓN DE DATOS ====================
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extrae números de teléfono colombianos"""
        patterns = [
            r'\+57\s*[1-9]\s*[\d\s\-\(\)]{7,10}',
            r'\+57\d{10}',
            r'(?:tel|telefono|phone)[\s:]*\+?57[\s\-]?[\d\s\-\(\)]{10,}',
            r'\(?[0-9]{1,3}\)?[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = match.group(0)
                phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
                phone = phone.strip()
                
                digits = re.sub(r'\D', '', phone)
                if len(digits) >= 10:
                    return phone
        
        return None
    
    def extract_address(self, text: str) -> Optional[str]:
        """Extrae direcciones colombianas"""
        patterns = [
            r'(?:cra|carrera|calle|av|avenida|diagonal|transversal)\s+\#?\d+[\s\#\-]*\d+[\s\-]*\d*[\s\-]*[^,\n]{0,30}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(0).strip()
                if 15 < len(address) < 150:
                    return address
        
        return None
    
    # ==================== BÚSQUEDA ADAPTABLE ====================
    
    def scrape_company(self, company_name: str, city: str) -> Optional[Dict[str, Any]]:
        """Scrape usando el mejor método disponible"""
        
        print("\n{} Buscando: {} ({})".format("="*3, company_name, city))
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'sources': [],
            'status': 'partial'
        }
        
        # INTENTO 1: Selenium (si disponible)
        if self.use_selenium:
            logger.info("1. Intentando con Selenium + Chrome...")
            data = self.search_with_selenium(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append('selenium')
                time.sleep(2)
        
        # INTENTO 2: Requests
        if not results['phone'] or not results['website']:
            logger.info("2. Intentando con Requests + Google...")
            data = self.search_with_requests(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append('requests')
            time.sleep(2)
        
        # Estado final
        if results['phone'] or results['website'] or results['address']:
            completed = sum(1 for v in results.values() if v and v not in [[], {}])
            results['status'] = 'completed' if completed >= 2 else 'partial'
        
        logger.info("   Estado: {}".format(results['status']))
        logger.info("   Fuentes: {}".format(', '.join(results['sources']) or 'ninguna'))
        
        return results
    
    # ==================== BASE DE DATOS ====================
    
    def get_pending_companies(self, limit: int = 50) -> List[Tuple]:
        """Obtiene empresas sin detalles"""
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
        """Guarda detalles en BD"""
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
            logger.info("   Datos guardados en BD")
            return True
        
        except Exception as e:
            logger.error("   Error: {}".format(e))
            return False
    
    # ==================== PROCESAMIENTO ====================
    
    def process_companies(self, limit: int = 5) -> Dict[str, Any]:
        """Procesa empresas"""
        
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
        logger.info("PROCESANDO {} EMPRESAS".format(len(companies)))
        logger.info("Método: {} + {}".format(
            "SELENIUM + CHROME" if self.use_selenium else "REQUESTS",
            "Fallback disponible"
        ))
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
                
                time.sleep(2)
        
        finally:
            self.close_db()
            self.close_driver()
        
        logger.info("\n" + "="*80)
        logger.info("COMPLETADO: {} de {} empresas procesadas".format(successful, len(companies)))
        logger.info("="*80)
        
        return {
            'success': True,
            'total': len(companies),
            'processed': successful,
            'message': '{} de {} empresas enriquecidas'.format(successful, len(companies))
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SCRAPER ADAPTABLE: Selenium + ChromeDriver OR Requests")
    print("="*80)
    
    scraper = AdaptiveMapsScraper(force_requests=False)  # Cambiar a True para forzar requests
    result = scraper.process_companies(limit=1)
    
    print("\nResultado:")
    print("  Total procesadas: {}".format(result['total']))
    print("  Exitosas: {}".format(result['processed']))
    print("  Mensaje: {}".format(result['message']))
