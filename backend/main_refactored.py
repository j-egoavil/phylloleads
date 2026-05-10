"""
PHYLLOLEADS - API Principal
Aplicación FastAPI para scraping y enriquecimiento de datos de empresas
"""
import os
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.config import DatabaseConfig

# Crear la aplicación
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_refactored:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False") == "True"
    )
