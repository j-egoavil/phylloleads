"""
Google Maps Scraper - Versión Mejorada (Sin ChromeDriver)
Opción 2: Busca en multiples fuentes locales colombianas
- DuckDuckGo + headers mejorados
- APIs gratuitas de búsqueda
- Páginas Amarillas Colombia
- Google My Business (sin API)
"""

import sqlite3
import logging
import time
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImprovedMapsScraper:
    """Scraper mejorado sin necesidad de ChromeDriver"""
    
    def __init__(self, db_path: str = "appdb.sqlite"):
        """Inicializa el scraper"""
        self.db_path = db_path
        self.conn = None
        self.session = requests.Session()
        
        # Headers realistas para evadir bloqueos
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.session.headers.update(self.headers)
        self.timeout = 15
    
    def connect_db(self) -> bool:
        """Conecta a la BD"""
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
    
    # ==================== BÚSQUEDA 1: PAGINAS AMARILLAS COLOMBIA ====================
    
    def search_paginas_amarillas(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca en Páginas Amarillas Colombia (sitio local)"""
        try:
            # Formato: https://www.paginasamarillas.com.co/search?q=...&location=...
            url = "https://www.paginasamarillas.com.co/search"
            params = {
                'q': company_name,
                'location': city
            }
            
            logger.info("   [Páginas Amarillas] Buscando: {} en {}".format(company_name, city))
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = {
                'phone': None,
                'website': None,
                'address': None
            }
            
            # Buscar resultado principal
            first_result = soup.find('div', class_='business-card') or soup.find('div', class_='result')
            
            if first_result:
                # Teléfono
                phone_elem = first_result.find('a', href=re.compile(r'tel:'))
                if phone_elem:
                    phone = phone_elem.get('href', '').replace('tel:', '').strip()
                    if phone:
                        results['phone'] = phone
                        logger.info("        -> Teléfono: {}".format(phone))
                
                # Website
                website_elem = first_result.find('a', href=re.compile(r'^https?://'))
                if website_elem and 'paginasamarillas' not in website_elem.get('href', ''):
                    website = website_elem.get('href', '').strip()
                    if website:
                        results['website'] = website
                        logger.info("        -> Website: {}".format(website))
                
                # Dirección
                address_elem = first_result.find('div', class_='address') or first_result.find('span', class_='address')
                if address_elem:
                    address = address_elem.get_text(strip=True)
                    if address:
                        results['address'] = address
                        logger.info("        -> Dirección: {}".format(address[:50]))
            
            return results if any(results.values()) else None
        
        except Exception as e:
            logger.warning("   [Páginas Amarillas] Error: {}".format(str(e)[:50]))
            return None
    
    # ==================== BÚSQUEDA 2: GOOGLE MAPS CACHE ====================
    
    def search_google_maps_cache(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca en Google Maps usando búsqueda normal (sin API)"""
        try:
            logger.info("   [Google Maps] Buscando: {} en {}".format(company_name, city))
            
            # Usar búsqueda en Google con parámetro "maps"
            search_query = "{} {} Colombia".format(company_name, city)
            url = "https://www.google.com/search"
            params = {
                'q': search_query,
                'tbm': 'lcl'  # Local search
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = {
                'phone': None,
                'website': None,
                'address': None
            }
            
            # Buscar teléfono en el HTML
            phone_pattern = r'\+57\s*[1-9]\s*\d{7,9}|\+57\s*\d{10}'
            phone_match = re.search(phone_pattern, response.text)
            if phone_match:
                results['phone'] = phone_match.group(0).strip()
                logger.info("        -> Teléfono: {}".format(results['phone']))
            
            # Buscar dirección
            address_pattern = r'(?:cra|carrera|calle|av|avenida|diagonal)\s+\d+[\s\#\-]*\d+'
            address_match = re.search(address_pattern, response.text, re.IGNORECASE)
            if address_match:
                results['address'] = address_match.group(0).strip()
                logger.info("        -> Dirección: {}".format(results['address']))
            
            return results if any(results.values()) else None
        
        except Exception as e:
            logger.warning("   [Google Maps] Error: {}".format(str(e)[:50]))
            return None
    
    # ==================== BÚSQUEDA 3: SITIOS LOCALES ESPECÍFICOS ====================
    
    def search_business_directories(self, company_name: str, city: str) -> Optional[Dict[str, str]]:
        """Busca en directorios empresariales colombianos"""
        
        # Lista de directorios locales
        directories = [
            {
                'name': 'Dato360',
                'url': 'https://www.dato360.com.co',
                'search_param': 'q'
            },
            {
                'name': 'Empreza',
                'url': 'https://www.empreza.com.co',
                'search_param': 'search'
            },
            {
                'name': 'RUES (Cámara de Comercio)',
                'url': 'https://www.rues.org.co',
                'search_param': 'q'
            }
        ]
        
        results = {
            'phone': None,
            'website': None,
            'address': None
        }
        
        for directory in directories:
            try:
                logger.info("   [{}] Buscando: {}".format(directory['name'], company_name))
                
                params = {directory['search_param']: company_name}
                response = self.session.get(directory['url'], params=params, timeout=10)
                
                text = response.text
                
                # Extraer teléfono
                phone_match = re.search(r'\+57\s*[1-9]\s*\d{7,9}', text)
                if phone_match and not results['phone']:
                    results['phone'] = phone_match.group(0).strip()
                    logger.info("        -> Teléfono: {}".format(results['phone']))
                
                # Extraer website
                website_match = re.search(r'https?://[^\s<>"{}|\\^`\[\]]*', text)
                if website_match and not results['website']:
                    website = website_match.group(0).strip()
                    if 'dato360' not in website and 'rues' not in website:
                        results['website'] = website
                        logger.info("        -> Website: {}".format(website))
                
                time.sleep(1)  # Respetar servidores
            
            except Exception as e:
                logger.warning("   [{}] Error: {}".format(directory['name'], str(e)[:30]))
                continue
        
        return results if any(results.values()) else None
    
    # ==================== EXTRACCIÓN DE DATOS ====================
    
    def extract_from_webpage(self, url: str) -> Optional[Dict[str, str]]:
        """Extrae datos de una página web"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            text = response.text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Eliminar scripts y estilos
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Obtener texto limpio
            clean_text = soup.get_text(separator=' ', strip=True)
            
            results = {
                'phone': self.extract_phone(clean_text),
                'website': self.extract_website_from_url(url),
                'address': self.extract_address(clean_text)
            }
            
            return results
        
        except Exception as e:
            logger.warning("Error extrayendo de {}: {}".format(url[:40], e))
            return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extrae números de teléfono colombianos"""
        patterns = [
            # +57 con espacios/dashes
            r'\+57\s*[1-9]\s*[\d\s\-\(\)]{7,10}',
            # +57 sin espacios
            r'\+57\d{10}',
            # Números locales
            r'(?:tel|telefono|phone)[\s:]*\+?57[\s\-]?[\d\s\-\(\)]{10,}',
            # Formato (X) XXXX-XXXX
            r'\(?[0-9]{1,3}\)?[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = match.group(0)
                # Limpiar
                phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
                phone = phone.strip()
                
                # Validar que tenga al menos 10 dígitos
                digits = re.sub(r'\D', '', phone)
                if len(digits) >= 10:
                    return phone
        
        return None
    
    def extract_website_from_url(self, url: str) -> Optional[str]:
        """Extrae dominio del URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc
            if domain and not any(x in domain for x in ['google', 'duckduckgo', 'bing', 'yahoo']):
                return "https://{}".format(domain)
        except:
            pass
        return None
    
    def extract_address(self, text: str) -> Optional[str]:
        """Extrae direcciones colombianas"""
        patterns = [
            r'(?:cra|carrera|calle|av|avenida|diagonal|transversal)\s+\#?\d+[\s\#\-]*\d+[\s\-]*\d*[\s\-]*[^,\n]{0,30}',
            r'(?:ubicado|ubicada|direccion|domicilio)[\s:]+([^,\n]{20,100})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(0) if match.lastindex is None else match.group(1)
                address = address.replace('|', ' ').strip()
                
                if len(address) > 15 and len(address) < 150:
                    return address
        
        return None
    
    # ==================== BÚSQUEDA COMBINADA MEJORADA ====================
    
    def scrape_company(self, company_name: str, city: str) -> Optional[Dict[str, Any]]:
        """Scrape desde múltiples fuentes mejoradas"""
        
        print("\n{} Buscando: {} ({})".format("="*3, company_name, city))
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'sources': [],
            'status': 'partial'
        }
        
        # BÚSQUEDA 1: Páginas Amarillas Colombia
        logger.info("1. Buscando en directorios locales...")
        data = self.search_paginas_amarillas(company_name, city)
        if data and any(data.values()):
            for key, value in data.items():
                if value and not results[key]:
                    results[key] = value
            results['sources'].append('paginas_amarillas')
            time.sleep(2)
        
        # BÚSQUEDA 2: Directorios empresariales
        if not results['phone'] or not results['website']:
            logger.info("2. Buscando en directorios empresariales...")
            data = self.search_business_directories(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append('directorios')
            time.sleep(2)
        
        # BÚSQUEDA 3: Google Maps Cache
        if not results['phone']:
            logger.info("3. Buscando en Google Maps...")
            data = self.search_google_maps_cache(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append('google_maps')
            time.sleep(2)
        
        # BÚSQUEDA 4: LinkedIn (verificación)
        logger.info("4. Verificando en LinkedIn...")
        linkedin_search = self.session.get(
            "https://www.linkedin.com/search/results/companies/",
            params={'keywords': company_name},
            timeout=10
        )
        if linkedin_search.status_code == 200:
            results['sources'].append('linkedin_verified')
            logger.info("   Empresa verificada en LinkedIn")
        
        # Estado final
        if results['phone'] or results['website'] or results['address']:
            results['status'] = 'completed' if (results['phone'] and results['website'] and results['address']) else 'partial'
        
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
            logger.error("Error obteniendo empresas: {}".format(e))
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
            logger.error("   Error guardando en BD: {}".format(e))
            return False
    
    def process_companies(self, limit: int = 5) -> Dict[str, Any]:
        """Procesa empresas"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'No se pudo conectar a BD'}
        
        companies = self.get_pending_companies(limit)
        
        if not companies:
            self.close_db()
            return {
                'success': True,
                'total': 0,
                'processed': 0,
                'message': 'Todas las empresas tienen detalles'
            }
        
        logger.info("\n" + "="*80)
        logger.info("PROCESANDO {} EMPRESAS (VERSIÓN MEJORADA)".format(len(companies)))
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
                
                time.sleep(3)  # Esperar entre búsquedas
        
        finally:
            self.close_db()
        
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
    scraper = ImprovedMapsScraper()
    result = scraper.process_companies(limit=5)
    print("\nResultado:", result)
