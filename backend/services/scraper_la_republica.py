import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
try:
    import psycopg2
    from psycopg2.extras import execute_values
except Exception:
    psycopg2 = None
    execute_values = None
import sqlite3
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import gzip
import io
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmpresasLaRepublicaScraper:
    """
    Scraper para empresas.larepublica.co usando estrategia de sitemaps
    Descarga sitemaps, busca por palabras clave y extrae información de las páginas
    """
    
    BASE_URL = "https://empresas.larepublica.co"
    SITEMAP_INDEX = f"{BASE_URL}/sitemapindex"
    
    def __init__(
        self,
        db_host: str = "localhost",
        db_port: int = 5432,
        db_name: str = "appdb",
        db_user: str = "postgres",
        db_password: str = "postgres",
        headless: bool = True,
        max_sitemaps: int = 5
    ):
        """
        Inicializa el scraper con estrategia de sitemaps
        
        Args:
            db_host: Host de PostgreSQL
            db_port: Puerto de PostgreSQL
            db_name: Nombre de la base de datos
            db_user: Usuario de PostgreSQL
            db_password: Contraseña de PostgreSQL
            headless: Si True, Selenium corre sin interfaz gráfica
            max_sitemaps: Máximo número de sitemaps a descargar (desde el más reciente)
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.max_sitemaps = max_sitemaps
    
    def _init_driver(self):
        """Inicializa el driver de Selenium (Firefox para Docker)"""
        try:
            firefox_options = FirefoxOptions()
            if self.headless:
                firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Firefox(options=firefox_options)
            logger.info("Driver de Firefox inicializado")
            return
        except Exception as e:
            logger.error(f"No se pudo inicializar Firefox: {e}")
            raise Exception("No se pudo inicializar navegador para scraping")
    
    def _close_driver(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver cerrado")
            except:
                pass
    
    def _download_sitemapindex(self) -> Optional[List[str]]:
        """
        Descarga el índice de sitemaps de empresas.larepublica.co
        
        Returns:
            Lista de URLs de sitemaps o None si falla
        """
        try:
            logger.info(f"🔽 Descargando índice de sitemaps desde {self.SITEMAP_INDEX}")
            response = self.session.get(self.SITEMAP_INDEX, timeout=30)
            logger.info(f"✅ Respuesta HTTP {response.status_code} recibida")
            response.raise_for_status()
            
            logger.debug(f"Parseando XML (size: {len(response.content)} bytes)")
            root = ET.fromstring(response.content)
            
            # Namespace de sitemap
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Extraer todas las URLs de sitemaps
            sitemap_urls = []
            for sitemap in root.findall('sm:sitemap', ns):
                loc = sitemap.find('sm:loc', ns)
                if loc is not None and loc.text:
                    sitemap_urls.append(loc.text)
            
            logger.info(f"📋 Encontrados {len(sitemap_urls)} sitemaps en el índice")
            
            # Los sitemaps más recientes generalmente están al final
            # Invertimos para empezar con los más recientes
            sitemap_urls.reverse()
            
            selected_sitemaps = sitemap_urls[:self.max_sitemaps]
            logger.info(f"📌 Seleccionados primeros {len(selected_sitemaps)} sitemaps (desde los más recientes)")
            for sitemap_url in selected_sitemaps[:3]:
                logger.debug(f"  - {sitemap_url}")
            
            return selected_sitemaps
        
        except Exception as e:
            logger.error(f"❌ Error descargando sitemapindex: {e}", exc_info=True)
            return None
    
    def _download_and_decompress_sitemap(self, sitemap_url: str) -> Optional[List[str]]:
        """
        Descarga un sitemap .txt.gz y lo descomprime
        
        Args:
            sitemap_url: URL del sitemap (ej: https://empresas.larepublica.co/sitemaps/companies_12.txt.gz)
            
        Returns:
            Lista de URLs de empresas o None si falla
        """
        try:
            logger.info(f"📥 Descargando sitemap: {sitemap_url}")
            
            response = self.session.get(sitemap_url, timeout=60)
            logger.info(f"✅ Respuesta HTTP {response.status_code} recibida (size: {len(response.content)} bytes)")
            response.raise_for_status()
            
            # Descomprimir
            logger.info(f"🗜️  Descomprimiendo archivo .gz")
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
            logger.info(f"✅ Descompresión completada")
            
            # Parsear URLs (una por línea)
            urls = [line.strip() for line in content.split('\n') if line.strip()]
            logger.info(f"✅ Parseo completado: {len(urls)} URLs de empresas extraídas")
            
            return urls
        
        except Exception as e:
            logger.error(f"❌ Error descargando/descomprimiendo sitemap: {e}", exc_info=True)
            return None
    
    def _search_keywords_in_urls(self, urls: List[str], keywords: List[str]) -> List[str]:
        """
        Busca URLs que coincidan con las palabras clave
        
        Args:
            urls: Lista de URLs del sitemap
            keywords: Palabras clave a buscar
            
        Returns:
            Lista de URLs que contienen al menos una palabra clave
        """
        matching_urls = []
        keywords_lower = [k.lower().replace(" ", "-") for k in keywords]
        
        for url in urls:
            url_lower = url.lower()
            for keyword in keywords_lower:
                if keyword in url_lower:
                    matching_urls.append(url)
                    logger.debug(f"Coincidencia encontrada: {keyword} en {url}")
                    break
        
        logger.info(f"Encontradas {len(matching_urls)} URLs coincidentes")
        return matching_urls
    
    def _scrape_company_page(self, url: str, niche: str) -> Optional[Dict[str, Any]]:
        """
        Scrappea una página individual de empresa y extrae la información
        
        Args:
            url: URL de la empresa
            niche: Nicho buscado
            
        Returns:
            Dict con datos de la empresa o None si falla
        """
        try:
            logger.debug(f"Scrapeando página: {url}")
            
            # Usar la sesión de requests para evitar inicializar navegadores pesados
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parsear con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información de la página
            company_data = self._parse_company_page(soup, url, niche)
            
            return company_data
        
        except Exception as e:
            logger.error(f"Error scrapeando página {url}: {e}")
            return None
    
    def _parse_company_page(self, soup: BeautifulSoup, url: str, niche: str) -> Optional[Dict[str, Any]]:
        """
        Parsea el HTML de una página de empresa y extrae información
        
        Args:
            soup: Objeto BeautifulSoup con el HTML
            url: URL de la empresa
            niche: Nicho buscado
            
        Returns:
            Dict con datos extraídos o None si falla
        """
        try:
            # Extraer nombre (generalmente en h1 o meta)
            name = "N/A"
            h1_tag = soup.find('h1')
            if h1_tag:
                name = h1_tag.get_text(strip=True)
            else:
                title_tag = soup.find('title')
                if title_tag:
                    name = title_tag.get_text(strip=True).split('|')[0].strip()
            
            # Limpiar el nombre (quitar NIT o "Registro Único" si está presente)
            if '-' in name:
                name = name.split('-')[0].strip()
            if 'Registro' in name:
                name = name.split('Registro')[0].strip()
            
            # Extraer NIT del URL
            nit = self._extract_nit_from_url(url)
            
            # Si no se encontró en URL, buscar en el texto de la página
            if nit == "N/A":
                nit_match = re.search(r'NIT\s*[:\s]*(\d{8,15})', soup.get_text(), re.IGNORECASE)
                if nit_match:
                    nit = nit_match.group(1)
            
            # Extraer ciudad del URL
            city = self._extract_city_from_url(url)
            
            # Estado (activa/inactiva)
            page_text = soup.get_text().lower()
            is_active = "inactiva" not in page_text and "no verificada" not in page_text
            
            # Estimar tamaño de empresa
            company_size = self._estimate_company_size(page_text)
            
            company_data = {
                "name": name,
                "url": url,
                "nit": nit,
                "city": city,
                "is_active": is_active,
                "status": "Activa" if is_active else "Inactiva",
                "company_size": company_size,
                "search_niche": niche,
                "scraped_at": datetime.now().isoformat()
            }
            
            logger.info(f"Empresa extraída: {name} ({nit})")
            return company_data
        
        except Exception as e:
            logger.error(f"Error parseando página: {e}")
            return None
    
    def _extract_nit_from_url(self, url: str) -> str:
        """
        Extrae el NIT del URL
        Formato: https://empresas.larepublica.co/colombia/quindio/armenia/constructora-inmobiliaria-buenavista-s-a-s-901469729
        El NIT es la última parte numérica al final de la URL
        """
        try:
            # Obtener la última parte después del último /
            last_part = url.split('/')[-1]
            
            # Buscar números al final (el NIT)
            match = re.search(r'(\d{8,15})$', last_part)
            if match:
                nit = match.group(1)
                # Formato típico: XXXXXXXX o XXXXXXXXX (8-9 dígitos)
                if len(nit) >= 8:
                    return nit
            
            return "N/A"
        except:
            return "N/A"
    
    def _extract_city_from_url(self, url: str) -> str:
        """
        Extrae la ciudad del URL
        Formato: /colombia/departamento/ciudad/nombre-nit
        """
        try:
            # Extraer partes del path
            parts = url.split('/')
            # Formato: https://empresas... /colombia /quindio /armenia /nombre-nit
            # Índices:                    0         1        2        3         4
            if len(parts) >= 5:
                # Índice 3 es generalmente la ciudad
                city = parts[3]
                return city if city else "N/A"
            return "N/A"
        except:
            return "N/A"
    
    def _estimate_company_size(self, text: str) -> str:
        """
        Intenta estimar el tamaño de la empresa basado en el texto
        Palabras clave: micro, pequeña, mediana, grande
        """
        text_lower = text.lower()
        
        if "grande" in text_lower or "corporación" in text_lower or "empresa grande" in text_lower:
            return "Grande"
        elif "mediana" in text_lower or "empresa mediana" in text_lower:
            return "Mediana"
        elif "pequeña" in text_lower or "pyme" in text_lower or "empresa pequeña" in text_lower:
            return "Pequeña"
        elif "micro" in text_lower or "autónomo" in text_lower or "independiente" in text_lower:
            return "Micro"
        else:
            return "No especificado"
    
    def search_niche(self, niche: str, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Busca empresas por nicho usando sitemaps
        
        Args:
            niche: Nicho de búsqueda (ej: "restaurantes", "veterinarias")
            keywords: Palabras clave específicas (si no se proporcionan, se usa el nicho como palabra clave)
            
        Returns:
            Lista de diccionarios con información de empresas
        """
        if keywords is None:
            keywords = [niche]
        else:
            keywords = list(set(keywords + [niche]))  # Incluir el nicho como palabra clave
        
        all_companies = []
        
        try:
            logger.info(f"🔍 Iniciando búsqueda de nicho: {niche}")
            logger.info(f"🔑 Palabras clave: {keywords}")
            
            # 1. Descargar índice de sitemaps
            logger.info(f"📋 Paso 1/4: Obteniendo índice de sitemaps...")
            sitemap_urls = self._download_sitemapindex()
            if not sitemap_urls:
                logger.warning("⚠️ No se pudieron obtener sitemaps")
                return []
            
            logger.info(f"✅ Obtenidos {len(sitemap_urls)} sitemaps")
            
            # 2. Procesar cada sitemap
            logger.info(f"📥 Paso 2/4: Descargando {len(sitemap_urls)} sitemaps...")
            for idx, sitemap_url in enumerate(sitemap_urls, 1):
                logger.info(f"  [{idx}/{len(sitemap_urls)}] Procesando: {sitemap_url}")
                
                # Descargar y descomprimir
                company_urls = self._download_and_decompress_sitemap(sitemap_url)
                if not company_urls:
                    logger.warning(f"  ⚠️ No se pudo descargar este sitemap")
                    continue
                
                logger.info(f"  ✅ Obtenidas {len(company_urls)} URLs del sitemap")
                
                # 3. Buscar coincidencias con palabras clave
                logger.info(f"🔎 Paso 3/4: Filtrando por palabras clave...")
                matching_urls = self._search_keywords_in_urls(company_urls, keywords)
                logger.info(f"  ✅ Encontradas {len(matching_urls)} coincidencias")
                
                if not matching_urls:
                    logger.info(f"  ℹ️ No hay coincidencias en este sitemap")
                    continue
                
                # 4. Scrappear cada página
                logger.info(f"🌐 Paso 4/4: Scrapeando {len(matching_urls)} páginas...")
                for page_idx, company_url in enumerate(matching_urls, 1):
                    try:
                        if page_idx % 10 == 0:
                            logger.info(f"  [{page_idx}/{len(matching_urls)}] Scrapeado...")
                        
                        company_data = self._scrape_company_page(company_url, niche)
                        if company_data:
                            all_companies.append(company_data)
                            
                            # Dar tiempo al servidor
                            time.sleep(0.5)
                    
                    except Exception as e:
                        logger.debug(f"  Error scrapeando {company_url}: {e}")
                        continue
                
                logger.info(f"  ✅ Completado sitemap {idx}: {len(all_companies)} empresas acumuladas")
        
        except Exception as e:
            logger.error(f"❌ Error en búsqueda de nicho: {e}", exc_info=True)
        
        finally:
            self._close_driver()
        
        logger.info(f"✅ Búsqueda completada: {len(all_companies)} empresas encontradas para '{niche}'")
        return all_companies
    
    def get_db_connection(self):
        """Obtiene conexión a la base de datos.

        Intenta PostgreSQL si `psycopg2` está disponible, si no, usa SQLite
        y la variable de entorno `APP_DB_PATH`.
        """
        # Intentar PostgreSQL si psycopg2 está disponible
        if psycopg2 is not None:
            try:
                conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    database=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                )
                return conn
            except Exception as e:
                logger.warning(f"No se pudo conectar a PostgreSQL ({e}), usando SQLite...")

        # Fallback a SQLite
        try:
            db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            logger.error(f"Error conectando a SQLite: {e}")
            return None
    
    def create_tables(self):
        """Crea las tablas necesarias en la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            logger.error("No se pudo conectar a la base de datos")
            return False
        
        try:
            cur = conn.cursor()
            
            # Tabla de empresas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(500) NOT NULL,
                    url VARCHAR(1000),
                    nit VARCHAR(50),
                    city VARCHAR(200),
                    is_active BOOLEAN DEFAULT true,
                    status VARCHAR(50),
                    company_size VARCHAR(50),
                    search_niche VARCHAR(200),
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(url)
                );
            """)
            
            # Tabla de búsquedas realizadas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_logs (
                    id SERIAL PRIMARY KEY,
                    niche VARCHAR(200) NOT NULL,
                    total_companies INT,
                    pages_scraped INT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    status VARCHAR(50)
                );
            """)
            
            conn.commit()
            cur.close()
            logger.info("Tablas creadas/verificadas exitosamente")
            return True
        
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            return False
        
        finally:
            conn.close()
    
    def save_companies(self, companies: List[Dict[str, Any]], niche: str) -> bool:
        """Guarda empresas en la base de datos"""
        if not companies:
            logger.warning("No hay empresas para guardar")
            return False
        
        conn = self.get_db_connection()
        if not conn:
            return False

        if psycopg2 is not None and execute_values is not None:
            try:
                cur = conn.cursor()
                values = []
                for company in companies:
                    values.append((
                        company.get("name"),
                        company.get("url"),
                        company.get("nit"),
                        company.get("city"),
                        company.get("is_active"),
                        company.get("status"),
                        company.get("company_size"),
                        company.get("search_niche"),
                        company.get("scraped_at"),
                    ))

                query = """
                    INSERT INTO companies 
                    (name, url, nit, city, is_active, status, company_size, search_niche, scraped_at)
                    VALUES %s
                    ON CONFLICT (url) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                    RETURNING id;
                """

                execute_values(cur, query, values)
                conn.commit()
                affected_rows = cur.rowcount
                cur.close()
                logger.info(f"Guardadas {affected_rows} empresas (Postgres)")
                return True
            except Exception as e:
                logger.error(f"Error guardando en Postgres: {e}")
                return False

        # SQLite fallback
        try:
            cur = conn.cursor()
            for company in companies:
                try:
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO companies
                        (name, url, nit, city, is_active, status, company_size, search_niche, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            company.get("name"),
                            company.get("url"),
                            company.get("nit"),
                            company.get("city"),
                            int(bool(company.get("is_active"))),
                            company.get("status"),
                            company.get("company_size"),
                            company.get("search_niche"),
                            company.get("scraped_at"),
                        ),
                    )
                except Exception as e:
                    logger.warning(f"Error insertando {company.get('name')}: {e}")

            conn.commit()
            cur.close()
            logger.info(f"Guardadas {len(companies)} empresas (SQLite)")
            return True

        except Exception as e:
            logger.error(f"Error guardando en SQLite: {e}")
            return False
        
        finally:
            try:
                conn.close()
            except:
                pass
    
    def scrape_and_save(self, niche: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Pipeline completo: scrape, parse y guarda en base de datos"""
        logger.info(f"Iniciando scrape para nicho: {niche}")
        
        self.create_tables()
        companies = self.search_niche(niche, keywords)
        
        if not companies:
            return {
                "success": False,
                "niche": niche,
                "total_companies": 0,
                "message": "No se encontraron resultados"
            }
        
        saved = self.save_companies(companies, niche)
        
        return {
            "success": saved,
            "niche": niche,
            "total_companies": len(companies),
            "companies": companies,
            "message": f"Scrape completado: {len(companies)} empresas"
        }

    def search_by_niche(self, niche: str, target_count: int = 100) -> Dict[str, Any]:
        """
        Búsqueda simplificada para background task
        Wrapper de scrape_and_save con parámetros específicos
        
        Args:
            niche: Nicho de búsqueda (ej: "veterinarias")
            target_count: Número objetivo de empresas (sin usar, para compatibilidad)
            
        Returns:
            Dict con resultado del scrape
        """
        return self.scrape_and_save(niche, keywords=[niche])


if __name__ == "__main__":
    # Uso directo
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "appdb")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    
    scraper = EmpresasLaRepublicaScraper(
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        headless=True,
        max_sitemaps=5
    )
    
    # Ejemplo: buscar restaurantes
    result = scraper.scrape_and_save("restaurantes", keywords=["restaurante", "café", "comida"])
    print(f"Resultado: {result}")
