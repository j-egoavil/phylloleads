"""Configuración centralizada de la aplicación"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    DEBUG = os.getenv("DEBUG", "False") == "True"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
class DatabaseConfig:
    """Configuración de base de datos"""
    # PostgreSQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "appdb")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    
    # SQLite (fallback)
    SQLITE_DB = os.getenv("SQLITE_DB", "appdb.sqlite")
    
class ScraperConfig:
    """Configuración del scraper"""
    HEADLESS = os.getenv("HEADLESS", "True") == "True"
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
