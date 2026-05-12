"""
Scraper Mejorado - Búsqueda con múltiples fuentes colombianas
Busca automáticamente en: Informa Colombia, DuckDuckGo y websites de la empresa
"""

import sqlite3
import logging
import time
import re
import os
import random
import urllib.parse
from typing import Dict, Any, Optional, List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import requests
from services.informacolombia_scraper import InformaColombiaScraper

# Intentar importar psycopg2 para PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None
    RealDictCursor = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomaticDataScraper:
    """Scraper automático que busca datos en múltiples fuentes"""
    
    def __init__(self, db_path: str = "appdb.sqlite", db_type: str = "sqlite",
                 db_host: str = "localhost", db_port: int = 5432,
                 db_name: str = "appdb", db_user: str = "postgres", 
                 db_password: str = "postgres"):
        self.db_path = db_path
        self.db_type = db_type
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.conn = None
        self.informa_scraper = InformaColombiaScraper()
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_browser(self, headless: bool = True):
        """Obtiene el driver del navegador disponible con opciones anti-detección."""
        try:
            # En Docker, Firefox está disponible
            # Primero intentar Firefox (funciona en Docker)
            try:
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                # Anti-detection options for Firefox
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference("useAutomationExtension", False)
                options.set_preference("general.useragent.override", 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
                driver = webdriver.Firefox(options=options)
                logger.info("Firefox iniciado con opciones anti-detección")
                return driver
            except:
                pass
            
            # Intentar Edge (local)
            try:
                options = webdriver.EdgeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                driver = webdriver.Edge(options=options)
                logger.info("Edge iniciado")
                return driver
            except:
                pass
            
            # Intentar Chrome (local)
            try:
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                driver = webdriver.Chrome(options=options)
                logger.info("Chrome iniciado")
                return driver
            except:
                pass
        
        except Exception as e:
            logger.warning(f"No se pudo iniciar navegador: {e}")
        
        return None
    
    def connect_db(self) -> bool:
        try:
            # Intentar PostgreSQL si psycopg2 está disponible
            if psycopg2 is not None and self.db_type == "postgres":
                try:
                    self.conn = psycopg2.connect(
                        host=self.db_host,
                        port=self.db_port,
                        database=self.db_name,
                        user=self.db_user,
                        password=self.db_password
                    )
                    logger.info("Conectado a PostgreSQL")
                    return True
                except Exception as e:
                    logger.warning(f"No se pudo conectar a PostgreSQL ({e}), usando SQLite...")
            
            # Fallback a SQLite
            db_path = os.getenv("APP_DB_PATH", self.db_path)
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self._ensure_company_details_schema()
            logger.info("Conectado a SQLite")
            return True
        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False

    def _ensure_company_details_schema(self):
        """Añade columnas faltantes a company_details en SQLite."""
        if not self.conn or not isinstance(self.conn, sqlite3.Connection):
            return

        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(company_details)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            'nit': 'TEXT',
            'legal_status': 'TEXT',
            'city_info': 'TEXT',
            'department': 'TEXT',
            'verified': 'BOOLEAN DEFAULT 0',
            'verification_reason': 'TEXT',
        }

        for column_name, column_definition in required_columns.items():
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE company_details ADD COLUMN {column_name} {column_definition}")

        self.conn.commit()
    
    def close_db(self):
        if self.conn:
            self.conn.close()
    
    def close_browser(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extrae teléfono del texto usando múltiples patrones robustos"""
        
        # Excluir patrones de fecha antes de buscar teléfono para evitar falsos positivos
        text_clean = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)  # Excluir YYYY-MM-DD (ej: 2026-05-11)
        text_clean = re.sub(r'\d{2}/\d{2}/\d{4}', '', text_clean)  # Excluir DD/MM/YYYY
        text_clean = re.sub(r'\d{2}-\d{2}-\d{4}', '', text_clean)  # Excluir DD-MM-YYYY
        
        # Patrones para números colombianos (más flexibles)
        patterns = [
            r'\+57\s*[1-9]\s*[\d\s\-\(\)]{8,}',  # Números colombianos con +57
            r'\(?\d{1,3}\)?\s*[\d\s\-\(\)]{8,12}',  # Formato (1) 234-5678
            r'\d{3}[\s\-]?\d{3,4}[\s\-]?\d{4}',  # XXX-XXXX o XXX XXX XXXX
            r'\+\d{1,3}\s*\d{8,}',  # Cualquier número con +
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean)
            if match:
                phone = match.group(0).strip()
                phone = re.sub(r'[\s\-\.\)]+$', '', phone).strip()
                digits = re.sub(r'\D', '', phone)
                # Validar: 7-15 dígitos, sin dígitos muy repetidos
                if 7 <= len(digits) <= 15 and not re.match(r'^(\d)\1{4,}$', digits):
                    return phone
        
        return None
    
    def extract_website_from_text(self, text: str) -> Optional[str]:
        """Extrae website del texto usando múltiples patrones"""
        patterns = [
            r'https?://[^\s\)<>]+',  # URLs completas
            r'www\.[^\s\)<>]+',  # URLs www
            r'[a-zA-Z0-9.-]+\.(com|co|net|org|gov|com\.co|edu|io)[^\s\)<>]*',  # Dominios
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0).strip()
                if len(url) < 200 and not any(x in url.lower() for x in ['google', 'duckduckgo', 'facebook']):
                    return url
        return None

    def extract_address_from_text(self, text: str) -> Optional[str]:
        """Extrae dirección del texto usando patrones colombianos mejorados"""
        if not text or len(text) < 10:
            return None
        
        # Patrones para direcciones colombianas (más específicos)
        patterns = [
            # Completas: Calle/Carrera # - # Este / Oeste, Barrio, Ciudad
            r'(?:Calle|Cl|Carrera|Cr|Avenida|Av|Diagonal|Dg|Transversal|Tr)\s+[#\d]+\s*[-–]\s*[#\d]+(?:\s+[A-Z]\.)?(?:\s+[A-Za-záéíóúñ\s]*)?(?:\s+(?:Barrio|Localidad|Vereda)\s+[A-Za-záéíóúñ\s]+)?',
            # Con número y complemento: Calle 10A #23-45 interior 5
            r'(?:Calle|Cl|Carrera|Cr|Avenida|Av)\s+\d+[A-Z]?\s+#\s*\d+\s*[-–]\s*\d+(?:\s+\w+)?',
            # Formato simple: Calle 10 Número 23-45
            r'(?:Calle|Cl|Carrera|Cr|Avenida|Av)\s+\d+(?:\s+[A-Z])?(?:\s+Número|\s+N[oº])\s+\d+\s*[-–]\s*\d+',
            # Con barrio: Carrera 7 #45, Barrio San Alejo
            r'(?:Calle|Cl|Carrera|Cr|Avenida|Av)\s+[\d#]+[\s\-]*[\d]+(?:.*?(?:Barrio|Localidad|Vereda|Zona)\s+[A-Za-záéíóúñ\s]+)?',
            # Solo con keywords fuertes: Dirección Actual + contenido
            r'(?:Dirección|Domicilio)\s*[:=]?\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s,]{15,200}?)(?:(?:Tel|Teléfono|Actividad|Forma Jurídica|NIT|Web|Email)\b|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1) if '(' in pattern and match.lastindex else match.group(0)
                address = address.strip().strip(':-')
                
                # Validar longitud y descartar ruido
                if 8 < len(address) < 250:
                    # Remover marcadores comunes
                    address = re.sub(r'(?:Ver mapa|Cómo llegar|Ver en mapa|Obtenerlo ahora|>>|<<).*$', '', address, flags=re.IGNORECASE).strip()
                    if len(address) > 8 and not address.lower().startswith('n/a'):
                        return address
        
        return None

    def _build_html_soup(self, html: str) -> BeautifulSoup:
        """Construye un parser con el HTML disponible."""
        return BeautifulSoup(html or '', 'html.parser')

    def _normalize_results(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Limpia resultados vacíos y asegura llaves consistentes."""
        cleaned = {
            'phone': results.get('phone'),
            'website': results.get('website'),
            'address': results.get('address'),
        }

        for key, value in list(cleaned.items()):
            if isinstance(value, str):
                value = value.strip()
                if not value or value.lower() in ['n/a', 'no data', 'unknown']:
                    cleaned[key] = None
                else:
                    cleaned[key] = value

        return cleaned if any(cleaned.values()) else None

    def _extract_contact_from_html(self, html: str) -> Dict[str, Optional[str]]:
        """Extrae teléfono, website y dirección desde HTML genérico."""
        soup = self._build_html_soup(html)
        page_text = soup.get_text("\n", strip=True)

        results = {
            'phone': None,
            'website': None,
            'address': None,
            'nit': None,
            'legal_status': None,
            'city_info': None,
            'department': None,
        }

        phone_links = soup.find_all('a', href=re.compile(r'^tel:', re.IGNORECASE))
        if phone_links:
            phone = phone_links[0].get('href', '').replace('tel:', '').strip()
            if phone:
                results['phone'] = phone

        if not results['phone']:
            phone = self.extract_phone_from_text(page_text)
            if phone:
                results['phone'] = phone

        website_candidates = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            if href.startswith('http') and not any(x in href.lower() for x in ['google', 'maps', 'duckduckgo', 'facebook', 'instagram', 'youtube']):
                website_candidates.append(href)

        if website_candidates:
            results['website'] = website_candidates[0]
        else:
            website = self.extract_website_from_text(page_text)
            if website:
                results['website'] = website

        # Mejorado: Buscar dirección en atributos HTML primero
        address_selectors = [
            ('div', {'data-attrid': 'address'}),
            ('span', {'class': re.compile(r'address', re.IGNORECASE)}),
            ('div', {'class': re.compile(r'address', re.IGNORECASE)}),
            ('div', {'data-attrid': re.compile(r'address', re.IGNORECASE)}),
        ]
        for tag_name, attrs in address_selectors:
            address_elem = soup.find(tag_name, attrs=attrs)
            if address_elem:
                address = address_elem.get_text(" ", strip=True)
                if address:
                    results['address'] = address
                    break

        # Si no encontró en atributos, usar nuevo método mejorado
        if not results['address']:
            address = self.extract_address_from_text(page_text)
            if address:
                results['address'] = address

        nit_match = re.search(r'\bNIT\b\s*[:\-]?\s*(\d{8,15})', page_text, re.IGNORECASE)
        if nit_match:
            results['nit'] = nit_match.group(1).strip()

        legal_match = re.search(r'\bForma\s+Jur[ií]dica\b\s*[:\-]?\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ\s\.]{3,120})', page_text, re.IGNORECASE)
        if legal_match:
            results['legal_status'] = legal_match.group(1).strip()

        city_match = re.search(r'\bCiudad\b\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})', page_text, re.IGNORECASE)
        if city_match:
            results['city_info'] = city_match.group(1).strip()

        dept_match = re.search(r'\bDepartamento\b\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})', page_text, re.IGNORECASE)
        if dept_match:
            results['department'] = dept_match.group(1).strip()

        # Intentar extraer información de JSON-LD (structured data)
        try:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json as _json
                    data = _json.loads(script.string or '{}')
                except Exception:
                    continue

                # Data puede ser lista o dict
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    # LocalBusiness o similar
                    itype = item.get('@type') or item.get('type')
                    if itype and ('Business' in str(itype) or 'LocalBusiness' in str(itype) or 'Organization' in str(itype)):
                        # address puede ser objeto con streetAddress
                        addr = item.get('address')
                        if isinstance(addr, dict) and not results['address']:
                            parts = []
                            for k in ('streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry'):
                                v = addr.get(k)
                                if v:
                                    parts.append(v)
                            if parts:
                                results['address'] = ', '.join(parts)
                        # Si ya tenemos dirección, salir
                        if results['address']:
                            break
                if results['address']:
                    break
        except Exception:
            pass

        return results
    
    def search_duckduckgo(self, empresa_nombre: str, ciudad: str) -> Optional[Dict]:
        """Busca en DuckDuckGo con fallback a regex"""
        if not self.driver:
            return None
        
        try:
            logger.info(f"   Buscando en DuckDuckGo: {empresa_nombre}")
            
            query = f"{empresa_nombre} {ciudad} telefono contacto"
            url = f"https://duckduckgo.com/?q={query}&ia=web"
            
            self.driver.set_page_load_timeout(15)
            self.driver.get(url)
            time.sleep(3)
            
            soup = self._build_html_soup(self.driver.page_source)
            page_text = soup.get_text("\n", strip=True)
            
            results = {'phone': None, 'website': None}
            snippets = soup.find_all('span', {'data-result': 'snippet'})
            
            for snippet in snippets[:3]:
                text = snippet.get_text(strip=True)
                if not results['phone']:
                    phone = self.extract_phone_from_text(text)
                    if phone:
                        results['phone'] = phone
                        logger.info(f"      -> Teléfono: {results['phone']}")
                if not results['website']:
                    website = self.extract_website_from_text(text)
                    if website:
                        results['website'] = website
                        logger.info(f"      -> Website: {results['website']}")
            
            if not results['phone']:
                phone = self.extract_phone_from_text(page_text)
                if phone:
                    results['phone'] = phone
                    logger.info(f"      -> Teléfono (regex): {results['phone']}")
            
            return self._normalize_results(results)
        
        except Exception as e:
            logger.warning(f"   Error DuckDuckGo: {str(e)[:50]}")
            return None
    
    
    def search_google_web(self, empresa_nombre: str, ciudad: str) -> Optional[Dict]:
        """Búsqueda en DuckDuckGo (más permisiva con scrapers que Google)"""
        try:
            logger.info(f"   Buscando en DuckDuckGo: {empresa_nombre}")
            
            # Búsqueda específica para datos de contacto
            search_query = f"{empresa_nombre} {ciudad} telefono contacto"
            search_url = f"https://duckduckgo.com/html/?q={requests.utils.quote(search_query)}"
            
            logger.info(f"   Navegando a DuckDuckGo: {search_query}")
            
            # Agregar delay aleatorio para evitar bloqueos
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            # Headers realistas
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'es-CO,es;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Connection': 'keep-alive',
            }
            
            try:
                # DuckDuckGo HTML endpoint no requiere JavaScript
                response = self.session.get(search_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                html = response.text
                logger.info(f"   Página obtenida: {len(html)} bytes")
                
                # Verificar si estamos siendo bloqueados
                if 'blocked' in html.lower() or 'captcha' in html.lower():
                    logger.warning("   DuckDuckGo está bloqueando")
                    return None
                
            except requests.exceptions.RequestException as req_error:
                logger.warning(f"   Error HTTP en DuckDuckGo: {str(req_error)[:80]}")
                return None
            
            # Extraer datos del HTML
            results = self._extract_search_results(html)
            
            if results.get('phone'):
                logger.info(f"      -> Teléfono: {results['phone']}")
            if results.get('website'):
                logger.info(f"      -> Website: {results['website']}")
            if results.get('address'):
                logger.info(f"      -> Dirección: {results['address'][:50]}")
            
            return self._normalize_results(results)
        
        except Exception as e:
            logger.warning(f"   Error búsqueda DuckDuckGo: {str(e)[:80]}")
            return None
    
    def _extract_search_results(self, html: str) -> Dict[str, Optional[str]]:
        """Extrae teléfono, website y dirección de resultados de búsqueda (genérico para múltiples motores)"""
        results = {'phone': None, 'website': None, 'address': None}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            all_text = soup.get_text("\n")
            
            # Extraer teléfono
            phone = self.extract_phone_from_text(all_text)
            if phone:
                results['phone'] = phone
                logger.debug(f"      Teléfono extraído: {phone}")
            
            # Extraer website: buscar links que no sean del motor de búsqueda
            links = soup.find_all('a', href=re.compile(r'https?://.*'))
            for link in links:
                href = link.get('href', '').strip()
                
                # Filtrar URLs del motor de búsqueda
                if href and href.startswith('http'):
                    # DuckDuckGo usa redirecciones /l/
                    if '/l/?uddg=' in href:
                        # Extraer la URL real de la redirección
                        try:
                            params = urllib.parse.urlparse(href).query
                            actual_url = urllib.parse.parse_qs(params).get('uddg', [''])[0]
                            if actual_url:
                                href = actual_url
                        except:
                            continue
                    
                    # Filtrar: debe ser HTTP(S), no del motor, no gestor
                    if (href.startswith('http') and 
                        'duckduckgo' not in href.lower() and 
                        'google' not in href.lower() and 
                        'webcache' not in href.lower() and
                        not self._is_website_host_provider(href)):
                        if not results['website']:
                            results['website'] = href
                            logger.debug(f"      Website extraído: {href}")
                            break
            
            # Mejorado: Extraer dirección usando el nuevo método
            address = self.extract_address_from_text(all_text)
            if address:
                results['address'] = address
                logger.debug(f"      Dirección extraída: {address}")
            
            return results
            
        except Exception as e:
            logger.debug(f"   Error extrayendo de búsqueda: {e}")
            return results
    
    def search_local_directory(self, empresa_nombre: str, ciudad: str) -> Optional[Dict]:
        """Busca en Páginas Amarillas - REQUIERE SELENIUM para JavaScript"""
        try:
            logger.info(f"   Buscando en Páginas Amarillas: {empresa_nombre}")
            
            # Inicializar driver si no existe
            if not self.driver:
                self.driver = self.get_browser()
                if not self.driver:
                    logger.warning("   No se pudo inicializar navegador para Páginas Amarillas")
                    return None
            
            # Construir URL de búsqueda
            search_query = f"{empresa_nombre} {ciudad}"
            search_url = f"https://www.paginasamarillas.com.co/search?q={requests.utils.quote(empresa_nombre)}&location={requests.utils.quote(ciudad)}"
            
            logger.info(f"   Navegando a: {search_url}")
            
            try:
                self.driver.set_page_load_timeout(20)
                self.driver.get(search_url)
                
                # Esperar a que carguen los resultados
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='result'], [class*='item'], div[data-testid]"))
                    )
                except:
                    logger.debug("   Timeout esperando resultados, continuando con lo que hay")
                
                # Esperar más tiempo para que se cargue JavaScript
                time.sleep(5)
                
                # Obtener el HTML renderizado
                html = self.driver.page_source
                logger.info(f"   Página renderizada: {len(html)} bytes")
                
            except Exception as driver_error:
                logger.warning(f"   Error Selenium: {str(driver_error)[:80]}")
                return None
            
            # Extraer datos del HTML renderizado
            results = self._extract_paginas_amarillas(html, empresa_nombre)
            
            if results.get('phone'):
                logger.info(f"      -> Teléfono: {results['phone']}")
            if results.get('website'):
                logger.info(f"      -> Website: {results['website']}")
            if results.get('address'):
                logger.info(f"      -> Dirección: {results['address'][:40]}")
            
            return self._normalize_results(results)
        
        except Exception as e:
            logger.warning(f"   Error búsqueda de directorios: {str(e)[:80]}")
            return None
    
    def _extract_paginas_amarillas(self, html: str, empresa_nombre: str) -> Dict[str, Optional[str]]:
        """Extrae teléfono, website y dirección de HTML de Páginas Amarillas"""
        results = {'phone': None, 'website': None, 'address': None}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar todos los textos con patrones de teléfono y website
            # en el HTML
            all_text = soup.get_text("\n")
            
            # Extraer teléfono
            phone = self.extract_phone_from_text(all_text)
            if phone:
                results['phone'] = phone
            
            # Buscar website: links a dominios .co, .com, etc (excluir gestores)
            links = soup.find_all('a', href=re.compile(r'https?://.*\.\w{2,}'))
            for link in links:
                href = link.get('href', '').strip()
                if href and not self._is_website_host_provider(href) and 'paginasamarillas' not in href.lower():
                    if not results['website']:
                        results['website'] = href
                        break
            
            # Mejorado: Usar nuevo método para extraer dirección
            address = self.extract_address_from_text(all_text)
            if address:
                results['address'] = address
            
            return results
            
        except Exception as e:
            logger.debug(f"   Error extrayendo de Páginas Amarillas: {e}")
            return results
    
    def search_google_maps(self, empresa_nombre: str, ciudad: str) -> Optional[Dict]:
        """Busca en Google Maps con fallback robusta a regex"""
        try:
            logger.info(f"   Buscando en Google Maps: {empresa_nombre}")
            
            search_query = f"{empresa_nombre} {ciudad}"
            url = f"https://www.google.com/maps/search/{requests.utils.quote(search_query)}"

            html = None

            if self.driver:
                try:
                    self.driver.set_page_load_timeout(15)
                    self.driver.get(url)

                    time.sleep(4)
                    html = self.driver.page_source
                except Exception as browser_error:
                    logger.warning(f"   Google Maps con navegador falló: {str(browser_error)[:80]}")

            if not html:
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
                html = response.text

            results = self._extract_contact_from_html(html)

            if results.get('phone'):
                logger.info(f"      -> Teléfono: {results['phone']}")
            if results.get('address'):
                logger.info(f"      -> Dirección: {results['address'][:40]}")
            if results.get('website'):
                logger.info(f"      -> Website: {results['website'][:40]}")

            return self._normalize_results(results)
        
        except Exception as e:
            logger.warning(f"   Error Google Maps: {str(e)[:50]}")
            return None
    
    def _is_website_host_provider(self, website: str) -> bool:
        """Detecta si la URL es de un proveedor de hosting/gestor (no de empresa real)"""
        host_providers = [
            'gurusoluciones.com',
            'wix.com',
            'godaddy.com',
            'wordpress.com',
            'blogger.com',
            'weebly.com',
            'jimdo.com',
            'squarespace.com',
            'webnode.com',
            'strikingly.com',
            'carrd.co',
            'pages.github.io',
            'github.io',
        ]
        domain = website.lower().split('/')[2] if 'http' in website else website.lower()
        return any(provider in domain for provider in host_providers)

    def scrape_company(self, company_id: int, company_name: str, city: str, larepublica_url: str = None, nit: str = None) -> Optional[Dict[str, Any]]:
        """Extrae datos de una empresa buscando en múltiples fuentes.

        Flujo actual:
        1. Informa Colombia como fuente principal.
        2. DuckDuckGo como fallback si Informa no aporta teléfono.
        3. Website de la empresa si existe un dominio válido.
        """
        
        print(f"\n[Scraping] {company_name} ({city})")
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'nit': None,
            'legal_status': None,
            'city_info': None,
            'department': None,
            'activity': None,
            'legal_status': None,
            'nit': None,
            'employees': None,
            'sources': [],
            'verified': False,
            'verification_reason': None,
            'status': 'partial'
        }
        
        try:
            # Inicializar driver si no existe
            if not self.driver:
                self.driver = self.get_browser()
                if not self.driver:
                    logger.warning("   No se pudo inicializar navegador")
                    return results
            
            logger.info(f"   Búsqueda iniciada: {company_name}")
            
            # 1. FUENTE PRINCIPAL: Informa Colombia (Directorio Oficial)
            data = self.informa_scraper.scrape_company(company_name, city, nit)
            if data:
                for key, value in data.items():
                    if key in results and value and not results[key]:
                        results[key] = value
                results['sources'].append('informacolombia')
                results['verified'] = True
                results['verification_reason'] = 'informa_colombia_profile'
                strategy_used = self.informa_scraper.last_used_strategy or "unknown"
                logger.info(f"   ✓ Datos extraídos de Informa Colombia [{strategy_used}]")

            # 2. FALLBACK: DuckDuckGo si Informa no completó datos clave
            if not results.get('phone') or not results.get('website') or not results.get('address'):
                data_fallback = self.search_duckduckgo(company_name, city)
                if data_fallback:
                    for key, value in data_fallback.items():
                        if key in results and value and not results[key]:
                            results[key] = value
                    results['sources'].append('duckduckgo')
                    if not results.get('verified'):
                        results['verification_reason'] = 'duckduckgo_fallback'

            # Si Informa no devolvió ficha real, pero sí pudimos completar por website,
            # marcar como no verificado para que el front no lo trate como dato oficial.
            if results.get('website') and 'website' in results.get('sources', []) and not results.get('verified'):
                results['verification_reason'] = 'website_fallback'
        
        except Exception as e:
            logger.error(f"Error scraping {company_name}: {e}")
        
        # Si faltan datos de contacto y hay website válido (no gestor), intentar extraer desde el website
        if (not results.get('phone') or not results.get('address')) and results.get('website'):
            if not self._is_website_host_provider(results.get('website')):
                try:
                    url = results.get('website')
                    if url and not url.startswith('http'):
                        url = 'http://' + url
                    logger.info(f"   Descargando website: {url}")
                    resp = self.session.get(url, timeout=10)
                    if resp.status_code == 200 and resp.text:
                        site_info = self._extract_contact_from_html(resp.text)
                        if site_info:
                            if not results.get('phone') and site_info.get('phone'):
                                results['phone'] = site_info.get('phone')
                                results['sources'].append('website')
                                logger.info(f"   Teléfono extraído del website")
                            if not results.get('address') and site_info.get('address'):
                                results['address'] = site_info.get('address')
                                results['sources'].append('website')
                            for field in ('nit', 'legal_status', 'city_info', 'department'):
                                if not results.get(field) and site_info.get(field):
                                    results[field] = site_info.get(field)
                                    results['sources'].append('website')
                        if not results.get('verified') and any([site_info.get('phone'), site_info.get('address')]):
                            results['verification_reason'] = 'website_fallback'
                except Exception as e:
                    logger.debug(f"No se pudo scrapear website válido: {e}")

        # Determinar estado
        if results['phone'] or results['website'] or results['address']:
            results['status'] = 'completed' if results['phone'] else 'partial'

        # Si el teléfono vino de fuentes de fallback o la página de Informa fue genérica,
        # exponerlo como no verificado para el front.
        if results.get('verification_reason') in {'duckduckgo_fallback', 'website_fallback'}:
            results['verified'] = False

        logger.info(f"   -> Estado: {results['status']} | Fuentes: {', '.join(results['sources'])}")

        return results
    
    def get_pending_companies(self, limit: int = 50) -> List:
        """Obtiene empresas sin detalles"""
        try:
            cursor = self.conn.cursor()
            
            # Query para PostgreSQL y SQLite es similar
            query = """
                SELECT c.id, c.name, c.city, c.nit
                FROM companies c
                LEFT JOIN company_details cd ON c.id = cd.company_id
                WHERE c.is_active = true
                AND (cd.id IS NULL 
                     OR cd.phone = 'N/A' 
                     OR cd.phone IS NULL)
                ORDER BY c.name
                LIMIT %s
            """ if isinstance(self.conn, type(None)) or (hasattr(self.conn, 'driver_version')) else """
                SELECT c.id, c.name, c.city, c.nit
                FROM companies c
                LEFT JOIN company_details cd ON c.id = cd.company_id
                WHERE c.is_active = 1
                AND (cd.id IS NULL 
                     OR cd.phone = 'N/A' 
                     OR cd.phone IS NULL)
                ORDER BY c.name
                LIMIT ?
            """
            
            # Usar placeholder correcto según la BD
            if psycopg2 and isinstance(self.conn, psycopg2.extensions.connection):
                cursor.execute(query, (limit,))
            else:
                cursor.execute(query.replace('%s', '?'), (limit,))
            
            results = cursor.fetchall()
            
            # Convertir sqlite3.Row a dict para compatibilidad
            result_dicts = []
            for row in results:
                if isinstance(row, dict):
                    result_dicts.append(row)
                else:
                    # sqlite3.Row
                    result_dicts.append({
                        'id': row[0],
                        'name': row[1],
                        'city': row[2],
                        'nit': row[3]
                    })
            
            logger.info(f"Encontradas {len(result_dicts)} empresas para procesar")
            return result_dicts
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def save_details(self, company_id: int, details: Dict[str, Any]) -> bool:
        """Guarda detalles en BD (PostgreSQL o SQLite)"""
        try:
            cursor = self.conn.cursor()
            
            if not any([details.get('phone'), details.get('website'), details.get('address'), details.get('nit'), details.get('legal_status'), details.get('city_info'), details.get('department')]):
                logger.warning("   No hay datos para guardar")
                return False
            
            # Usar INSERT ON CONFLICT para PostgreSQL, INSERT OR REPLACE para SQLite
            if psycopg2 and isinstance(self.conn, psycopg2.extensions.connection):
                # PostgreSQL
                cursor.execute("""
                    INSERT INTO company_details 
                    (company_id, phone, website, address, nit, legal_status, city_info, department, verified, verification_reason, scraped_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (company_id) 
                    DO UPDATE SET 
                        phone = EXCLUDED.phone,
                        website = EXCLUDED.website,
                        address = EXCLUDED.address,
                        nit = EXCLUDED.nit,
                        legal_status = EXCLUDED.legal_status,
                        city_info = EXCLUDED.city_info,
                        department = EXCLUDED.department,
                        verified = EXCLUDED.verified,
                        verification_reason = EXCLUDED.verification_reason,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    company_id,
                    details.get('phone') or 'N/A',
                    details.get('website') or 'N/A',
                    details.get('address') or 'N/A',
                    details.get('nit') or 'N/A',
                    details.get('legal_status') or 'N/A',
                    details.get('city_info') or 'N/A',
                    details.get('department') or 'N/A',
                    1 if details.get('verified') else 0,
                    details.get('verification_reason'),
                    datetime.now().isoformat()
                ))
            else:
                # SQLite
                cursor.execute("""
                    INSERT OR REPLACE INTO company_details 
                    (company_id, phone, website, address, nit, legal_status, city_info, department, verified, verification_reason, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    details.get('phone') or 'N/A',
                    details.get('website') or 'N/A',
                    details.get('address') or 'N/A',
                    details.get('nit') or 'N/A',
                    details.get('legal_status') or 'N/A',
                    details.get('city_info') or 'N/A',
                    details.get('department') or 'N/A',
                    1 if details.get('verified') else 0,
                    details.get('verification_reason'),
                    datetime.now().isoformat()
                ))
            
            self.conn.commit()
            logger.info("   ✓ Datos guardados en BD")
            return True
        
        except Exception as e:
            logger.error(f"   Error guardando: {e}")
            return False
    
    def process_companies(self, limit: int = 10) -> Dict[str, Any]:
        """Procesa todas las empresas"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'No se pudo conectar a BD'}
        
        # Iniciar navegador
        self.driver = self.get_browser()
        if not self.driver:
            logger.warning("Continuando sin navegador (requests only)")
        
        companies = self.get_pending_companies(limit)
        
        if not companies:
            self.close_db()
            self.close_browser()
            return {
                'success': True,
                'total': 0,
                'processed': 0,
                'message': 'Todas las empresas tienen detalles'
            }
        
        logger.info("\n" + "="*80)
        logger.info(f"SCRAPER AUTOMÁTICO - Procesando {len(companies)} empresas")
        logger.info("="*80 + "\n")
        
        successful = 0
        
        try:
            for i, company in enumerate(companies, 1):
                try:
                    print(f"\n[{i}/{len(companies)}] {company['name']}")
                    print(f"      NIT: {company['nit']} | Ciudad: {company['city']}")
                    
                    details = self.scrape_company(
                        company['id'],
                        company['name'],
                        company['city'],
                        nit=company.get('nit')
                    )
                    
                    if details and self.save_details(company['id'], details):
                        successful += 1
                
                except Exception as e:
                    logger.error(f"Error procesando: {e}")
                
                time.sleep(2)
        
        finally:
            self.close_db()
            self.close_browser()
        
        logger.info("\n" + "="*80)
        logger.info(f"COMPLETADO: {successful} de {len(companies)} empresas enriquecidas")
        logger.info("="*80)
        
        return {
            'success': True,
            'total': len(companies),
            'processed': successful,
            'message': f'{successful} de {len(companies)} empresas enriquecidas'
        }


def main():
    print("\n" + "="*80)
    print("SCRAPER AUTOMÁTICO MEJORADO")
    print("Búsqueda multi-fuente: Informa Colombia + DuckDuckGo + website fallback")
    print("="*80)
    
    # Configurar BD desde variables de entorno
    db_type = "postgres" if os.getenv("DB_HOST") else "sqlite"
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "appdb")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
    
    scraper = AutomaticDataScraper(
        db_path=db_path,
        db_type=db_type,
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password
    )
    result = scraper.process_companies(limit=10)
    
    print("\n" + "="*80)
    print("RESULTADO FINAL")
    print("="*80)
    print(f"Total procesadas: {result['total']}")
    print(f"Exitosas: {result['processed']}")
    print(f"Mensaje: {result['message']}")
    print()


if __name__ == "__main__":
    main()
