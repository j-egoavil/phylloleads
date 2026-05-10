# PHYLLOLEADS - Scraper y Enriquecimiento de Datos de Empresas

Aplicación completa para scrapear, organizar y enriquecer datos de empresas desde múltiples fuentes (La República, Google Maps, DuckDuckGo).

## 📁 Estructura del Proyecto

```
phylloleads/
├── backend/                    # API FastAPI + Servicios de scraping
│   ├── app/                   # Código modular (config, modelos, rutas)
│   ├── services/              # Servicios de scraping reutilizables
│   ├── scripts/               # Scripts de automatización (maestro, setup, etc)
│   ├── db/                    # Esquemas SQL y datos
│   ├── tests/                 # Tests unitarios
│   ├── main.py               # Entry point API (actual)
│   ├── main_refactored.py    # Versión modular (WIP)
│   └── requirements.txt
│
├── frontend/                  # React + TanStack Router
├── docs/                      # Documentación centralizada
├── docker-compose.yml         # Orquestación de servicios
└── README.md                  # Este archivo
```

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
# Clonar proyecto
git clone <repo>
cd phylloleads
cp .env.example .env

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. Instalar Dependencias

```bash
pip install -r backend/requirements.txt
```

### 3. Ejecutar Scraper Principal

```bash
python backend/scripts/run_scraper_maestro.py
```

Esto ejecuta automáticamente:
1. Extrae empresas de La República
2. Enriquece datos con Google Maps
3. Genera reportes y exporta JSON

### 4. Iniciar API

```bash
cd backend
python -m uvicorn main:app --reload
```

Accede a `http://localhost:8000/docs` para explorar la API.

## 📦 Estructura del Backend

### `services/`
Contiene los scrapers reutilizables:
- `scraper_la_republica.py` - Extrae empresas de LaRepública.co
- `scraper_automatico.py` - Enriquecimiento multi-fuente
- `google_maps_scraper.py` - Búsqueda en Google Maps

### `scripts/`
Scripts de utilidad y automatización:
- `run_scraper_maestro.py` - Orquesta todo el flujo (ejecuta 3 pasos)
- `setup_database.py` - Inicializa base de datos
- `migrate_sqlite_to_postgres.py` - Migración de datos

### `db/`
Esquemas y queries:
- `schema.sql` - Schema principal de BD
- `results.sql` - Queries útiles

## 🔑 Variables de Entorno

```env
# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
DB_USER=postgres
DB_PASSWORD=postgres
SQLITE_DB=appdb.sqlite  # Fallback

# Scraper
HEADLESS=True
TIMEOUT=30
MAX_RETRIES=3

# API
DEBUG=False
PORT=8000
```

## 🔌 Endpoints Principales

```bash
# Búsqueda
POST /api/search                    # Buscar empresas por nicho
GET  /api/companies/{niche}         # Obtener empresas guardadas

# Datos enriquecidos
GET  /api/companies-with-details    # Con teléfono, website, dirección

# Estadísticas
GET  /api/stats                     # Resumen general
GET  /health                        # Health check
```

## 🐳 Docker

```bash
# Build y run
docker-compose up --build

# Servicios disponibles:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
```

## 📚 Documentación

- **[SCRAPER.md](docs/SCRAPER.md)** - Detalles de scrapers y opciones
- **[DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md)** - Guía de Docker
- **[POSTGRES_SETUP.md](docs/POSTGRES_SETUP.md)** - Configuración PostgreSQL
- **[GUIA_RAPIDA.md](docs/GUIA_RAPIDA.md)** - Start rápido

## 🔧 Comandos Útiles

```bash
# Ejecutar todo el flujo
python backend/scripts/run_scraper_maestro.py

# Setup inicial BD
python backend/scripts/setup_database.py

# Actualizar datos
python backend/scripts/actualizar_datos.py

# Tests
pytest backend/tests/

# API desarrollo
cd backend && python -m uvicorn main:app --reload --port 8000

# API producción
cd backend && python -m uvicorn main:app --workers 4 --port 8000
```

## 📊 Datos Extraídos

- Nombre de empresa
- Número de registro (RUES)
- Ciudad
- Estado (Activa/Inactiva)
- Tamaño de empresa
- Teléfono (enriquecimiento)
- Website (enriquecimiento)
- Dirección (enriquecimiento)

## 🔄 Flujo de Trabajo

```
Run Scraper Maestro
    ↓
[PASO 1] Extrae La República
    ↓ (Si no hay resultados, intenta enriquecimiento)
[PASO 2] Enriquecimiento (Google Maps + DuckDuckGo)
    ↓
[PASO 3] Genera reporte y exporta JSON
    ↓
✅ Datos listos en API y BD
```

## ⚙️ Requierimientos

- Python 3.11+
- PostgreSQL 16 (opcional, SQLite por defecto)
- Firefox o Chrome para Selenium
- Docker (opcional)

## 🐛 Solución de Problemas

**PostgreSQL no conecta**: El sistema usa SQLite automáticamente como fallback.

**Firefox no inicia**: Instala Firefox o usa Chrome editando los scripts.

**Puerto 8000 en uso**: `python -m uvicorn main:app --port 8001`

## 📝 Notas

- Documentación antigua fue consolidada en `docs/`
- Backend tiene estructura modular lista para expansión
- Frontend está separado para independencia
- Todo funciona con SQLite, PostgreSQL opcional

## 📞 Contacto

Para issues o preguntas, crea un issue en el repositorio.
