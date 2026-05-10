"""
Scraper Páginas Amarillas Colombia - Búsqueda automática de teléfonos
Extrae datos reales directamente de la fuente más confiable de Colombia
"""

import sqlite3
import logging
import time
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaginasAmarillasDirectScraper:
    """Scraper que busca directamente en Páginas Amarillas Colombia"""
    
    def __init__(self, db_path: str = "appdb.sqlite"):
        self.db_path = db_path
        self.conn = None
        self.session = requests.Session()
        
        # Headers realistas
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9',
            'Referer': 'https://www.paginasamarillas.com.co/',
        }
        self.session.headers.update(self.headers)
    
    def connect_db(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info("Conectado a BD")
            return True
        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False
    
    def close_db(self):
        if self.conn:
            self.conn.close()
    
    def search_paginas_amarillas(self, empresa_nombre: str, ciudad: str) -> Optional[Dict[str, str]]:
        """Busca en Páginas Amarillas Colombia"""
        try:
            logger.info(f"   [Páginas Amarillas] Buscando: {empresa_nombre} en {ciudad}")
            
            # URL de búsqueda en Páginas Amarillas
            search_url = "https://www.paginasamarillas.com.co/search"
            params = {
                'q': empresa_nombre,
                'location': ciudad
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = {
                'phone': None,
                'website': None,
                'address': None
            }
            
            # Buscar el primer resultado
            # Páginas Amarillas usa estructuras variables, intentar múltiples selectores
            business_result = (
                soup.find('div', class_='business-listing') or
                soup.find('div', class_='result-item') or
                soup.find('a', class_='business-card')
            )
            
            if business_result:
                # Extraer teléfono
                phone_link = business_result.find('a', href=re.compile(r'tel:'))
                if phone_link:
                    phone = phone_link.get('href', '').replace('tel:', '').strip()
                    if phone and re.search(r'\d{7,}', phone):
                        results['phone'] = phone
                        logger.info(f"        -> Teléfono: {phone}")
                
                # Extraer website
                for link in business_result.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('http') and 'paginasamarillas' not in href:
                        results['website'] = href
                        logger.info(f"        -> Website: {href}")
                        break
                
                # Extraer dirección
                address_elem = (
                    business_result.find('div', class_='address') or
                    business_result.find('span', class_='address')
                )
                if address_elem:
                    address = address_elem.get_text(strip=True)
                    if address and len(address) > 10:
                        results['address'] = address
                        logger.info(f"        -> Dirección: {address[:50]}")
            
            if any(results.values()):
                return results
            
            return None
        
        except Exception as e:
            logger.warning(f"   [Páginas Amarillas] Error: {str(e)[:80]}")
            return None
    
    def search_google_direct(self, empresa_nombre: str, ciudad: str) -> Optional[Dict[str, str]]:
        """Búsqueda directa en Google para encontrar teléfono"""
        try:
            logger.info(f"   [Google Search] Buscando: {empresa_nombre}")
            
            search_query = f"{empresa_nombre} {ciudad} Colombia telefono contacto"
            url = "https://www.google.com/search"
            params = {
                'q': search_query,
                'hl': 'es'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            text = response.text
            
            results = {
                'phone': None,
                'website': None,
                'address': None
            }
            
            # Patrones para extraer teléfono
            phone_patterns = [
                r'\+57\s*[1-9]\s*[\d\s\-\(\)]{7,}',
                r'\+57\s*\d{10}',
                r'Tel[.]*[\s:]*\+?57[\d\s\-\(\)]{10,}',
            ]
            
            for pattern in phone_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    phone = match.group(0)
                    # Validar
                    digits = re.sub(r'\D', '', phone)
                    if len(digits) >= 10:
                        results['phone'] = phone.strip()
                        logger.info(f"        -> Teléfono: {phone}")
                        break
                if results['phone']:
                    break
            
            # Extraer website
            website_matches = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', text)
            if website_matches:
                for domain in website_matches:
                    if domain and not any(x in domain for x in ['google', 'maps', 'youtube']):
                        results['website'] = f"https://{domain}"
                        logger.info(f"        -> Website: {results['website']}")
                        break
            
            return results if any(results.values()) else None
        
        except Exception as e:
            logger.warning(f"   [Google] Error: {str(e)[:80]}")
            return None
    
    def scrape_company(self, company_id: int, company_name: str, city: str) -> Optional[Dict[str, Any]]:
        """Extrae datos de una empresa"""
        
        print(f"\n=== Buscando: {company_name} ({city})")
        
        results = {
            'phone': None,
            'website': None,
            'address': None,
            'sources': [],
            'status': 'partial'
        }
        
        # INTENTO 1: Páginas Amarillas
        logger.info("1. Buscando en Páginas Amarillas...")
        data = self.search_paginas_amarillas(company_name, city)
        if data and any(data.values()):
            for key, value in data.items():
                if value and not results[key]:
                    results[key] = value
            results['sources'].append('paginas_amarillas')
            time.sleep(2)
        
        # INTENTO 2: Google Direct
        if not results['phone']:
            logger.info("2. Buscando en Google...")
            data = self.search_google_direct(company_name, city)
            if data and any(data.values()):
                for key, value in data.items():
                    if value and not results[key]:
                        results[key] = value
                results['sources'].append('google_search')
            time.sleep(2)
        
        # Determinar estado
        if results['phone'] or results['website'] or results['address']:
            results['status'] = 'completed' if all([results['phone'], results['website']]) else 'partial'
        
        logger.info(f"   Estado: {results['status']}")
        logger.info(f"   Fuentes: {', '.join(results['sources']) or 'ninguna'}")
        
        return results
    
    def get_pending_companies(self, limit: int = 50) -> List:
        """Obtiene empresas sin detalles o con detalles incompletos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.city, c.nit
                FROM companies c
                LEFT JOIN company_details cd ON c.id = cd.company_id
                WHERE c.is_active = 1
                AND (cd.id IS NULL 
                     OR cd.phone = 'N/A' 
                     OR (cd.phone IS NULL))
                ORDER BY c.name
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            logger.info(f"Encontradas {len(results)} empresas para procesar")
            return results
        
        except Exception as e:
            logger.error(f"Error: {e}")
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
            logger.error(f"   Error: {e}")
            return False
    
    def process_companies(self, limit: int = 10) -> Dict[str, Any]:
        """Procesa todas las empresas"""
        
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
        logger.info(f"EJECUTANDO SCRAPER - Procesando {len(companies)} empresas")
        logger.info("Fuentes: Páginas Amarillas + Google Search")
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
                        company['city']
                    )
                    
                    if details and self.save_details(company['id'], details):
                        successful += 1
                
                except Exception as e:
                    logger.error(f"Error procesando: {e}")
                
                time.sleep(3)  # Respetar servidores
        
        finally:
            self.close_db()
        
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
    print("SCRAPER AUTOMÁTICO - Páginas Amarillas + Google Search")
    print("Ejecuta scraper para todas las empresas sin datos reales")
    print("="*80)
    
    scraper = PaginasAmarillasDirectScraper()
    result = scraper.process_companies(limit=10)
    
    print("\n" + "="*80)
    print("RESULTADO")
    print("="*80)
    print(f"Total procesadas: {result['total']}")
    print(f"Exitosas: {result['processed']}")
    print(f"Mensaje: {result['message']}")
    print()


if __name__ == "__main__":
    main()
