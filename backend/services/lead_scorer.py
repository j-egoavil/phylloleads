"""
Sistema de Scoring de Leads
Califica leads de 0-100 y asigna categoría A/B/C
"""
from typing import Dict, Any, Tuple
from datetime import datetime
import re


class LeadScorer:
    """Califica la calidad de un lead"""
    
    # Rango de puntuaciones: A (85-100), B (60-84), C (0-59)
    CATEGORY_A = (85, 100)
    CATEGORY_B = (60, 84)
    CATEGORY_C = (0, 59)
    
    def __init__(self):
        self.weights = {
            'name': 10,
            'phone': 25,
            'website': 25,
            'address': 20,
            'email': 10,
            'company_size': 5,
            'active_status': 5
        }
    
    def score_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Califica un lead y retorna puntuación y categoría
        
        Args:
            lead: Dict con datos del lead
            
        Returns:
            Dict con:
            - score: 0-100
            - category: 'A', 'B', 'C'
            - details: breakdown de scoring
        """
        score = 0
        details = {}
        
        # 1. NOMBRE (10 puntos)
        name_score = self._score_name(lead.get('name', ''))
        score += name_score
        details['name'] = name_score
        
        # 2. TELÉFONO (25 puntos) - MUY IMPORTANTE
        phone_score = self._score_phone(lead.get('phone', ''))
        score += phone_score
        details['phone'] = phone_score
        
        # 3. WEBSITE (25 puntos) - MUY IMPORTANTE
        website_score = self._score_website(lead.get('website', ''))
        score += website_score
        details['website'] = website_score
        
        # 4. DIRECCIÓN (20 puntos)
        address_score = self._score_address(lead.get('address', ''))
        score += address_score
        details['address'] = address_score
        
        # 5. EMAIL (10 puntos)
        email_score = self._score_email(lead.get('email', ''))
        score += email_score
        details['email'] = email_score
        
        # 6. TAMAÑO EMPRESA (5 puntos)
        size_score = self._score_company_size(lead.get('company_size', ''))
        score += size_score
        details['company_size'] = size_score
        
        # 7. ESTADO (5 puntos)
        active_score = self._score_active_status(lead.get('is_active', True))
        score += active_score
        details['active_status'] = active_score
        
        # Normalizar a máximo 100
        score = min(100, max(0, score))
        
        # Asignar categoría
        category = self._get_category(score)
        
        return {
            'score': score,
            'category': category,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def _score_name(self, name: str) -> int:
        """Puntuación para nombre (0-10)"""
        if not name or len(name.strip()) < 3:
            return 0
        if len(name) < 5:
            return 5
        return 10
    
    def _score_phone(self, phone: str) -> int:
        """Puntuación para teléfono (0-25)"""
        if not phone or phone.lower() in ['n/a', 'no data', 'unknown']:
            return 0
        
        # Verificar formato válido
        phone_clean = re.sub(r'\D', '', phone)
        
        if len(phone_clean) < 7:
            return 5  # Muy corto
        if len(phone_clean) >= 10:
            return 25  # Completo
        
        return 15  # Parcial
    
    def _score_website(self, website: str) -> int:
        """Puntuación para website (0-25)"""
        if not website or website.lower() in ['n/a', 'no data', 'unknown']:
            return 0
        
        # Verificar si parece un URL válido
        if re.match(r'^https?://', website):
            return 25  # URL completa
        elif '.' in website and len(website) > 5:
            return 20  # Probablemente un dominio
        
        return 10  # Parcial
    
    def _score_address(self, address: str) -> int:
        """Puntuación para dirección (0-20)"""
        if not address or address.lower() in ['n/a', 'no data', 'unknown']:
            return 0
        
        # Contar palabras como indicador de completitud
        words = len(address.split())
        
        if words < 3:
            return 5
        if words < 5:
            return 10
        if words < 8:
            return 15
        return 20
    
    def _score_email(self, email: str) -> int:
        """Puntuación para email (0-10)"""
        if not email or '@' not in email:
            return 0
        
        # Verificar formato básico de email
        if re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return 10
        
        return 5
    
    def _score_company_size(self, size: str) -> int:
        """Puntuación para tamaño empresa (0-5)"""
        if not size or size.lower() in ['n/a', 'unknown']:
            return 0
        return 5
    
    def _score_active_status(self, is_active: bool) -> int:
        """Puntuación para estado (0-5)"""
        return 5 if is_active else 2
    
    def _get_category(self, score: int) -> str:
        """Retorna categoría basada en puntuación"""
        if score >= self.CATEGORY_A[0]:
            return 'A'
        elif score >= self.CATEGORY_B[0]:
            return 'B'
        else:
            return 'C'
    
    def filter_by_category(self, leads: list, category: str) -> list:
        """Filtra leads por categoría"""
        filtered = []
        for lead in leads:
            scored = self.score_lead(lead)
            if scored['category'] == category:
                lead['score'] = scored['score']
                lead['category'] = scored['category']
                filtered.append(lead)
        return filtered


# Instancia singleton
scorer = LeadScorer()
