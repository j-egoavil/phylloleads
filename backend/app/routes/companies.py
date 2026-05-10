"""
Rutas para gestión de empresas
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import sqlite3
import os

router = APIRouter(prefix="/api/companies", tags=["companies"])


def get_db_connection():
    """Obtiene conexión a BD"""
    db_path = os.getenv("APP_DB_PATH", "appdb.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
async def get_companies(
    niche: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Obtiene empresas con filtros"""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM companies WHERE 1=1"
        params = []
        
        if niche:
            query += " AND search_niche = ?"
            params.append(niche)
        
        if city:
            query += " AND city = ?"
            params.append(city)
        
        query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        companies = [dict(row) for row in rows]
        conn.close()
        
        return {
            'success': True,
            'total': len(companies),
            'companies': companies
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_id}")
async def get_company(company_id: int):
    """Obtiene detalles de una empresa"""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Empresa
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        
        if not company:
            conn.close()
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        
        # Detalles
        cursor.execute("""
            SELECT * FROM company_details 
            WHERE company_id = ?
        """, (company_id,))
        details = cursor.fetchone()
        
        conn.close()
        
        result = dict(company)
        if details:
            result['details'] = dict(details)
        
        return {
            'success': True,
            'company': result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/niche/{niche}")
async def get_companies_by_niche(niche: str, limit: int = 50):
    """Obtiene empresas por nicho"""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, cd.phone, cd.website, cd.address
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE c.search_niche = ? AND c.is_active = 1
            LIMIT ?
        """, (niche, limit))
        
        rows = cursor.fetchall()
        companies = [dict(row) for row in rows]
        conn.close()
        
        return {
            'success': True,
            'niche': niche,
            'total': len(companies),
            'companies': companies
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/{city}")
async def get_companies_by_city(city: str, limit: int = 50):
    """Obtiene empresas por ciudad"""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, cd.phone, cd.website, cd.address
            FROM companies c
            LEFT JOIN company_details cd ON c.id = cd.company_id
            WHERE c.city = ? AND c.is_active = 1
            LIMIT ?
        """, (city, limit))
        
        rows = cursor.fetchall()
        companies = [dict(row) for row in rows]
        conn.close()
        
        return {
            'success': True,
            'city': city,
            'total': len(companies),
            'companies': companies
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
