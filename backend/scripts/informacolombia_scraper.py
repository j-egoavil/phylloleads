import requests
from bs4 import BeautifulSoup
import urllib.parse
import logging
import re
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class InformaColombiaScraper:
    """Scraper especializado para Informa Colombia (Directorio de Empresas)"""
    
    BASE_URL = "https://www.informacolombia.com"
    SEARCH_URL = f"{BASE_URL}/directorio-empresas/buscar"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9,en-US;q=0.8,en;q=0.7'
        })

    def scrape_company(self, name: str, city: str = "") -> Optional[Dict[str, Any]]:
        """Busca y extrae datos de una empresa en Informa Colombia"""
        try:
            query = f"{name} {city}".strip()
            logger.info(f"   [Informa] Buscando: {query}")
            
            # 1. Realizar búsqueda
            params = {'q': query}
            response = self.session.get(self.SEARCH_URL, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Encontrar el primer link de empresa en los resultados
            # Informa suele listar resultados en elementos con clase 'business-name' o dentro de tablas
            company_link = None
            for a in soup.find_all('a', href=True):
                if '/directorio-empresas/informacion-empresa/' in a['href']:
                    company_link = a['href']
                    if not company_link.startswith('http'):
                        company_link = self.BASE_URL + company_link
                    break
            
            if not company_link:
                logger.warning(f"   [Informa] No se encontró perfil para: {name}")
                return None
            
            logger.info(f"   [Informa] Accediendo a perfil: {company_link}")
            
            # 3. Extraer datos del perfil
            profile_resp = self.session.get(company_link, timeout=15)
            profile_resp.raise_for_status()
            profile_soup = BeautifulSoup(profile_resp.text, 'html.parser')
            
            data = {
                'phone': self._extract_field(profile_soup, r'Teléfono'),
                'address': self._extract_field(profile_soup, r'Dirección|Domicilio'),
                'website': self._extract_website(profile_soup),
                'activity': self._extract_field(profile_soup, r'Actividad|Objeto Social'),
                'legal_status': self._extract_field(profile_soup, r'Estado'),
                'source': 'informacolombia'
            }
            
            return data
            
        except Exception as e:
            logger.error(f"   [Informa] Error: {e}")
            return None

    def _extract_field(self, soup: BeautifulSoup, pattern: str) -> Optional[str]:
        """Busca un campo basado en una etiqueta de texto"""
        label = soup.find(text=re.compile(pattern, re.IGNORECASE))
        if label:
            # Usualmente el valor está en el padre o en el siguiente elemento
            container = label.find_parent(['div', 'td', 'p'])
            if container:
                text = container.get_text(strip=True)
                # Limpiar la etiqueta del resultado
                return re.sub(pattern + r'[:\s]*', '', text, flags=re.IGNORECASE).strip()
        return None

    def _extract_website(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el sitio web si existe en el perfil"""
        # Buscar links externos que no sean de redes sociales o de informa
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            if href.startswith('http') and not any(x in href for x in ['informacolombia', 'facebook', 'twitter', 'linkedin', 'instagram']):
                if not a.get_text(strip=True).lower().startswith('ver'):
                    return a['href']
        return None