"""
Google Maps Scraper - Versión OPERA
Usa Opera en lugar de Chrome (mismo motor Chromium)
No necesita ChromeDriver, usa OperaDriver
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

# Intentar importar Selenium para Opera
try:
    from selenium import webdriver
    from selenium.webdriver.opera.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
    logger.info("Selenium disponible para Opera")
except ImportError as e:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium no disponible: {}".format(e))


class OperaMapsScraper:
    """Scraper usando Opera + Selenium"""
    
    def __init__(self, db_path: str = "appdb.sqlite"):
        """
        Inicializa el scraper con Opera
        
        Args:
            db_path: Ruta a BD SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.driver = None
        self.use_opera = False
        
        # Configurar sesion de requests (fallback)
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9',
        }
        self.session.headers.update(self.headers)
        
        # Detectar Opera
        self._detect_opera()
    
    def _detect_opera(self):
        """Detecta si Opera está instalado y disponible"""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium no disponible, instalando...")
            os.system("pip install selenium")
            return
        
        # Rutas posibles de Opera en Windows
        opera_paths = [
            r"C:\Program Files\Opera\opera.exe",
            r"C:\Program Files (x86)\Opera\opera.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\opera.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Opera\opera.exe"),
        ]
        
        logger.info("Buscando Opera...")
        opera_found = None
        
        for path in opera_paths:
            if os.path.exists(path):
                logger.info("Opera encontrado en: {}".format(path))
                opera_found = path
                break
        
        if not opera_found:
            logger.error("Opera no encontrado en rutas estándar")
            logger.info("Instalando Opera... (https://www.opera.com)")
            return
        
        try:
            logger.info("Inicializando OperaDriver...")
            
            # Configurar opciones de Opera
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--start-maximized')
            
            # Crear instancia de Opera
            self.driver = webdriver.Opera(options=options)
            self.use_opera = True
            
            logger.info("OperaDriver ACTIVADO - Listo para scraping")
        
        except Exception as e:
            logger.error("Error inicializando Opera: {}".format(e))
            logger.info("Asegúrate de tener Opera instalado")
            self.use_opera = False
    
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
        """Cierra Opera"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    # ==================== BÚSQUEDA CON OPERA ====================
    
    def search_with_opera(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca con Opera + Selenium"""
        if not self.use_opera:
            logger.warning("Opera no disponible")
            return None
        
        try:
            logger.info("   [Opera] Buscando en Google Maps...")
            
            search_query = "{} {} Colombia".format(company_name, city)
            url = "https://www.google.com/maps/search/{}".format(urllib.parse.quote(search_query))
            
            self.driver.get(url)
            time.sleep(4)  # Esperar a que cargue Maps
            
            # Extraer información del DOM
            page_source = self.driver.page_source
            
            results = {
                'phone': self.extract_phone(page_source),
                'website': None,
                'address': self.extract_address(page_source)
            }
            
            # Buscar website
            try:
                # Buscar en los elementos de la página
                website_matches = re.findall(r'href="(https?://[^"]+)"', page_source)
                for match in website_matches:
                    if 'google' not in match and 'maps' not in match:
                        results['website'] = match
                        break
            except:
                pass
            
            if any(results.values()):
                logger.info("   Datos encontrados con Opera")
                for key, value in results.items():
                    if value:
                        logger.info("        -> {}: {}".format(key.capitalize(), str(value)[:60]))
            
            return results
        
        except Exception as e:
            logger.error("   [Opera] Error: {}".format(str(e)[:80]))
            return None
    
    def search_with_requests(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Búsqueda fallback con requests"""
        try:
            logger.info("   [Requests] Búsqueda alternativa...")
            
            search_query = "{} {} Colombia telefono".format(company_name, city)
            url = "https://www.google.com/search"
            params = {'q': search_query, 'num': 5}
            
            response = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            results = {
                'phone': self.extract_phone(text),
                'website': None,
                'address': self.extract_address(text)
            }
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and 'google' not in href:
                    results['website'] = href
                    break
            
            if any(results.values()):
                logger.info("   Datos encontrados con Requests")
            
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
    
    # ==================== BÚSQUEDA PRINCIPAL ====================
    
    def scrape_company(self, company_name: str, city: str) -> Optional[Dict[str, Any]]:
        """Scrape usando Opera"""
        
        print("\n{} Buscando: {} ({})".format("="*3, company_name, city))
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'sources': [],
            'status': 'partial'
        }
        
        # INTENTO 1: Opera
        if self.use_opera:
            logger.info("1. Buscando con Opera + Google Maps...")
            data = self.search_with_opera(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append('opera_maps')
                time.sleep(2)
        
        # INTENTO 2: Requests (fallback)
        if not results['phone'] or not results['website']:
            logger.info("2. Buscando alternativo con Requests...")
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
        logger.info("PROCESANDO {} EMPRESAS CON OPERA".format(len(companies)))
        logger.info("Método: Opera + Google Maps")
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
                    logger.error("Error procesando empresa: {}".format(e))
                
                time.sleep(3)
        
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


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("SCRAPER CON OPERA (No necesita ChromeDriver)")
    print("="*80)
    
    # Crear scraper
    scraper = OperaMapsScraper()
    
    if not scraper.use_opera:
        print("\nOPERACION REQUERIDA:")
        print("1. Instala Opera desde: https://www.opera.com/")
        print("2. Asegúrate que esté en 'C:/Program Files/Opera/opera.exe'")
        print("3. Ejecuta este script de nuevo")
        return
    
    # Procesar empresa (1 de prueba)
    result = scraper.process_companies(limit=1)
    
    print("\nResultado:")
    print("  Total procesadas: {}".format(result['total']))
    print("  Exitosas: {}".format(result['processed']))
    print("  Mensaje: {}".format(result['message']))


if __name__ == "__main__":
    main()
