"""Paquete principal de la aplicación"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import companies, scraper

def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI con middleware"""
    app = FastAPI(
        title="Phylloleads - Scraper API",
        description="API para scrapear y enriquecer datos de empresas",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rutas
    app.include_router(companies.router)
    app.include_router(scraper.router)
    
    # Health check
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "healthy"}
    
    return app
