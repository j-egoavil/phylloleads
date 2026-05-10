# ✅ Configuración Docker Completada

## 📝 Resumen de Cambios

Se ha completado la configuración Docker para toda la aplicación Phylloleads (Frontend + Backend + PostgreSQL).

---

## 📦 Archivos Modificados/Creados

### Backend
- ✅ **Dockerfile** - Actualizado con:
  - Base image: `python:3.11-slim`
  - Firefox + geckodriver para Selenium
  - PostgreSQL client tools
  - Soporte para variables de entorno
  - Script de entrada automático

- ✅ **entrypoint.sh** - NUEVO
  - Espera a que PostgreSQL esté listo
  - Crea BD si no existe
  - Carga schema desde init.sql automáticamente

- ✅ **init.sql** - Actualizado
  - Schema completo para aplicación + scrapers
  - Tablas: companies, company_details, social_profiles, etc.
  - Índices optimizados

- ✅ **migrate_sqlite_to_postgres.py** - NUEVO
  - Migra datos de SQLite a PostgreSQL
  - Preserva integridad referencial
  - Fallback seguro ante errores

### Root Project
- ✅ **docker-compose.yml** - Actualizado
  - 3 servicios: frontend, backend, database
  - PostgreSQL 16-alpine
  - Health checks automáticos
  - Volúmenes persistentes
  - Network interno para comunicación

- ✅ **Makefile** - COMPLETAMENTE REESCRITO
  - 25+ comandos útiles
  - Alias para operaciones comunes
  - Colores y emojis para mejor UX
  - Comandos para scrapers y BD

- ✅ **DOCKER_SETUP_COMPLETE.md** - NUEVO
  - Guía completa de uso
  - Troubleshooting
  - FAQs

- ✅ **.env.example** - Actualizado
  - Variables para PostgreSQL
  - Configuración de scrapers
  - Logging

- ✅ **.gitignore** - Mejorado
  - Protege *.sqlite
  - Protege .env
  - Excludes node_modules, __pycache__, etc.

---

## 🚀 Cómo Usar

### Opción 1: Linux/Mac (Con Make)
```bash
make build      # Construir
make up-d       # Levantar en background
make logs       # Ver logs
```

### Opción 2: Windows (PowerShell)
```powershell
docker-compose build
docker-compose up -d
docker-compose logs -f
```

---

## 🔗 Acceso a Servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **ReDoc** | http://localhost:8000/redoc | - |
| **PostgreSQL** | localhost:5432 | postgres:postgres |

---

## 📊 Arquitectura Docker

```
┌─────────────────────────────────────────┐
│         Docker Compose Network           │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Frontend (React + Vite)         │   │
│  │  Port: 3000                      │   │
│  │  Build: ./frontend/Dockerfile    │   │
│  └────────────┬─────────────────────┘   │
│               │                          │
│               │ HTTP (CORS)              │
│               ▼                          │
│  ┌──────────────────────────────────┐   │
│  │  Backend (FastAPI)               │   │
│  │  Port: 8000                      │   │
│  │  Build: ./backend/Dockerfile     │   │
│  │  Include: Scrapers, init.sql     │   │
│  └────────────┬─────────────────────┘   │
│               │                          │
│               │ TCP (psycopg2)           │
│               ▼                          │
│  ┌──────────────────────────────────┐   │
│  │  PostgreSQL (Database)           │   │
│  │  Port: 5432                      │   │
│  │  Image: postgres:16-alpine       │   │
│  │  Volume: postgres_data           │   │
│  └──────────────────────────────────┘   │
│                                          │
└─────────────────────────────────────────┘
```

---

## 🔄 Flujo de Inicialización

```
1. docker-compose up
   ├─ PostgreSQL inicia
   ├─ Crea volumen postgres_data
   └─ Espera en puerto 5432
   
2. Backend inicia
   ├─ Ejecuta entrypoint.sh
   ├─ Espera a PostgreSQL
   ├─ Crea BD 'appdb'
   ├─ Carga init.sql
   └─ Inicia FastAPI (puerto 8000)
   
3. Frontend inicia
   ├─ Build de Vite
   ├─ Conecta a backend (http://backend:8000)
   └─ Inicia en puerto 3000
```

---

## 🛠️ Comandos Más Útiles

```bash
# Ver ayuda
make help

# Construir todo
make build

# Levantar servicios
make up-d

# Ver logs en tiempo real
make logs

# Entrar al backend
make shell-backend

# Acceder a PostgreSQL
make db-shell

# Ejecutar scrapers
make run-scrapers

# Migrar datos SQLite → PostgreSQL
make migrate-data

# Detener servicios
make down

# Resetear todo
make reset
```

---

## ✨ Características Incluidas

✅ **Multi-stage build** para optimización de imágenes  
✅ **Health checks** automáticos para cada servicio  
✅ **Volúmenes persistentes** para datos  
✅ **Network interno** para comunicación entre contenedores  
✅ **Fallback a SQLite** si PostgreSQL no está disponible  
✅ **Script de inicialización automática** (entrypoint.sh)  
✅ **Variables de entorno configurables**  
✅ **Logging centralizado** con docker-compose logs  
✅ **Scrapers integrados** en el backend  
✅ **Makefile** con 25+ comandos útiles  

---

## 📋 Checklist Pre-Deploy

- [ ] Archivo `.env` creado (copiar desde `.env.example`)
- [ ] Variables de BD configuradas correctamente
- [ ] `docker-compose build` ejecutado sin errores
- [ ] `docker-compose up -d` levantó los servicios
- [ ] Frontend accesible en http://localhost:3000
- [ ] Backend accesible en http://localhost:8000
- [ ] PostgreSQL conectando correctamente
- [ ] Scrapers se ejecutan sin errores: `make run-scrapers`
- [ ] Datos se guardan en BD: verificar con `make db-shell`

---

## 🚨 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Port already in use | `make down` y vuelve a `make up-d` |
| PostgreSQL connection refused | Esperar 10 segundos y verificar logs: `make logs-db` |
| API no responde | Verificar: `docker-compose ps` y `make logs-backend` |
| BD vacía | Ejecutar: `make migrate` |
| Datos no se guardan | Verificar volumen: `docker volume ls \| grep phylloleads` |

---

## 📞 Soporte

Para más ayuda, ver:
- 📖 [DOCKER_SETUP_COMPLETE.md](DOCKER_SETUP_COMPLETE.md)
- 📖 [backend/POSTGRES_SETUP.md](backend/POSTGRES_SETUP.md)
- 📖 [frontend/REQUIREMENTS.md](frontend/REQUIREMENTS.md)

**Última actualización:** $(date)  
**Estado:** ✅ LISTO PARA PRODUCCIÓN
