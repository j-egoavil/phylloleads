import logging
import re
import time
import html as html_lib
import requests
import unicodedata
from typing import Dict, Optional, Any, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

logger = logging.getLogger(__name__)


class InformaColombiaScraper:
    """Scraper para el directorio público de Informa Colombia."""

    BASE_URL = "https://www.informacolombia.com/directorio-empresas"

    def __init__(self):
        self.driver = None
        self.strategy_log = []  # Registra qué estrategia funcionó para cada empresa
        self.last_used_strategy = None  # Estrategia usada en la última búsqueda
        self.last_request_time = 0  # Para controlar delays entre requests

    def _name_to_slug(self, name: str) -> str:
        """Convierte razón social a slug de Informa Colombia.
        
        Ejemplos:
        - "Veterinarias SAS" -> "veterinarias-sas"
        - "Distribuciones Veterinarias SA SoC" -> "distribuciones-veterinarias-sa-soc"
        """
        # Normalizar acentos
        name = unicodedata.normalize('NFKD', name)
        name = ''.join(c for c in name if not unicodedata.combining(c))
        
        # Minúsculas
        name = name.lower()
        
        # Reemplazar caracteres especiales con guiones
        name = re.sub(r'[^a-z0-9\s]', ' ', name)
        
        # Espacios múltiples a simples
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Espacios a guiones
        name = re.sub(r'\s+', '-', name)
        
        return name

    def scrape_by_direct_url(self, name: str, city: str = "", nit: str = "") -> Tuple[Optional[Dict[str, Any]], str]:
        """ESTRATEGIA 4: Usa requests + BeautifulSoup para acceder directo a la URL.
        
        Sin Selenium, sin búsqueda. Simplemente genera el slug e intenta acceder.
        Retorna (datos, estrategia_usada).
        """
        try:
            # Delay inteligente para evitar rate limiting
            time_since_last = time.time() - self.last_request_time
            if time_since_last < 5:
                delay = 5 - time_since_last + (2 if time_since_last < 2 else 1 if time_since_last < 3.5 else 0)
                logger.info(f"   [Informa-Direct] ⏳ Esperando {delay:.1f}s para evitar rate limit (429)...")
                time.sleep(delay)
            self.last_request_time = time.time()
            
            slug = self._name_to_slug(name)
            if not slug:
                logger.info(f"   [Informa-Direct] No se pudo generar slug para: {name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'slug_generation_failed'
                })
                return None, "direct_url_failed"

            url = f"https://www.informacolombia.com/directorio-empresas/informacion-empresa/{slug}"
            logger.info(f"   [Informa-Direct] GET {url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-CO,es;q=0.9',
                'Referer': 'https://www.informacolombia.com/',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 429:
                logger.warning(f"   [Informa-Direct] ⚠️ Rate limit (429) - Informa nos está bloqueando")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'rate_limit_429'
                })
                return None, "direct_url_rate_limit"
            
            if response.status_code == 410:
                logger.warning(f"   [Informa-Direct] Empresa no existe en Informa (410)")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'not_found_410'
                })
                return None, "direct_url_not_found"
            
            if response.status_code != 200:
                logger.warning(f"   [Informa-Direct] Status {response.status_code} para {name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': f'http_error_{response.status_code}'
                })
                return None, f"direct_url_http_error_{response.status_code}"

            page_text = response.text
            soup = BeautifulSoup(page_text, 'html.parser')

            # Detectar si es página genérica
            if self._is_generic_informa_page(response.text, name):
                logger.warning(f"   [Informa-Direct] Página genérica detectada para {name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'direct_url_generic_page'
                })
                return None, "direct_url_generic_page"

            # Extraer datos usando métodos existentes
            table_fields = self._extract_table_fields(soup)
            informa_address = self._extract_address_from_informa_html(page_text)
            if informa_address and not table_fields.get('address'):
                table_fields['address'] = informa_address

            data = {
                'nit': table_fields.get('nit') or self._extract_text(page_text, r'\bNIT\b\s*(\d{8,15})'),
                'phone': table_fields.get('phone') or self._extract_text(page_text, r'\bTel[eé]fono\b\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{6,20})'),
                'address': table_fields.get('address') or self._extract_text(page_text, r'\bDirecci[oó]n\s+Actual\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{8,220}?)(?:\s+(?:Cómo llegar|Ver Mapa|NIT|Actividad|Forma Jurídica|Ranking)|$)'),
                'website': self._extract_website(soup),
                'activity': table_fields.get('activity') or self._extract_text(page_text, r'\bActividad\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Forma Jurídica|Ranking|NIT)|$)'),
                'legal_status': table_fields.get('legal_status') or self._extract_text(page_text, r'\bForma\s+Jur[ií]dica\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Ranking|NIT)|$)'),
                'city_info': table_fields.get('city_info') or self._extract_text(page_text, r'\bCiudad\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'department': table_fields.get('department') or self._extract_text(page_text, r'\bDepartamento\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'source': 'informacolombia'
            }

            # Limpieza final
            for key, value in list(data.items()):
                if isinstance(value, str):
                    value = value.strip().strip(':-')
                    if not value or 'DISPONIBLE' in value.upper() or value.lower() in {'ver mapa', 'cómo llegar', 'obtenerlo ahora >>'}:
                        data[key] = None
                    else:
                        data[key] = value

            logger.info(f"   [Informa-Direct] ✓ Datos extraídos para {name}")
            self.strategy_log.append({
                'company': name,
                'strategy': 'direct_url',
                'success': True,
                'result': 'direct_url_success'
            })
            return data, "direct_url_success"

        except Exception as e:
            logger.error(f"   [Informa-Direct] Error: {e}")
            self.strategy_log.append({
                'company': name,
                'strategy': 'direct_url',
                'success': False,
                'result': f'direct_url_exception'
            })
            return None, "direct_url_exception"

    def scrape_by_search_requests(self, name: str, city: str = "", nit: str = "") -> Tuple[Optional[Dict[str, Any]], str]:
        """ESTRATEGIA 2: Búsqueda con requests + BeautifulSoup (sin Selenium).
        
        Realiza búsqueda directamente con HTTP GET/POST, parsea HTML de resultados.
        Retorna (datos, estrategia_usada).
        
        Más rápido que Selenium, menos detectable, pero requiere conocer estructura Informa.
        """
        try:
            # Delay anti-rate-limit
            time_since_last = time.time() - self.last_request_time
            if time_since_last < 5:
                delay = 5 - time_since_last + (2 if time_since_last < 2 else 1 if time_since_last < 3.5 else 0)
                logger.info(f"   [Informa-Search] ⏳ Esperando {delay:.1f}s para evitar rate limit...")
                time.sleep(delay)
            self.last_request_time = time.time()

            search_name = re.sub(r'\s+', ' ', (name or '')).strip()
            if not search_name:
                logger.info(f"   [Informa-Search] Nombre no disponible")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'search_requests',
                    'success': False,
                    'result': 'invalid_name'
                })
                return None, "search_requests_invalid_name"

            logger.info(f"   [Informa-Search] Buscando empresa: {search_name}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-CO,es;q=0.9',
                'Referer': 'https://www.informacolombia.com/',
                'Connection': 'keep-alive',
            }

            # 1. Intentar búsqueda directa con parámetro GET
            search_url = f"{self.BASE_URL}?q={requests.utils.quote(search_name)}"
            logger.info(f"   [Informa-Search] GET {search_url}")
            
            resp = requests.get(search_url, headers=headers, timeout=15)
            
            if resp.status_code == 429:
                logger.warning(f"   [Informa-Search] ⚠️ Rate limit (429)")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'search_requests',
                    'success': False,
                    'result': 'rate_limit_429'
                })
                return None, "search_requests_rate_limit"
            
            if resp.status_code != 200:
                logger.warning(f"   [Informa-Search] Status {resp.status_code}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'search_requests',
                    'success': False,
                    'result': f'http_error_{resp.status_code}'
                })
                return None, f"search_requests_http_error_{resp.status_code}"

            # 2. Parsear página de búsqueda
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Buscar enlace al perfil de empresa en resultados
            profile_link = None
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                if '/directorio-empresas/informacion-empresa/' in href:
                    profile_link = href if href.startswith('http') else self._absolute_url(href)
                    logger.info(f"   [Informa-Search] Perfil encontrado: {profile_link}")
                    break

            if not profile_link:
                logger.warning(f"   [Informa-Search] No se encontró perfil para: {search_name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'search_requests',
                    'success': False,
                    'result': 'no_profile_found'
                })
                return None, "search_requests_no_profile"

            # Delay antes de acceder al perfil
            time.sleep(2)
            self.last_request_time = time.time()

            # 3. Acceder al perfil
            logger.info(f"   [Informa-Search] Accediendo al perfil...")
            resp_profile = requests.get(profile_link, headers=headers, timeout=15)
            
            if resp_profile.status_code != 200:
                logger.warning(f"   [Informa-Search] Status {resp_profile.status_code} en perfil")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'search_requests',
                    'success': False,
                    'result': f'profile_http_error_{resp_profile.status_code}'
                })
                return None, f"search_requests_profile_error"

            # 4. Detectar página genérica/CAPTCHA
            if self._is_generic_informa_page(resp_profile.text, search_name):
                logger.warning(f"   [Informa-Search] Página genérica detectada")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'search_requests',
                    'success': False,
                    'result': 'generic_page'
                })
                return None, "search_requests_generic_page"

            # 5. Extraer datos del perfil
            profile_soup = BeautifulSoup(resp_profile.text, 'html.parser')
            table_fields = self._extract_table_fields(profile_soup)
            informa_address = self._extract_address_from_informa_html(resp_profile.text)
            if informa_address and not table_fields.get('address'):
                table_fields['address'] = informa_address

            data = {
                'nit': table_fields.get('nit') or self._extract_text(resp_profile.text, r'\bNIT\b\s*(\d{8,15})'),
                'phone': table_fields.get('phone') or self._extract_text(resp_profile.text, r'\bTel[eé]fono\b\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{6,20})'),
                'address': table_fields.get('address') or self._extract_text(resp_profile.text, r'\bDirecci[oó]n\s+Actual\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{8,220}?)(?:\s+(?:Cómo llegar|Ver Mapa|NIT|Actividad|Forma Jurídica|Ranking)|$)'),
                'website': self._extract_website(profile_soup),
                'activity': table_fields.get('activity') or self._extract_text(resp_profile.text, r'\bActividad\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Forma Jurídica|Ranking|NIT)|$)'),
                'legal_status': table_fields.get('legal_status') or self._extract_text(resp_profile.text, r'\bForma\s+Jur[ií]dica\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Ranking|NIT)|$)'),
                'city_info': table_fields.get('city_info') or self._extract_text(resp_profile.text, r'\bCiudad\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'department': table_fields.get('department') or self._extract_text(resp_profile.text, r'\bDepartamento\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'source': 'informacolombia'
            }

            # Limpieza final
            for key, value in list(data.items()):
                if isinstance(value, str):
                    value = value.strip().strip(':-')
                    if not value or 'DISPONIBLE' in value.upper() or value.lower() in {'ver mapa', 'cómo llegar', 'obtenerlo ahora >>'}:
                        data[key] = None
                    else:
                        data[key] = value

            logger.info(f"   [Informa-Search] ✓ Datos extraídos para {search_name}")
            self.strategy_log.append({
                'company': name,
                'strategy': 'search_requests',
                'success': True,
                'result': 'search_requests_success'
            })
            return data, "search_requests_success"

        except Exception as e:
            logger.error(f"   [Informa-Search] Error: {e}")
            self.strategy_log.append({
                'company': name,
                'strategy': 'search_requests',
                'success': False,
                'result': f'exception'
            })
            return None, "search_requests_exception"
        """ESTRATEGIA 4: Usa requests + BeautifulSoup para acceder directo a la URL.
        
        Sin Selenium, sin búsqueda. Simplemente genera el slug e intenta acceder.
        Retorna (datos, estrategia_usada).
        """
        try:
            # Delay inteligente para evitar rate limiting
            # Informa bloquea después de ~5-10 requests rápidos, así que usamos delays variables
            time_since_last = time.time() - self.last_request_time
            if time_since_last < 5:
                delay = 5 - time_since_last + (2 if time_since_last < 2 else 1 if time_since_last < 3.5 else 0)
                logger.info(f"   [Informa-Direct] ⏳ Esperando {delay:.1f}s para evitar rate limit (429)...")
                time.sleep(delay)
            self.last_request_time = time.time()
            
            slug = self._name_to_slug(name)
            if not slug:
                logger.info(f"   [Informa-Direct] No se pudo generar slug para: {name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'slug_generation_failed'
                })
                return None, "direct_url_failed"

            url = f"https://www.informacolombia.com/directorio-empresas/informacion-empresa/{slug}"
            logger.info(f"   [Informa-Direct] GET {url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-CO,es;q=0.9',
                'Referer': 'https://www.informacolombia.com/',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 429:
                logger.warning(f"   [Informa-Direct] ⚠️ Rate limit (429) - Informa nos está bloqueando")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'rate_limit_429'
                })
                return None, "direct_url_rate_limit"
            
            if response.status_code == 410:
                logger.warning(f"   [Informa-Direct] Empresa no existe en Informa (410)")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'not_found_410'
                })
                return None, "direct_url_not_found"
            
            if response.status_code != 200:
                logger.warning(f"   [Informa-Direct] Status {response.status_code} para {name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': f'http_error_{response.status_code}'
                })
                return None, f"direct_url_http_error_{response.status_code}"

            page_text = response.text
            soup = BeautifulSoup(page_text, 'html.parser')

            # Detectar si es página genérica
            if self._is_generic_informa_page(response.text, name):
                logger.warning(f"   [Informa-Direct] Página genérica detectada para {name}")
                self.strategy_log.append({
                    'company': name,
                    'strategy': 'direct_url',
                    'success': False,
                    'result': 'direct_url_generic_page'
                })
                return None, "direct_url_generic_page"

            # Extraer datos usando métodos existentes
            table_fields = self._extract_table_fields(soup)
            informa_address = self._extract_address_from_informa_html(page_text)
            if informa_address and not table_fields.get('address'):
                table_fields['address'] = informa_address

            data = {
                'nit': table_fields.get('nit') or self._extract_text(page_text, r'\bNIT\b\s*(\d{8,15})'),
                'phone': table_fields.get('phone') or self._extract_text(page_text, r'\bTel[eé]fono\b\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{6,20})'),
                'address': table_fields.get('address') or self._extract_text(page_text, r'\bDirecci[oó]n\s+Actual\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{8,220}?)(?:\s+(?:Cómo llegar|Ver Mapa|NIT|Actividad|Forma Jurídica|Ranking)|$)'),
                'website': self._extract_website(soup),
                'activity': table_fields.get('activity') or self._extract_text(page_text, r'\bActividad\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Forma Jurídica|Ranking|NIT)|$)'),
                'legal_status': table_fields.get('legal_status') or self._extract_text(page_text, r'\bForma\s+Jur[ií]dica\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Ranking|NIT)|$)'),
                'city_info': table_fields.get('city_info') or self._extract_text(page_text, r'\bCiudad\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'department': table_fields.get('department') or self._extract_text(page_text, r'\bDepartamento\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'source': 'informacolombia'
            }

            # Limpieza final
            for key, value in list(data.items()):
                if isinstance(value, str):
                    value = value.strip().strip(':-')
                    if not value or 'DISPONIBLE' in value.upper() or value.lower() in {'ver mapa', 'cómo llegar', 'obtenerlo ahora >>'}:
                        data[key] = None
                    else:
                        data[key] = value

            logger.info(f"   [Informa-Direct] ✓ Datos extraídos para {name}")
            self.strategy_log.append({
                'company': name,
                'strategy': 'direct_url',
                'success': True,
                'result': 'direct_url_success'
            })
            return data, "direct_url_success"

        except Exception as e:
            logger.error(f"   [Informa-Direct] Error: {e}")
            self.strategy_log.append({
                'company': name,
                'strategy': 'direct_url',
                'success': False,
                'result': f'direct_url_exception'
            })
            return None, "direct_url_exception"

    def _get_browser(self, headless: bool = True):
        """Obtiene un navegador headless para interactuar con el directorio."""
        try:
            # Primero probar Chrome/Chromium, que suele comportarse mejor con sitios dinámicos.
            try:
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                return webdriver.Chrome(options=options)
            except Exception:
                pass

            # Fallback a Edge.
            try:
                options = EdgeOptions()
                if headless:
                    options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                return webdriver.Edge(options=options)
            except Exception:
                pass

            # Último fallback: Firefox.
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            return webdriver.Firefox(options=options)
        except Exception:
            return None

    def scrape_company(self, name: str, city: str = "", nit: str = "", headless: bool = True) -> Optional[Dict[str, Any]]:
        """Busca una empresa en Informa con múltiples estrategias.

        Intenta primero:
        1. Estrategia 4: URL directa (patrón slug)
        2. Estrategia 2: requests + BeautifulSoup
        3. Estrategia 1 (heredada): Búsqueda + Selenium (más lento, puede trigger CAPTCHA)
        
        Registra qué estrategia funcionó para análisis posterior.
        """
        try:
            search_name = re.sub(r'\s+', ' ', (name or '')).strip()
            if not search_name:
                logger.info("   [Informa] Nombre no disponible")
                return None

            logger.info(f"   [Informa] Procesando empresa: {search_name}")

            # ========== ESTRATEGIA 4: URL DIRECTA (Sin búsqueda, sin Selenium) ==========
            data, strategy_used = self.scrape_by_direct_url(search_name, city, nit)
            if data:
                self.last_used_strategy = "direct_url (sin búsqueda, sin Selenium)"
                self.strategy_log.append({
                    'company': search_name,
                    'strategy': 'direct_url',
                    'success': True,
                    'result': strategy_used
                })
                logger.info(f"   [Informa] ✓ ESTRATEGIA 4 (URL directa) funcionó para {search_name}")
                return data

            logger.info(f"   [Informa] Estrategia 4 falló ({strategy_used}), intentando Estrategia 2...")

            # ========== ESTRATEGIA 2: BÚSQUEDA CON REQUESTS + BeautifulSoup ==========
            data, strategy_used = self.scrape_by_search_requests(search_name, city, nit)
            if data:
                self.last_used_strategy = "search_requests (búsqueda HTTP sin Selenium)"
                self.strategy_log.append({
                    'company': search_name,
                    'strategy': 'search_requests',
                    'success': True,
                    'result': strategy_used
                })
                logger.info(f"   [Informa] ✓ ESTRATEGIA 2 (búsqueda requests) funcionó para {search_name}")
                return data

            logger.info(f"   [Informa] Estrategia 2 falló ({strategy_used}), intentando Estrategia 1 (Selenium)...")

            # ========== ESTRATEGIA 1 (HEREDADA): Búsqueda + Selenium ==========
            if not self.driver:
                self.driver = self._get_browser(headless=headless)
                if not self.driver:
                    logger.warning("   [Informa] No se pudo iniciar navegador")
                    self.strategy_log.append({
                        'company': search_name,
                        'strategy': 'selenium_search',
                        'success': False,
                        'result': 'browser_failed'
                    })
                    return None

            self.driver.set_page_load_timeout(20)
            self.driver.get(self.BASE_URL)
            time.sleep(2)

            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Buscar empresa']"))
            )
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                search_input,
                search_name,
            )

            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Buscar')]") )
            )
            search_button.click()

            WebDriverWait(self.driver, 15).until(
                lambda driver: '/servlet/app/portal/EMP/prod/LISTADO_EMPRESAS/' in driver.current_url or 'Listado de empresas encontradas' in driver.title
            )
            time.sleep(3)  # Delay más largo para evitar CAPTCHA

            # En la lista de resultados, tomar el primer enlace a información de empresa.
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            company_link = None
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                if '/directorio-empresas/informacion-empresa/' in href:
                    company_link = href if href.startswith('http') else self._absolute_url(href)
                    break

            if not company_link:
                logger.warning(f"   [Informa] No se encontró perfil para: {search_name}")
                self.strategy_log.append({
                    'company': search_name,
                    'strategy': 'selenium_search',
                    'success': False,
                    'result': 'no_link_found'
                })
                return None

            logger.info(f"   [Informa] Accediendo a perfil: {company_link}")
            self.driver.get(company_link)
            time.sleep(3)  # Delay más largo después de acceder al perfil

            profile_html = self.driver.execute_script("return document.body.innerHTML || ''")
            page_text = self.driver.execute_script("return document.body.innerText || ''") or ''

            # Detectar CAPTCHA o página genérica
            if self._is_generic_informa_page(page_text, search_name):
                logger.warning("   [Informa] Página genérica/bloqueada/CAPTCHA detectada; se ignora extracción")
                self.strategy_log.append({
                    'company': search_name,
                    'strategy': 'selenium_search',
                    'success': False,
                    'result': 'generic_page_or_captcha'
                })
                return None

            profile_soup = BeautifulSoup(profile_html, 'html.parser')
            table_fields = self._extract_table_fields(profile_soup)

            # Extraer dirección específica desde el HTML de Informa
            informa_address = self._extract_address_from_informa_html(profile_html)
            if informa_address and not table_fields.get('address'):
                table_fields['address'] = informa_address

            data = {
                'nit': table_fields.get('nit') or self._extract_text(page_text, r'\bNIT\b\s*(\d{8,15})'),
                'phone': table_fields.get('phone') or self._extract_text(page_text, r'\bTel[eé]fono\b\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{6,20})'),
                'address': table_fields.get('address') or self._extract_text(page_text, r'\bDirecci[oó]n\s+Actual\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{8,220}?)(?:\s+(?:Cómo llegar|Ver Mapa|NIT|Actividad|Forma Jurídica|Ranking)|$)'),
                'website': self._extract_website(profile_soup),
                'activity': table_fields.get('activity') or self._extract_text(page_text, r'\bActividad\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Forma Jurídica|Ranking|NIT)|$)'),
                'legal_status': table_fields.get('legal_status') or self._extract_text(page_text, r'\bForma\s+Jur[ií]dica\b\s*([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{3,120}?)(?:\s+(?:Ranking|NIT)|$)'),
                'city_info': table_fields.get('city_info') or self._extract_text(page_text, r'\bCiudad\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'department': table_fields.get('department') or self._extract_text(page_text, r'\bDepartamento\b\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})'),
                'source': 'informacolombia'
            }

            # Limpieza final
            for key, value in list(data.items()):
                if isinstance(value, str):
                    value = value.strip().strip(':-')
                    if not value or 'DISPONIBLE' in value.upper() or value.lower() in {'ver mapa', 'cómo llegar', 'obtenerlo ahora >>'}:
                        data[key] = None
                    else:
                        data[key] = value

            self.strategy_log.append({
                'company': search_name,
                'strategy': 'selenium_search',
                'success': True,
                'result': 'success'
            })
            self.last_used_strategy = "selenium_search (búsqueda + perfil)"
            logger.info(f"   [Informa] ✓ ESTRATEGIA 1 (Selenium) funcionó para {search_name}")
            return data

        except Exception as e:
            logger.error(f"   [Informa] Error: {e}")
            self.strategy_log.append({
                'company': search_name,
                'strategy': 'unknown',
                'success': False,
                'result': f'exception: {str(e)}'
            })
            return None

    def _is_generic_informa_page(self, page_text: str, search_name: str) -> bool:
        """Detecta páginas genéricas/corporativas de Informa que no son la ficha real de empresa."""
        text = (page_text or '').lower()
        if not text:
            return True

        generic_signals = [
            'informa colombia s.a.',
            'clientes@informacolombia.com',
            'tip: du',
            'política de tratamiento de datos',
        ]

        has_generic = sum(1 for s in generic_signals if s in text) >= 2
        has_company_fields = any(x in text for x in ['nit', 'dirección actual', 'direccion actual', 'forma jurídica', 'forma juridica'])

        # Verificar que el nombre buscado esté presente de forma razonable
        tokens = [t for t in re.sub(r'[^a-zA-Z0-9\s]', ' ', search_name.lower()).split() if len(t) > 3]
        token_hits = sum(1 for t in tokens[:4] if t in text)

        return has_generic and (not has_company_fields or token_hits < 2)

    def _absolute_url(self, href: str) -> str:
        if href.startswith('http'):
            return href
        return f"https://www.informacolombia.com{href}"

    def _extract_text(self, text: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip()

    def _extract_table_fields(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """Extrae campos de las tablas del perfil público de Informa."""
        fields = {'nit': None, 'phone': None, 'address': None, 'activity': None, 'legal_status': None, 'city_info': None, 'department': None}

        for row in soup.find_all('tr'):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(['th', 'td'])]
            if len(cells) < 2:
                continue

            label = cells[0].lower()
            value = cells[1].strip()
            if not value:
                continue

            if 'tel' in label and not fields['phone']:
                fields['phone'] = value
            elif 'direcci' in label and not fields['address']:
                fields['address'] = re.sub(r'\s+(?:Cómo llegar|Ver Mapa).*$','', value, flags=re.IGNORECASE).strip()
            elif label == 'nit' and not fields['nit']:
                fields['nit'] = value
            elif 'actividad' in label and not fields['activity']:
                fields['activity'] = value
            elif 'forma jur' in label and not fields['legal_status']:
                fields['legal_status'] = value
            elif 'ciudad' in label and not fields['city_info']:
                fields['city_info'] = value
            elif 'departamento' in label and not fields['department']:
                fields['department'] = value

        return fields

    def _extract_address_from_informa_html(self, page_html: str) -> Optional[str]:
        """Extrae la dirección desde el HTML específico de Informa.

        Busca primero en llamadas JS `showMapEmp(...)` donde el segundo argumento
        suele contener la dirección completa. Luego busca frases tipo
        'la dirección, <DIRECCION> en la ciudad de'.
        """
        if not page_html:
            return None

        decoded_html = html_lib.unescape(page_html)

        # 1) showMapEmp('es', 'ADDRESS, CITY, ...', ...)
        m = re.search(r"showMapEmp\(\s*['\"][^'\"]*['\"]\s*,\s*['\"]([^'\"]{6,250})['\"]", decoded_html)
        if m:
            addr = m.group(1).strip()
            # Limpiar comillas y etiquetas
            addr = re.sub(r'<[^>]+>', '', addr)
            addr = re.sub(r'\s+', ' ', addr).strip(', .')
            if len(addr) > 6:
                return addr

        # 2) Texto en párrafo: 'la dirección, <ADDRESS> en la ciudad de'
        m2 = re.search(r"la\s+direcci[oó]n[,\s]+([A-Z0-9ÁÉÍÓÚÑa-záéíóúñ#\-\.\s]{8,250}?)\s+en\s+la\s+ciudad", decoded_html, re.IGNORECASE)
        if m2:
            addr = m2.group(1).strip()
            addr = re.sub(r'<[^>]+>', '', addr)
            addr = re.sub(r'\s+', ' ', addr).strip(', .')
            if len(addr) > 6:
                return addr

        return None

    def _extract_website(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae un sitio externo si el perfil muestra un enlace público real."""
        blocked = ['informacolombia', 'facebook', 'twitter', 'linkedin', 'instagram', 'youtube', 'maps.google', 'google.es/maps']
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if href.startswith('http') and not any(x in href.lower() for x in blocked):
                text = a.get_text(strip=True).lower()
                if text and not text.startswith('ver'):
                    return href
        return None

    def get_strategy_report(self) -> Dict[str, Any]:
        """Retorna un reporte de qué estrategias funcionaron para cada empresa."""
        direct_url_success = sum(1 for log in self.strategy_log if log.get('strategy') == 'direct_url' and log.get('success'))
        selenium_success = sum(1 for log in self.strategy_log if log.get('strategy') == 'selenium_search' and log.get('success'))
        
        return {
            'total_companies': len(self.strategy_log),
            'direct_url_success': direct_url_success,
            'selenium_success': selenium_success,
            'success_rate_direct_url': f"{direct_url_success}/{len([l for l in self.strategy_log if l.get('strategy') == 'direct_url'])}",
            'success_rate_selenium': f"{selenium_success}/{len([l for l in self.strategy_log if l.get('strategy') == 'selenium_search'])}",
            'detailed_log': self.strategy_log
        }
