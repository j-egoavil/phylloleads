import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import psycopg2
from psycopg2.extras import execute_values
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmpresasLaRepublicaScraper:
    """
    Scraper para empresas.larepublica.co
    Busca empresas por nicho y extrae información: nombre, RUES, ciudad, tamaño
    """
    
    BASE_URL = "https://empresas.larepublica.co"
    SEARCH_URL = f"{BASE_URL}/search"
    
    def __init__(
        self,
        db_host: str = "localhost",
        db_port: int = 5432,
        db_name: str = "appdb",
        db_user: str = "postgres",
        db_password: str = "postgres",
        headless: bool = True
    ):
        """
        Inicializa el scraper con parámetros de conexión a base de datos
        
        Args:
            db_host: Host de PostgreSQL
            db_port: Puerto de PostgreSQL
            db_name: Nombre de la base de datos
            db_user: Usuario de PostgreSQL
            db_password: Contraseña de PostgreSQL
            headless: Si True, Selenium corre sin interfaz gráfica
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _init_driver(self):
        """Inicializa el driver de Selenium (Firefox primero para Docker, luego Chrome/Edge)"""
        # Intentar Firefox primero (disponible en Docker)
        try:
            firefox_options = FirefoxOptions()
            if self.headless:
                firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Firefox(options=firefox_options)
            logger.info("Driver de Firefox inicializado")
            return
        except Exception as e:
            logger.debug(f"Firefox no disponible: {e}")
        
        # Intentar Chrome (local)
        try:
            chrome_options = ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Driver de Chrome inicializado")
            return
        except Exception as e:
            logger.debug(f"Chrome no disponible: {e}")
        
        # Intentar Edge (local)
        try:
            edge_options = EdgeOptions()
            if self.headless:
                edge_options.add_argument("--headless")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Edge(options=edge_options)
            logger.info("Driver de Edge inicializado")
            return
        except Exception as e:
            logger.error(f"No se pudo inicializar ningún navegador: {e}")
            raise Exception("No hay navegador disponible (Firefox, Chrome o Edge)")
    
    
    def _close_driver(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver cerrado")
    
    def search_niche(self, niche: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        Busca empresas por nicho y extrae los links de resultados
        
        Args:
            niche: Término de búsqueda (ej: "veterinarias", "restaurantes")
            pages: Número de páginas a scrapear
            
        Returns:
            Lista de diccionarios con información de empresas
        """
        if not self.driver:
            self._init_driver()
        
        all_companies = []
        
        try:
            for page in range(1, pages + 1):
                logger.info(f"Scrapeando página {page} para nicho: {niche}")
                
                # Construir URL con búsqueda
                url = f"{self.BASE_URL}?q={niche}&page={page}"
                
                # Cargar página
                self.driver.get(url)
                
                # Esperar a que carguen los resultados
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "result-item"))
                    )
                except:
                    logger.warning(f"No se encontraron resultados en página {page}")
                    break
                
                # Dar tiempo adicional para scroll y carga
                time.sleep(2)
                
                # Parsear HTML
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Extraer links de empresas con clase "result-item"
                result_items = soup.find_all('a', class_='result-item')
                logger.info(f"Encontradas {len(result_items)} empresas en página {page}")
                
                for item in result_items:
                    try:
                        company_data = self._parse_company_item(item)
                        if company_data:
                            all_companies.append(company_data)
                    except Exception as e:
                        logger.error(f"Error parseando empresa: {e}")
                        continue
                
                # Respetar el servidor
                time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
        finally:
            self._close_driver()
        
        logger.info(f"Total de empresas extraídas: {len(all_companies)}")
        return all_companies
    
    def _parse_company_item(self, item) -> Optional[Dict[str, Any]]:
        """
        Parsea un elemento de resultado de empresa
        
        Args:
            item: Elemento BeautifulSoup del resultado
            
        Returns:
            Dict con datos de la empresa o None si hay error
        """
        try:
            # Extraer nombre
            name_tag = item.find('h3', class_='company-name')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            
            # Extraer href para obtener el link
            href = item.get('href', '')
            full_url = f"{self.BASE_URL}{href}" if href.startswith('/') else href
            
            # Extraer NIT del href (última parte del URL)
            # Formato típico: /colombia/bolivar/cartagena/nombre-empresa-nit
            nit = self._extract_nit_from_url(href)
            
            # Extraer información adicional (puede estar en span o divs dentro del item)
            # La estructura puede variar, así que intentamos extraer múltiples campos
            
            # Información de RUES (número de identificación)
            rues_text = ""
            for span in item.find_all('span'):
                text = span.get_text(strip=True)
                if any(char.isdigit() for char in text) and len(text) > 5:
                    # Probable número de RUES/RUT
                    rues_text = text
                    break
            
            # Extraer ciudad/región del href o de otros campos
            # El href generalmente tiene formato: /colombia/bolivar/cartagena/...
            city = self._extract_city_from_url(href)
            
            # Extraer información de activa/inactiva y tamaño
            # Esto usualmente está en el texto del item o en atributos
            status_text = item.get_text(strip=True)
            is_active = "inactiva" not in status_text.lower()
            
            company_data = {
                "name": name,
                "url": full_url,
                "nit": nit,
                "rues": rues_text,
                "city": city,
                "is_active": is_active,
                "status": "Activa" if is_active else "Inactiva",
                "company_size": self._estimate_company_size(status_text),
                "search_niche": "",  # Se asigna en search_niche()
                "scraped_at": datetime.now().isoformat(),
                "raw_html": str(item)
            }
            
            return company_data
        
        except Exception as e:
            logger.error(f"Error en _parse_company_item: {e}")
            return None
    
    def _extract_nit_from_url(self, url: str) -> str:
        """
        Extrae el NIT del URL
        Formato típico: /colombia/bolivar/cartagena/nombre-empresa-nit
        El NIT es la última parte después del último guion
        """
        try:
            # Obtener la última parte del URL
            last_part = url.split('/')[-1]
            # El NIT está al final después del último guion
            if '-' in last_part:
                nit = last_part.split('-')[-1]
                # Verificar que sea un número válido
                if nit.isdigit() and len(nit) >= 8:
                    return nit
            return "N/A"
        except:
            return "N/A"
    
    def _extract_city_from_url(self, url: str) -> str:
        """
        Extrae la ciudad del URL
        Formato típico: /colombia/bolivar/cartagena/nombre-empresa-nit
        """
        try:
            parts = url.split('/')
            # Formato esperado: ['', 'colombia', 'departamento', 'ciudad', 'nombre-nit']
            if len(parts) >= 4:
                return parts[3]  # Índice 3 es la ciudad
            return "N/A"
        except:
            return "N/A"
    
    def _estimate_company_size(self, text: str) -> str:
        """
        Intenta estimar el tamaño de la empresa basado en el texto
        Palabras clave: micro, pequeña, mediana, grande
        """
        text_lower = text.lower()
        
        if "grande" in text_lower or "corporación" in text_lower:
            return "Grande"
        elif "mediana" in text_lower or "empresa mediana" in text_lower:
            return "Mediana"
        elif "pequeña" in text_lower or "pyme" in text_lower:
            return "Pequeña"
        elif "micro" in text_lower or "autónomo" in text_lower:
            return "Micro"
        else:
            return "No especificado"
    
    def get_db_connection(self):
        """Obtiene conexión a PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            return conn
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            return None
    
    def create_tables(self):
        """Crea las tablas necesarias en la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            logger.error("No se pudo conectar a la base de datos")
            return False
        
        try:
            cur = conn.cursor()
            
            # Tabla de empresas scrapeadas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(500) NOT NULL,
                    url VARCHAR(1000),
                    rues VARCHAR(100),
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
        """
        Guarda las empresas en la base de datos
        
        Args:
            companies: Lista de diccionarios con datos de empresas
            niche: Nicho buscado
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        if not companies:
            logger.warning("No hay empresas para guardar")
            return False
        
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            
            # Preparar datos para insert
            values = []
            for company in companies:
                company["search_niche"] = niche
                values.append((
                    company.get("name"),
                    company.get("url"),
                    company.get("rues"),
                    company.get("city"),
                    company.get("is_active"),
                    company.get("status"),
                    company.get("company_size"),
                    company.get("search_niche"),
                    company.get("scraped_at")
                ))
            
            # Insert con ON CONFLICT para evitar duplicados
            query = """
                INSERT INTO companies 
                (name, url, rues, city, is_active, status, company_size, search_niche, scraped_at)
                VALUES %s
                ON CONFLICT (url) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    is_active = EXCLUDED.is_active,
                    status = EXCLUDED.status,
                    company_size = EXCLUDED.company_size,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """
            
            execute_values(cur, query, values)
            conn.commit()
            
            affected_rows = cur.rowcount
            cur.close()
            
            logger.info(f"Guardadas/actualizadas {affected_rows} empresas")
            return True
        
        except Exception as e:
            logger.error(f"Error guardando empresas: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_companies_by_niche(self, niche: str) -> List[Dict[str, Any]]:
        """
        Obtiene empresas guardadas por nicho
        
        Args:
            niche: Nicho a buscar
            
        Returns:
            Lista de diccionarios con datos de empresas
        """
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, url, rues, city, is_active, status, company_size, scraped_at
                FROM companies
                WHERE search_niche = %s
                ORDER BY scraped_at DESC
                LIMIT 1000;
            """, (niche,))
            
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
            cur.close()
            
            return results
        
        except Exception as e:
            logger.error(f"Error obteniendo empresas: {e}")
            return []
        
        finally:
            conn.close()
    
    def scrape_and_save(self, niche: str, pages: int = 1) -> Dict[str, Any]:
        """
        Pipeline completo: scrape, parse y guarda en base de datos
        
        Args:
            niche: Término de búsqueda
            pages: Número de páginas a scrapear
            
        Returns:
            Dict con resultado de la operación
        """
        logger.info(f"Iniciando scrape para nicho: {niche}")
        
        # Crear tablas si no existen
        self.create_tables()
        
        # Buscar empresas
        companies = self.search_niche(niche, pages)
        
        if not companies:
            logger.warning(f"No se encontraron empresas para {niche}")
            return {
                "success": False,
                "niche": niche,
                "total_companies": 0,
                "message": "No se encontraron resultados"
            }
        
        # Guardar en BD
        saved = self.save_companies(companies, niche)
        
        return {
            "success": saved,
            "niche": niche,
            "total_companies": len(companies),
            "companies": companies,
            "message": f"Scrape completado: {len(companies)} empresas"
        }


# Uso directo del script
if __name__ == "__main__":
    import sys
    
    # Configurar desde variables de entorno o argumentos
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "appdb")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    
    # Crear scraper
    scraper = EmpresasLaRepublicaScraper(
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        headless=True
    )
    
    # Ejemplo de uso
    niche = sys.argv[1] if len(sys.argv) > 1 else "veterinarias"
    pages = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    result = scraper.scrape_and_save(niche, pages)
    print(f"\n✅ Resultado: {result}")
