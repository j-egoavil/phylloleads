from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
import sqlite3
import time
import sys
from pathlib import Path
import asyncio

# Agregar servicios al path
sys.path.insert(0, str(Path(__file__).parent))

from services.scraper_la_republica import EmpresasLaRepublicaScraper
from services.scraper_automatico import AutomaticDataScraper
from app.routes.scraper import router as scraper_router
from app.routes.companies import router as companies_router
from services.lead_queue import lead_queue
from app.routes.scraper import manager
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="Phylloleads - Scraper y Lead Scoring",
    description="API para scrapear empresas, calificar leads y gestionar en tiempo real",
    version="1.0.0"
)

# Incluir routers
app.include_router(scraper_router)
app.include_router(companies_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de salud
@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "name": "Phylloleads API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "scraper": "/api/scraper",
            "companies": "/api/companies"
        }
    }

# Modelos Pydantic
class SearchRequest(BaseModel):
    """Modelo para solicitar búsqueda de empresas"""
    niche: str
    pages: int = 1
    description: Optional[str] = None

class CompanyResponse(BaseModel):
    """Modelo para respuesta de empresa"""
    id: Optional[int]
    name: str
    url: str
    rues: str
    city: str
    is_active: bool
    status: str
    company_size: str
    search_niche: str
    scraped_at: Optional[str]

class SearchResponse(BaseModel):
    """Modelo para respuesta de búsqueda"""
    success: bool
    niche: str
    total_companies: int
    message: str
    companies: Optional[List[dict]]

# Inicializar scraper
def get_scraper():
    """Factory para crear instancias del scraper"""
    return EmpresasLaRepublicaScraper(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "appdb"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
        headless=True
    )

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica que la API esté disponible"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Endpoints de scraping
@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
async def search_companies(request: SearchRequest):
    """
    Busca empresas por nicho en empresas.larepublica.co
    
    Args:
        niche: Término de búsqueda (ej: "veterinarias", "restaurantes")
        pages: Número de páginas a scrapear (default: 1)
    
    Returns:
        SearchResponse con empresas encontradas
    """
    if not request.niche or len(request.niche.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nicho debe tener al menos 2 caracteres")
    
    if request.pages < 1 or request.pages > 10:
        raise HTTPException(status_code=400, detail="El número de páginas debe estar entre 1 y 10")
    
    try:
        scraper = get_scraper()
        logger.info(f"Iniciando búsqueda para nicho: {request.niche}, páginas: {request.pages}")
        
        result = scraper.scrape_and_save(request.niche, request.pages)
        
        return SearchResponse(
            success=result["success"],
            niche=result["niche"],
            total_companies=result["total_companies"],
            message=result["message"],
            companies=result.get("companies", [])
        )
    
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error durante el scrape: {str(e)}")

@app.get("/api/companies/{niche}", tags=["Companies"])
async def get_companies_by_niche(niche: str, limit: int = 100):
    """
    Obtiene empresas guardadas para un nicho específico
    
    Args:
        niche: Nicho a consultar
        limit: Número máximo de resultados
    
    Returns:
        Lista de empresas
    """
    try:
        scraper = get_scraper()
        companies = scraper.get_companies_by_niche(niche)
        
        # Limitar resultados
        companies = companies[:limit]
        
        return {
            "success": True,
            "niche": niche,
            "total": len(companies),
            "companies": companies
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo empresas: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/search-async", tags=["Search"])
async def search_companies_async(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Inicia una búsqueda asincrónica en background
    Ideal para búsquedas largas que no bloqueen la respuesta
    
    Args:
        niche: Término de búsqueda
        pages: Número de páginas a scrapear
    
    Returns:
        Confirmación del inicio de la búsqueda
    """
    if not request.niche or len(request.niche.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nicho debe tener al menos 2 caracteres")
    
    if request.pages < 1 or request.pages > 10:
        raise HTTPException(status_code=400, detail="El número de páginas debe estar entre 1 y 10")
    
    try:
        scraper = get_scraper()
        
        # Agregar tarea al background
        background_tasks.add_task(scraper.scrape_and_save, request.niche, request.pages)
        
        return {
            "success": True,
            "message": f"Búsqueda de '{request.niche}' iniciada en background",
            "niche": request.niche,
            "status": "processing"
        }
    
    except Exception as e:
        logger.error(f"Error iniciando búsqueda async: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """
    Obtiene estadísticas generales del scraper
    """
    try:
        scraper = get_scraper()
        conn = scraper.get_db_connection()
        
        if not conn:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
        
        cur = conn.cursor()
        
        # Total de empresas
        cur.execute("SELECT COUNT(*) FROM companies;")
        total_companies = cur.fetchone()[0]
        
        # Empresas por nicho
        cur.execute("""
            SELECT search_niche, COUNT(*) as count 
            FROM companies 
            GROUP BY search_niche 
            ORDER BY count DESC;
        """)
        companies_by_niche = [{"niche": row[0], "count": row[1]} for row in cur.fetchall()]
        
        # Empresas activas vs inactivas
        cur.execute("""
            SELECT is_active, COUNT(*) 
            FROM companies 
            GROUP BY is_active;
        """)
        status_stats = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        return {
            "total_companies": total_companies,
            "companies_by_niche": companies_by_niche,
            "active_companies": status_stats.get(True, 0),
            "inactive_companies": status_stats.get(False, 0)
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==================== NUEVOS ENDPOINTS: GOOGLE MAPS ENRICHMENT ====================

@app.get("/api/companies-with-details", tags=["Companies"])
async def get_companies_with_details(niche: str = "veterinarias"):
    """
    Obtiene empresas CON detalles de Google Maps
    (Opción 2: Búsqueda Combinada)
    
    Retorna:
    - Nombre, NIT, ciudad
    - Teléfono, website, dirección (del scraper de Google Maps)
    
    Args:
        niche: Nicho a filtrar (default: veterinarias)
    
    Returns:
        Lista de empresas con detalles completos
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect("appdb.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query: Obtener empresas CON sus detalles
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.nit,
                c.city,
                c.is_active,
                c.status,
                c.company_size,
                cd.phone,
                cd.website,
                cd.address,
                cd.scraped_at
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE c.search_niche = ? AND c.is_active = 1
            ORDER BY c.name
        """, (niche,))
        
        companies = []
        for row in cursor.fetchall():
            companies.append({
                "id": row[0],
                "name": row[1],
                "nit": row[2],
                "city": row[3],
                "status": row[5],
                "company_size": row[6],
                "phone": row[7] if row[7] and row[7] != "N/A" else None,
                "website": row[8] if row[8] and row[8] != "N/A" else None,
                "address": row[9] if row[9] and row[9] != "N/A" else None,
                "details_updated_at": row[10]
            })
        
        conn.close()
        
        # Contar con detalles completos
        with_details = sum(1 for c in companies if c["phone"] or c["website"] or c["address"])
        without_details = len(companies) - with_details
        
        return {
            "success": True,
            "niche": niche,
            "total": len(companies),
            "with_details": with_details,
            "without_details": without_details,
            "companies": companies
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo empresas con detalles: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/companies/{company_id}/details", tags=["Companies"])
async def get_company_details(company_id: int):
    """
    Obtiene detalles de Google Maps de una empresa específica
    
    Args:
        company_id: ID de la empresa
    
    Returns:
        Detalles completos: teléfono, website, dirección, etc.
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect("appdb.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.nit,
                c.city,
                c.url,
                cd.phone,
                cd.website,
                cd.address,
                cd.latitude,
                cd.longitude,
                cd.scraped_at
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE c.id = ?
        """, (company_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        
        return {
            "success": True,
            "company": {
                "id": row[0],
                "name": row[1],
                "nit": row[2],
                "city": row[3],
                "url_larepublica": row[4],
                "google_maps": {
                    "phone": row[5] if row[5] and row[5] != "N/A" else None,
                    "website": row[6] if row[6] and row[6] != "N/A" else None,
                    "address": row[7] if row[7] and row[7] != "N/A" else None,
                    "latitude": row[8],
                    "longitude": row[9],
                    "scraped_at": row[10]
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo detalles: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==================== SCRAPER AUTOMÁTICO ====================

@app.post("/api/scraper/enrich-automatic", tags=["Scraper"])
async def enrich_companies_automatic(background_tasks: BackgroundTasks, limit: int = 10):
    """
    Ejecuta enriquecimiento automático en background
    Busca datos faltantes en Google Maps, DuckDuckGo, Páginas Amarillas
    
    Ideal para:
    - Completar datos de teléfono, website, dirección
    - Procesamiento automático sin intervención manual
    - Ejecución en background sin bloquear la API
    
    Args:
        limit: Número de empresas a procesar (default: 10)
    
    Returns:
        ID de tarea en background + estadísticas iniciales
    """
    try:
        def run_scraper():
            """Ejecuta el scraper en background"""
            try:
                logger.info(f"Iniciando enriquecimiento automático: {limit} empresas")
                scraper = AutomaticDataScraper()
                result = scraper.process_companies(limit=limit)
                logger.info(f"Enriquecimiento completado: {result}")
            except Exception as e:
                logger.error(f"Error en enriquecimiento automático: {e}")
        
        # Agregar tarea al background
        background_tasks.add_task(run_scraper)
        
        # Obtener estadísticas actuales
        conn = sqlite3.connect("appdb.sqlite")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE phone != 'N/A' AND phone IS NOT NULL
        """)
        with_phone = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE website != 'N/A' AND website IS NOT NULL
        """)
        with_website = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "message": f"Enriquecimiento de {limit} empresas iniciado en background",
            "status": "processing",
            "current_stats": {
                "total_companies": total,
                "with_phone": with_phone,
                "with_website": with_website,
                "coverage_phone": f"{(with_phone/total*100):.1f}%" if total > 0 else "0%",
                "coverage_website": f"{(with_website/total*100):.1f}%" if total > 0 else "0%"
            }
        }
    
    except Exception as e:
        logger.error(f"Error iniciando enriquecimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/scraper/status", tags=["Scraper"])
async def scraper_status():
    """
    Obtiene estado actual del scraper
    Muestra estadísticas de enriquecimiento
    """
    try:
        conn = sqlite3.connect("appdb.sqlite")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE phone != 'N/A' AND phone IS NOT NULL
        """)
        with_phone = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE website != 'N/A' AND website IS NOT NULL
        """)
        with_website = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM company_details 
            WHERE address != 'N/A' AND address IS NOT NULL
        """)
        with_address = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT search_niche, COUNT(*) as count 
            FROM companies 
            GROUP BY search_niche
        """)
        by_niche = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "success": True,
            "status": "operational",
            "statistics": {
                "total_companies": total,
                "enriched": {
                    "phone": with_phone,
                    "website": with_website,
                    "address": with_address
                },
                "coverage": {
                    "phone": f"{(with_phone/total*100):.1f}%" if total > 0 else "0%",
                    "website": f"{(with_website/total*100):.1f}%" if total > 0 else "0%",
                    "address": f"{(with_address/total*100):.1f}%" if total > 0 else "0%"
                },
                "companies_by_niche": by_niche
            }
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Inicialización
@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logger.info("🚀 Aplicación iniciada")
    scraper = get_scraper()
    scraper.create_tables()
    logger.info("✅ Tablas de base de datos verificadas/creadas")
    
    # Limpiar estados inicializados de reinicios anteriores
    lead_queue.scraping_status.clear()
    logger.info("🧹 Estados de scraping limpiados")
    
    # Iniciar background task de scraping
    asyncio.create_task(background_scraper_task())


async def background_scraper_task():
    """
    Background task que continuamente chequea nichos en cola y lanza el scraper
    Ejecuta en paralelo con la API
    """
    logger.info("🔄 Background scraper task iniciado")
    
    # Esperar a que la app esté lista
    await asyncio.sleep(2)
    
    while True:
        try:
            # Chequear nichos que necesitan scraping (estado initialized)
            niches_to_scrape = [
                niche for niche, status in lead_queue.scraping_status.items()
                if status.get('status') == 'initialized'
            ]
            
            if niches_to_scrape:
                logger.info(f"📊 Nichos a scrapear: {niches_to_scrape}")
                
                for niche in niches_to_scrape:
                    status = lead_queue.scraping_status.get(niche, {})
                    target = status.get('target', 100)
                    
                    logger.info(f"🔍 Iniciando scraper para: {niche} (objetivo: {target})")
                    
                    try:
                        # Ejecutar scraper en thread pool para no bloquear
                        await asyncio.to_thread(run_scraper_for_niche, niche, target)
                    except Exception as e:
                        logger.error(f"❌ Error scraping {niche}: {e}", exc_info=True)
                        lead_queue.scraping_status[niche]['status'] = 'error'
            
            # Esperar antes de siguiente chequeo (reducido a 3 segundos)
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Error en background scraper task: {e}", exc_info=True)
            await asyncio.sleep(3)


def run_scraper_for_niche(niche: str, target_count: int):
    """
    Ejecuta el scraper para un nicho específico con pipeline multi-fuente:
    1. La República: obtiene tabla de empresas
    2. Google Maps: obtiene contacto
    3. Páginas Amarillas: obtiene más contacto
    4. Enriquecimiento y scoring
    Se ejecuta en thread pool para no bloquear la API
    """
    try:
        print(f"\n{'='*80}")
        print(f"🚀 PIPELINE SCRAPER INICIADO: '{niche}' (target: {target_count})")
        print(f"  Fuentes: La República → Google Maps → Páginas Amarillas")
        print(f"{'='*80}\n")
        
        logger.info(f"📥 Pipeline iniciado para: {niche}")
        lead_queue.scraping_status[niche]['status'] = 'running'
        
        # PASO 1: Obtener empresas de La República
        print(f"\n[1/3] 📰 Scrapeando La República para '{niche}'...")
        republica_scraper = EmpresasLaRepublicaScraper(
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "appdb"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", "postgres"),
            headless=True
        )
        
        logger.info(f"🌐 Descargando sitemaps para: {niche}")
        result = republica_scraper.search_by_niche(niche, target_count)
        
        if not result or not result.get('success'):
            logger.warning(f"⚠️ La República retornó resultado vacío para: {niche}")
            print(f"⚠️ La República no encontró empresas para {niche}\n")
            lead_queue.scraping_status[niche]['status'] = 'empty'
            return
        
        companies = result.get('companies', [])
        logger.info(f"✅ Obtenidas {len(companies)} empresas de La República para: {niche}")
        print(f"   ✓ {len(companies)} empresas encontradas\n")
        
        # PASO 2: Enriquecer con información de contacto (Maps, Páginas Amarillas, etc)
        print(f"[2/3] 🗺️  Enriqueciendo con información de contacto...")
        enricher = AutomaticDataScraper(
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "appdb"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", "postgres")
        )
        
        enriched_companies = []
        for idx, company in enumerate(companies, 1):
            raw_name = company.get('name', 'Unknown')
            city = company.get('city', 'Unknown')
            
            # Limpiar el nombre: extrae solo la parte antes del "-"
            # Ejemplo: "NOMBRE S.A.S - Registro Único..." → "NOMBRE S.A.S"
            company_name = raw_name.split('-')[0].strip() if '-' in raw_name else raw_name
            company_name = company_name.split('Registro')[0].strip() if 'Registro' in company_name else company_name
            
            try:
                print(f"   [{idx}/{len(companies)}] {company_name} ({city})...", end="", flush=True)
                
                # Usar AutomaticDataScraper para buscar en múltiples fuentes
                contact_info = enricher.scrape_company(
                    idx,
                    company_name,
                    city
                )
                
                enriched = {
                    'id': idx,
                    'name': company_name,
                    'company': company_name,
                    'email': contact_info.get('email') or '',
                    'phone': contact_info.get('phone') or 'N/A',
                    'website': contact_info.get('website') or company.get('website', 'N/A'),
                    'address': contact_info.get('address') or company.get('address', 'N/A'),
                    'city': city,
                    'niche': niche,
                    'url': company.get('url', ''),
                    'sources': ', '.join(contact_info.get('sources', [])),
                    'source': 'pipeline_multi_source',
                }
                enriched_companies.append(enriched)
                
                status = contact_info.get('status', 'partial')
                print(f" ✓ [{status}]")
                
                # Google Maps necesita pausa más larga para no ser bloqueado
                time.sleep(5)
                
            except Exception as e:
                logger.warning(f"   Error enriqueciendo {company_name}: {e}")
                print(f" ⚠️ (error)")
                # Igual agregar con info básica
                enriched_companies.append({
                    'id': idx,
                    'name': company_name,
                    'company': company_name,
                    'email': '',
                    'phone': 'N/A',
                    'website': company.get('website', 'N/A'),
                    'address': company.get('address', 'N/A'),
                    'city': city,
                    'niche': niche,
                    'url': company.get('url', ''),
                    'sources': 'error_enriquecimiento',
                    'source': 'pipeline_incomplete',
                })
        
        logger.info(f"✅ Enriquecidas {len(enriched_companies)} empresas")
        print(f"   ✓ {len(enriched_companies)} empresas enriquecidas\n")
        
        # PASO 3: Agregar a la cola con información completa
        print(f"[3/3] 📍 Agregando leads a la cola...")
        added_to_queue = lead_queue.queue_leads(niche, enriched_companies)
        
        logger.info(f"📍 Agregadas {added_to_queue} empresas a la cola de {niche}")
        print(f"   ✓ {added_to_queue} leads agregados a la cola\n")
        
        print(f"{'='*80}")
        print(f"✅ PIPELINE COMPLETADO: {len(enriched_companies)} leads para '{niche}'")
        print(f"{'='*80}\n")
        
        lead_queue.scraping_status[niche]['status'] = 'completed'
    
    except Exception as e:
        logger.error(f"❌ Error en pipeline para {niche}: {e}")
        print(f"❌ PIPELINE ERROR for {niche}: {e}\n")
        lead_queue.scraping_status[niche]['status'] = 'error'
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
