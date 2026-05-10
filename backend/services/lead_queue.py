"""
Sistema de Cola de Nichos y Tracking de Leads
Maneja múltiples nichos en paralelo y trackea leads ya enviados
"""
import asyncio
from typing import List, Dict, Any, Set
from datetime import datetime
from collections import deque
import sqlite3
import os


class LeadQueue:
    """Gestiona cola de leads por nicho y tracking de enviados"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
        self.db_path = db_path
        
        # Colas por nicho
        self.niches_queue: Dict[str, deque] = {}
        
        # Tracking de leads ya enviados (por nicho)
        # Formato: {nicho: {company_id, ...}}
        self.sent_leads: Dict[str, Set[int]] = {}
        
        # Estado de scraping por nicho
        self.scraping_status: Dict[str, Dict[str, Any]] = {}
        
        self._init_db()
    
    def _init_db(self):
        """Inicializa tabla de tracking de leads"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sent_leads (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    niche VARCHAR(200) NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, niche)
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error inicializando tracking de leads: {e}")
    
    def add_niche(self, niche: str, target_count: int) -> None:
        """Agrega un nicho a la cola"""
        if niche not in self.niches_queue:
            self.niches_queue[niche] = deque()
            self.sent_leads[niche] = set()
            self.scraping_status[niche] = {
                'status': 'initialized',
                'target': target_count,
                'sent': 0,
                'queued': 0,
                'started_at': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
            self._load_sent_leads(niche)
    
    def _load_sent_leads(self, niche: str) -> None:
        """Carga leads ya enviados del DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT company_id FROM sent_leads WHERE niche = ?
            """, (niche,))
            
            for row in cursor.fetchall():
                self.sent_leads[niche].add(row[0])
            
            conn.close()
        except Exception as e:
            print(f"Error cargando leads enviados: {e}")
    
    def queue_leads(self, niche: str, leads: List[Dict[str, Any]]) -> int:
        """
        Agrega leads a la cola (solo nuevos, no duplicados)
        
        Returns:
            Cantidad de leads nuevos agregados
        """
        if niche not in self.niches_queue:
            self.add_niche(niche, 100)
        
        added = 0
        for lead in leads:
            company_id = lead.get('id')
            
            # No agregar si ya fue enviado
            if company_id not in self.sent_leads[niche]:
                self.niches_queue[niche].append(lead)
                added += 1
        
        if added > 0:
            self.scraping_status[niche]['queued'] = len(self.niches_queue[niche])
            self.scraping_status[niche]['last_update'] = datetime.now().isoformat()
        
        return added
    
    def get_next_lead(self, niche: str) -> Dict[str, Any] | None:
        """Obtiene el siguiente lead de la cola"""
        if niche not in self.niches_queue or len(self.niches_queue[niche]) == 0:
            return None
        
        lead = self.niches_queue[niche].popleft()
        return lead
    
    def mark_as_sent(self, niche: str, company_id: int) -> None:
        """Marca un lead como enviado"""
        if niche not in self.sent_leads:
            self.sent_leads[niche] = set()
        
        self.sent_leads[niche].add(company_id)
        
        # Guardar en BD
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO sent_leads (company_id, niche)
                VALUES (?, ?)
            """, (company_id, niche))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error marcando lead como enviado: {e}")
        
        # Actualizar estado
        if niche in self.scraping_status:
            self.scraping_status[niche]['sent'] += 1
            self.scraping_status[niche]['last_update'] = datetime.now().isoformat()
    
    def get_next_niche(self) -> str | None:
        """Obtiene el siguiente nicho con leads en cola"""
        for niche, queue in self.niches_queue.items():
            if len(queue) > 0:
                # Verificar si ya cumplió target
                status = self.scraping_status[niche]
                if status['sent'] < status['target']:
                    return niche
        
        return None
    
    def get_status(self, niche: str = None) -> Dict[str, Any]:
        """Obtiene estado de nicho o todos"""
        if niche:
            return self.scraping_status.get(niche, {})
        
        return {
            'niches': self.scraping_status,
            'total_niches': len(self.niches_queue),
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_niche(self, niche: str) -> None:
        """Limpia cola de un nicho"""
        if niche in self.niches_queue:
            self.niches_queue[niche].clear()
            self.scraping_status[niche]['queued'] = 0
            self.scraping_status[niche]['last_update'] = datetime.now().isoformat()
    
    def is_complete(self, niche: str) -> bool:
        """Verifica si nicho alcanzó el target"""
        if niche not in self.scraping_status:
            return False
        
        status = self.scraping_status[niche]
        return status['sent'] >= status['target']
    
    def get_completed_niches(self) -> List[str]:
        """Retorna nichos completados"""
        completed = []
        for niche, status in self.scraping_status.items():
            if status['sent'] >= status['target']:
                completed.append(niche)
        return completed


# Instancia singleton
lead_queue = LeadQueue()
