"""
Rutas para el sistema de scraping con scoring y tiempo real
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime

from services.lead_scorer import scorer
from services.lead_queue import lead_queue

router = APIRouter(prefix="/api/scraper", tags=["scraper"])

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Envía mensaje a todos los clientes conectados"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error enviando WebSocket: {e}")


manager = ConnectionManager()


# Modelos
class StartScraperRequest(BaseModel):
    """Solicitud para iniciar scraper"""
    niches: List[str]  # ["veterinarias", "restaurantes"]
    target_count: int  # Cuántos leads validos por nicho
    min_category: str = 'C'  # Categoría mínima: A, B, C
    max_concurrent: int = 3  # Máximo nichos simultáneos


class LeadResponse(BaseModel):
    """Lead con scoring"""
    id: int
    name: str
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: str
    score: int
    category: str
    niche: str
    timestamp: str


# Endpoints
@router.post("/start")
async def start_scraper(request: StartScraperRequest):
    """Inicia scraper con nichos y targets"""
    
    if not request.niches or len(request.niches) == 0:
        raise HTTPException(status_code=400, detail="Debe especificar al menos un nicho")
    
    if request.target_count < 1 or request.target_count > 10000:
        raise HTTPException(status_code=400, detail="target_count debe estar entre 1 y 10000")
    
    # Agregar nichos a la cola
    for niche in request.niches:
        lead_queue.add_niche(niche, request.target_count)
    
    # Broadcast de inicio
    await manager.broadcast({
        'type': 'scraper_started',
        'niches': request.niches,
        'target_count': request.target_count,
        'timestamp': datetime.now().isoformat()
    })
    
    return {
        'success': True,
        'message': f'Scraper iniciado para {len(request.niches)} nicho(s)',
        'niches': request.niches,
        'target_count': request.target_count
    }


@router.post("/submit-leads")
async def submit_leads(niche: str, leads: List[dict]):
    """
    Backend de scraper envía leads nuevos
    Solo agrega leads que no fueron enviados previamente
    """
    
    if not niche or not leads:
        return {'added': 0, 'duplicates': 0}
    
    # Filtrar duplicados
    new_leads = []
    duplicates = 0
    
    for lead in leads:
        company_id = lead.get('id')
        if company_id in lead_queue.sent_leads.get(niche, set()):
            duplicates += 1
        else:
            new_leads.append(lead)
    
    # Agregar a cola
    added = lead_queue.queue_leads(niche, new_leads)
    
    return {
        'added': added,
        'duplicates': duplicates,
        'queued': len(lead_queue.niches_queue.get(niche, []))
    }


@router.get("/next-lead")
async def get_next_lead(niche: Optional[str] = None):
    """
    Frontend solicita siguiente lead
    Si no especifica nicho, obtiene del siguiente en cola
    """
    
    # Determinar nicho a usar
    if not niche:
        niche = lead_queue.get_next_niche()
        if not niche:
            return {'success': False, 'message': 'No hay leads en cola'}
    
    # Obtener lead
    lead = lead_queue.get_next_lead(niche)
    
    if not lead:
        return {'success': False, 'message': f'No hay más leads para {niche}'}
    
    # Calificar lead
    scored = scorer.score_lead(lead)
    
    # Enriquecer respuesta
    lead_response = {
        'success': True,
        'lead': {
            'id': lead.get('id'),
            'name': lead.get('name'),
            'phone': lead.get('phone'),
            'website': lead.get('website'),
            'address': lead.get('address'),
            'city': lead.get('city'),
            'niche': niche,
            'score': scored['score'],
            'category': scored['category'],
            'scoring_details': scored['details']
        },
        'queue_status': {
            'niche': niche,
            'remaining': len(lead_queue.niches_queue.get(niche, [])),
            'target': lead_queue.scraping_status.get(niche, {}).get('target', 0),
            'sent': lead_queue.scraping_status.get(niche, {}).get('sent', 0)
        }
    }
    
    return lead_response


@router.post("/accept-lead/{lead_id}")
async def accept_lead(lead_id: int, niche: str):
    """Frontend acepta un lead (marca como enviado)"""
    
    lead_queue.mark_as_sent(niche, lead_id)
    
    # Broadcast
    status = lead_queue.get_status(niche)
    await manager.broadcast({
        'type': 'lead_accepted',
        'lead_id': lead_id,
        'niche': niche,
        'status': status,
        'timestamp': datetime.now().isoformat()
    })
    
    return {'success': True, 'lead_id': lead_id, 'niche': niche}


@router.get("/status")
async def get_scraper_status(niche: Optional[str] = None):
    """Obtiene estado del scraper"""
    
    if niche:
        return lead_queue.get_status(niche)
    
    return lead_queue.get_status()


@router.get("/stats")
async def get_scraper_stats():
    """Obtiene estadísticas generales"""
    
    stats = {
        'total_niches': len(lead_queue.niches_queue),
        'niches': {},
        'timestamp': datetime.now().isoformat()
    }
    
    for niche, queue in lead_queue.niches_queue.items():
        status = lead_queue.scraping_status.get(niche, {})
        stats['niches'][niche] = {
            'target': status.get('target'),
            'sent': status.get('sent'),
            'queued': len(queue),
            'progress': f"{status.get('sent', 0)}/{status.get('target', 0)}",
            'is_complete': lead_queue.is_complete(niche)
        }
    
    return stats


# WebSocket para actualizaciones en tiempo real
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para recibir actualizaciones en tiempo real"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'get_status':
                # Client solicita estado
                status = lead_queue.get_status()
                await websocket.send_json({
                    'type': 'status_update',
                    'data': status,
                    'timestamp': datetime.now().isoformat()
                })
            
            elif message.get('type') == 'get_next_lead':
                # Client solicita siguiente lead
                niche = message.get('niche')
                lead = lead_queue.get_next_lead(niche)
                
                if lead:
                    scored = scorer.score_lead(lead)
                    await websocket.send_json({
                        'type': 'new_lead',
                        'lead': {
                            'id': lead.get('id'),
                            'name': lead.get('name'),
                            'phone': lead.get('phone'),
                            'website': lead.get('website'),
                            'address': lead.get('address'),
                            'city': lead.get('city'),
                            'niche': niche,
                            'score': scored['score'],
                            'category': scored['category']
                        }
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
