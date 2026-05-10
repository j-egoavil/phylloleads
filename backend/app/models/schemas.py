"""Esquemas Pydantic para la API"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SearchRequest(BaseModel):
    """Modelo para solicitar búsqueda de empresas"""
    niche: str
    pages: int = 1
    description: Optional[str] = None

class CompanyResponse(BaseModel):
    """Modelo para respuesta de empresa"""
    id: Optional[int]
    name: str
    url: Optional[str] = None
    rues: Optional[str] = None
    city: Optional[str] = None
    is_active: bool
    status: Optional[str] = None
    company_size: Optional[str] = None
    search_niche: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    scraped_at: Optional[datetime] = None

class SearchResponse(BaseModel):
    """Modelo para respuesta de búsqueda"""
    success: bool
    niche: str
    total_companies: int
    message: str
    companies: Optional[List[dict]] = None

class EnrichmentRequest(BaseModel):
    """Modelo para solicitar enriquecimiento de datos"""
    company_ids: Optional[List[int]] = None
    niche: Optional[str] = None

class EnrichmentResponse(BaseModel):
    """Modelo para respuesta de enriquecimiento"""
    success: bool
    total_processed: int
    successful: int
    failed: int
    message: str
