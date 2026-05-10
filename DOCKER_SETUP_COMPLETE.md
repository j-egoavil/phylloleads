# 🐳 Docker Setup - Phylloleads

Guía completa para ejecutar Phylloleads con Docker (Frontend + Backend + PostgreSQL).

---

## ✅ Requisitos Previos

- **Docker Desktop** instalado (Windows/Mac/Linux)
  - Descargar desde: https://www.docker.com/products/docker-desktop
  - Verificar: `docker --version` y `docker-compose --version`

---

## 🚀 Inicio Rápido

### Opción 1: Con Make (Recomendado en Linux/Mac)

```bash
# Crear archivo .env desde el template
make env

# Construir imágenes
make build

# Levantar servicios
make up-d

# Ver logs
make logs
```

**URLs de acceso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Opción 2: Con Docker Compose (Windows/PowerShell)

```powershell
# Crear archivo .env
Copy-Item .env.example -Destination .env

# Construir imágenes
docker-compose build

# Levantar servicios en background
docker-compose up -d

# Ver logs (opcional)
docker-compose logs -f
```

---

## 📋 Estructura Docker

```
phylloleads/
├── frontend/                 # React + Vite (SSR)
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── ...
├── backend/                  # FastAPI + Scrapers
│   ├── Dockerfile
│   ├── entrypoint.sh         # Script de inicialización
│   ├── init.sql              # Schema PostgreSQL
│   ├── requirements.txt
│   └── ...
├── docker-compose.yml        # Orquestación de servicios
├── .env.example              # Variables de entorno
├── Makefile                  # Comandos útiles
└── ...
```

---

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Base de datos PostgreSQL
DB_HOST=database
DB_PORT=5432
DB_NAME=appdb
DB_USER=postgres
DB_PASSWORD=postgres

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Scrapers
SCRAPER_TIMEOUT=900
SCRAPER_LIMIT=50
BROWSER_HEADLESS=true

# Frontend
VITE_API_URL=http://localhost:8000/api
```

O simplemente:
```bash
cp .env.example .env
```

---

## 📊 Servicios

### 1. **Frontend** (Port 3000)
- React + Vite con SSR (TanStack Start con Bun)
- Hot-reload en modo desarrollo
- URL: http://localhost:3000

### 2. **Backend** (Port 8000)
- FastAPI con Scrapers automáticos
- API REST con documentación interactiva
- URLs:
  - API: http://localhost:8000/api
  - Docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

### 3. **PostgreSQL** (Port 5432)
- Base de datos principal
- Schema automático desde `init.sql`
- Usuario: `postgres`
- Contraseña: `postgres` (configurable)

---

## 📦 Comandos Principales

### Build

```bash
# Construir todas las imágenes
make build

# Reconstruir solo backend (después de cambios en requirements.txt)
make build-backend

# Reconstruir con caché limpio
docker-compose build --no-cache
```

### Levantar/Bajar Servicios

```bash
# Levantar con logs activos (Ctrl+C para detener)
make up

# Levantar en background
make up-d

# Detener servicios
make down

# Reiniciar servicios
make restart
```

### Logs

```bash
# Todos los logs
make logs

# Solo backend
make logs-backend

# Solo BD
make logs-db

# Con búsqueda (últimas 50 líneas)
docker-compose logs --tail=50
```

### Acceso Shell

```bash
# Entrar al contenedor backend
make shell-backend

# Acceder a PostgreSQL
make db-shell

# O conectar directamente
docker-compose exec backend bash
docker-compose exec database psql -U postgres
```

---

## 🗄️ Database Management

### Inicializar BD

```bash
# Cargar schema desde init.sql
make migrate

# O manualmente
docker-compose exec database psql -U postgres -d appdb -f /docker-entrypoint-initdb.d/01-init.sql
```

### Comandos PostgreSQL Útiles

```bash
# Entrar a PostgreSQL shell
make db-shell

# Listar bases de datos
\l

# Conectar a appdb
\c appdb

# Ver tablas
\dt

# Ver estructura de tabla
\d companies

# Contar registros
SELECT COUNT(*) FROM companies;
```

### Resetear BD

```bash
# ADVERTENCIA: Esto elimina TODOS los datos
make db-reset

# O manualmente
docker-compose exec -T database psql -U postgres -c "DROP DATABASE appdb;"
docker-compose exec -T database psql -U postgres -c "CREATE DATABASE appdb;"
```

---

## 🕷️ Ejecutar Scrapers

### Dentro del contenedor

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Ejecutar scrapers
python run_scraper_maestro.py --timeout 900

# O por Make
make run-scrapers
```

### Migrar datos de SQLite a PostgreSQL

```bash
# Ejecutar migración
make migrate-data

# O manualmente
docker-compose exec backend python migrate_sqlite_to_postgres.py
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

**Solución:**
- Verificar que Docker Desktop está corriendo
- En Windows: Reiniciar Docker Desktop
- En Linux: `sudo systemctl start docker`

### Error: "port 8000 is already in use"

**Solución:**
```bash
# Usar puerto diferente
docker-compose up -p 8001:8000

# O matar el proceso anterior
docker-compose down
```

### Error: "database 'appdb' does not exist"

**Solución:**
```bash
# Reinicializar BD
make migrate

# O recrear completamente
make db-reset
```

### Backend no conecta a PostgreSQL

**Verifica:**
```bash
# Entrar a backend y probar conexión
docker-compose exec backend bash

# Dentro del contenedor
python -c "import psycopg2; psycopg2.connect(host='database', user='postgres')"

# Si da error, revisar logs
docker-compose logs database
```

### Frontend muestra error de API

**Verifica:**
```bash
# Backend está corriendo
curl http://localhost:8000/health

# CORS está configurado correctamente
# Revisar backend/main.py
```

---

## 🧹 Limpieza

```bash
# Detener servicios (BD se mantiene)
make down

# Limpiar todo incluyendo volúmenes (CUIDADO: borra datos)
make clean
make reset

# O manualmente
docker-compose down -v
```

---

## 📈 Estadísticas y Monitoreo

```bash
# Ver estado de contenedores
make ps

# Estado detallado
make status

# Ver volúmenes
docker volume ls | grep phylloleads

# Usar Docker Stats (tiempo real)
docker stats
```

---

## 🔗 Links Útiles

- **Docker Compose Docs:** https://docs.docker.com/compose/
- **FastAPI:** https://fastapi.tiangolo.com/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **React + Vite:** https://vitejs.dev/

---

## ❓ FAQ

**P: ¿Puedo desarrollar el frontend sin Docker?**
R: Sí, pero debes tener Node.js instalado. Ver `frontend/REQUIREMENTS.md`

**P: ¿Cómo cambio el puerto del frontend/backend?**
R: En `docker-compose.yml`, cambia la línea `ports: - "3000:8080"` (host:container)

**P: ¿Puedo usar SQLite en lugar de PostgreSQL?**
R: Sí, pero no está recomendado en producción. Para desarrollo, descomenta las líneas en `scraper_automatico.py`

**P: ¿Dónde están los datos persistentes?**
R: En volúmenes Docker:
```bash
docker volume inspect phylloleads_postgres_data
```

---

**¿Preguntas o problemas?** Contacta al equipo de desarrollo.
