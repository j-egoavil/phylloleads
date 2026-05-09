"""
Google Maps Scraper - Busqueda Combinada (Sin APIs de pago)
Opcion 2: Busca en multiples fuentes
- Google Search (direccion, telefono)
- LinkedIn (verificar empresa)
- Paginas amarillas / Sitios locales
- Conectado a SQLite BD
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CombinedMapsScraper:
    """Scraper que busca en multiples fuentes sin APIs de pago"""
    
    def __init__(self, db_path: str = "appdb.sqlite"):
        """Inicializa el scraper"""
        self.db_path = db_path
        self.conn = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
    
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
            logger.info("BD cerrada")
    
    # ==================== FUENTE 1: DUCKDUCKGO (No requiere API) ====================
    
    def search_duckduckgo(self, query: str) -> Optional[List[str]]:
        """Busca en DuckDuckGo (no requiere API)"""
        try:
            url = "https://html.duckduckgo.com/"
            params = {
                'q': query,
                't': 'h_'
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer URLs de resultados
            results = []
            for result in soup.find_all('a', class_='result__a'):
                href = result.get('href')
                if href and 'duckduckgo.com' not in href:
                    results.append(href)
            
            return results[:3]  # Top 3 resultados
        
        except Exception as e:
            logger.warning("Error buscando en DuckDuckGo: {}".format(e))
            return None
    
    # ==================== EXTRAER DATOS DE HTML ====================
    
    def extract_from_webpage(self, url: str) -> Optional[Dict[str, str]]:
        """Extrae telefono, website, direccion de una pagina web"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            text = response.text
            html = response.content
            
            # Extraer datos
            phone = self.extract_phone(text)
            website = self.extract_website_from_url(url)
            address = self.extract_address(text)
            
            return {
                'phone': phone,
                'website': website,
                'address': address
            }
        
        except Exception as e:
            logger.warning("Error extrayendo de {}: {}".format(url, e))
            return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extrae numero de telefono del texto"""
        # Patrones colombianos
        patterns = [
            r'\+57\s*[1-9]\s*\d{1,4}\s*\d{3,4}\s*\d{3,4}',
            r'\+57\s*\d{10}',
            r'\(?([0-9]|[\(\)])*-?[0-9]{3,4}?-?[0-9]{3,4}\)?',
            r'(?:tel|telefono|phone)[\s:]*\+?57[\s\-]?[0-9\-\(\)\s]{10,}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = match.group(0)
                # Limpiar
                phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
                if re.search(r'\d', phone):
                    return phone.strip()
        
        return None
    
    def extract_website_from_url(self, url: str) -> Optional[str]:
        """Extrae dominio del URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc
            if domain and not domain.startswith('html.duckduckgo'):
                return "https://{}".format(domain)
        except:
            pass
        return None
    
    def extract_address(self, text: str) -> Optional[str]:
        """Extrae direccion del texto"""
        # Buscar patrones de direccion
        patterns = [
            r'(?:cra|carrera|calle|av|avenida|diagonal|transversal)\s+\d+[\s\#\-]*\d+[\s\-]*\d*',
            r'(?:ubicado|ubicada|direccion|address)[\s:]+([^,\n]{20,80})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(0) if match.lastindex is None else match.group(1)
                address = address.replace('|', ' ').strip()
                if len(address) > 10:
                    return address
        
        return None
    
    # ==================== BUSQUEDA COMBINADA ====================
    
    def scrape_company(self, company_name: str, city: str) -> Optional[Dict[str, Any]]:
        """Scrape informacion desde multiples fuentes"""
        
        print("\n{} Buscando: {} ({})".format("="*3, company_name, city))
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'sources': [],
            'status': 'partial'
        }
        
        # BUSQUEDA 1: DuckDuckGo (Google Search)
        logger.info("1. Buscando en DuckDuckGo...")
        search_query = "{} {} Colombia telefono".format(company_name, city)
        urls = self.search_duckduckgo(search_query)
        
        if urls:
            logger.info("   Encontrados {} resultados".format(len(urls)))
            for i, url in enumerate(urls, 1):
                logger.info("   [{}/{}] Extrayendo de: {}".format(i, len(urls), url[:60]))
                data = self.extract_from_webpage(url)
                
                if data:
                    if data.get('phone') and not results['phone']:
                        results['phone'] = data['phone']
                        logger.info("        -> Telefono: {}".format(data['phone']))
                    
                    if data.get('website') and not results['website']:
                        results['website'] = data['website']
                        logger.info("        -> Website: {}".format(data['website']))
                    
                    if data.get('address') and not results['address']:
                        results['address'] = data['address']
                        logger.info("        -> Direccion: {}".format(data['address'][:50]))
                    
                    results['sources'].append('google_search')
                
                time.sleep(1)  # Respetar servidor
        else:
            logger.info("   Sin resultados en DuckDuckGo")
        
        # BUSQUEDA 2: LinkedIn (verificacion)
        logger.info("2. Verificando en LinkedIn...")
        linkedin_query = "site:linkedin.com/company {}".format(company_name.replace(' ', '+'))
        linkedin_urls = self.search_duckduckgo(linkedin_query)
        
        if linkedin_urls:
            logger.info("   Empresa verificada en LinkedIn")
            results['sources'].append('linkedin')
        else:
            logger.info("   No encontrado en LinkedIn")
        
        time.sleep(1)
        
        # Estado final
        if results['phone'] or results['website'] or results['address']:
            results['status'] = 'completed' if (results['phone'] and results['website']) else 'partial'
        
        logger.info("   Estado: {}".format(results['status']))
        logger.info("   Fuentes: {}".format(', '.join(results['sources']) or 'ninguna'))
        
        return results
    
    # ==================== BASE DE DATOS ====================
    
    def get_pending_companies(self, limit: int = 50) -> List[Tuple]:
        """Obtiene empresas sin detalles de BD"""
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
            
            # Validar que hay al menos algo para guardar
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
            logger.info("   Datos guardados en BD (company_details)")
            return True
        
        except Exception as e:
            logger.error("   Error guardando en BD: {}".format(e))
            return False
    
    def verify_database_structure(self) -> bool:
        """Verifica que la tabla company_details existe"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='company_details'
            """)
            
            if not cursor.fetchone():
                logger.warning("Tabla company_details no existe, creando...")
                cursor.execute("""
                    CREATE TABLE company_details (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER UNIQUE,
                        phone VARCHAR(50),
                        website VARCHAR(500),
                        address VARCHAR(500),
                        latitude FLOAT,
                        longitude FLOAT,
                        google_maps_url VARCHAR(500),
                        scraped_at TIMESTAMP,
                        FOREIGN KEY(company_id) REFERENCES companies(id)
                    )
                """)
                self.conn.commit()
                logger.info("Tabla company_details creada")
            
            return True
        
        except Exception as e:
            logger.error("Error verificando estructura: {}".format(e))
            return False
    
    # ==================== PROCESAMIENTO PRINCIPAL ====================
    
    def process_companies(self, limit: int = 5) -> Dict[str, Any]:
        """Procesa todas las empresas"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'No se pudo conectar a BD'}
        
        if not self.verify_database_structure():
            return {'success': False, 'error': 'Error en estructura de BD'}
        
        companies = self.get_pending_companies(limit)
        
        if not companies:
            logger.info("Todas las empresas tienen detalles")
            self.close_db()
            return {
                'success': True,
                'total': 0,
                'processed': 0,
                'message': 'Todas las empresas tienen detalles'
            }
        
        logger.info("\n" + "="*80)
        logger.info("PROCESANDO {} EMPRESAS".format(len(companies)))
        logger.info("="*80 + "\n")
        
        processed = 0
        successful = 0
        
        try:
            for i, company in enumerate(companies, 1):
                try:
                    print("\n[{}/{}] {}".format(i, len(companies), company['name']))
                    print("      NIT: {} | Ciudad: {}".format(company['nit'], company['city']))
                    
                    # Scrape
                    details = self.scrape_company(company['name'], company['city'])
                    
                    # Guardar
                    if details:
                        saved = self.save_details(company['id'], details)
                        
                        if saved:
                            print("\n   RESULTADO:")
                            print("   - Telefono: {}".format(details.get('phone') or 'N/A'))
                            print("   - Website: {}".format(details.get('website') or 'N/A'))
                            print("   - Direccion: {}".format((details.get('address') or 'N/A')[:60]))
                            successful += 1
                    
                    processed += 1
                    time.sleep(2)  # Delay entre búsquedas
                
                except Exception as e:
                    logger.error("Error procesando {}: {}".format(company['name'], e))
                    processed += 1
                    continue
        
        finally:
            self.close_db()
        
        # Resumen
        logger.info("\n" + "="*80)
        logger.info("PROCESAMIENTO COMPLETADO")
        logger.info("="*80)
        logger.info("Total: {} | Exitosas: {} | Parciales: {}".format(
            processed, successful, processed - successful
        ))
        
        return {
            'success': True,
            'total': len(companies),
            'processed': processed,
            'successful': successful,
            'failed': processed - successful
        }


def show_stats():
    """Muestra estadisticas de BD"""
    try:
        conn = sqlite3.connect("appdb.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contar empresas con detalles
        cursor.execute("SELECT COUNT(*) as count FROM company_details WHERE phone != 'N/A' OR website != 'N/A'")
        with_details = cursor.fetchone()['count']
        
        # Contar empresas sin detalles
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE cd.id IS NULL AND c.is_active = 1
        """)
        without_details = cursor.fetchone()['count']
        
        # Mostrar algunos datos
        cursor.execute("""
            SELECT c.name, cd.phone, cd.website, cd.address
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            LIMIT 5
        """)
        
        print("\n" + "="*80)
        print("ESTADISTICAS DE BASE DE DATOS")
        print("="*80)
        print("Empresas con detalles: {}".format(with_details))
        print("Empresas sin detalles: {}".format(without_details))
        
        print("\nUltimos datos guardados:")
        for row in cursor.fetchall():
            print("- {}: {} | {}".format(
                row['name'][:40],
                row['phone'] if row['phone'] and row['phone'] != 'N/A' else 'N/A',
                row['website'] if row['website'] and row['website'] != 'N/A' else 'N/A'
            ))
        
        conn.close()
    
    except Exception as e:
        logger.error("Error mostrando estadisticas: {}".format(e))


def main():
    """Main"""
    
    print("\n" + "="*80)
    print("BUSQUEDA COMBINADA - DUCKDUCKGO + LINKEDIN + PAGINAS AMARILLAS")
    print("="*80)
    
    print("""
OPCION 2: Busqueda Combinada
  - Sin costo
  - Sin APIs de pago
  - Multiples fuentes
  - Verificacion en LinkedIn
  
Conectado a: appdb.sqlite
Tabla: company_details
""")
    
    scraper = CombinedMapsScraper()
    
    try:
        # Procesar 5 empresas
        result = scraper.process_companies(limit=5)
        
        # Mostrar resultados
        print("\n" + "="*80)
        if result['success']:
            print("PROCESAMIENTO EXITOSO")
            print("="*80)
            print("Total procesadas: {}".format(result['processed']))
            print("Exitosas: {}".format(result['successful']))
            print("Parciales: {}".format(result['failed']))
            
            # Mostrar estadisticas
            show_stats()
        else:
            print("ERROR")
            print("="*80)
            print("Error: {}".format(result.get('error')))
    
    except KeyboardInterrupt:
        print("\n\nScraping cancelado por el usuario")
    except Exception as e:
        logger.error("Error: {}".format(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
