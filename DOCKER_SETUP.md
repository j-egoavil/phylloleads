# 🐳 Docker Setup - Sistema de Scraping con Scoring

## Descripción General

El sistema completo está dockerizado para facilitar deployment:
- **Frontend**: React + Vite (TanStack Start) en Bun
- **Backend**: FastAPI + Scrapers
- **Database**: PostgreSQL + SQLite
- **Orquestación**: Docker Compose

---

## 📋 Pre-requisitos

- Docker Desktop instalado y corriendo
- Docker Compose v2.0+ (incluido en Docker Desktop)
- 4GB RAM mínimo disponible

---

## 🚀 Ejecutar Sistema Completo

### Opción 1: Comando Simple (Recomendado)

```bash
# Desde raíz del proyecto
docker-compose up -d

# Verificar servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Opción 2: Con Build Forzado

```bash
# Reconstruir imágenes
docker-compose up -d --build

# Esperar a que todo inicie (~30-60 segundos)
docker-compose ps
```

### Opción 3: Desarrollo (Con Hot-Reload)

```bash
# Iniciar sin modo daemon (ver logs en terminal)
docker-compose up

# En otro terminal:
docker-compose exec backend bash  # Acceder al backend
docker-compose exec frontend bash # Acceder al frontend
```

---

## 🌐 Acceso a Servicios

Una vez corriendo:

| Servicio | URL | Descripción |
|----------|-----|------------|
| Frontend | http://localhost:3000 | UI de leads |
| Backend API | http://localhost:8000 | FastAPI + docs |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Database | localhost:5432 | PostgreSQL (interno) |

### Verificar que todo funciona

```bash
# Frontend
curl http://localhost:3000

# Backend
curl http://localhost:8000/health

# API
curl http://localhost:8000/api/scraper/status
```

---

## 📝 Configuración

### Variables de Entorno

Crear `.env` en raíz del proyecto:

```env
# Database
DB_NAME=appdb
DB_USER=postgres
DB_PASSWORD=postgres

# (Opcional - hay defaults)
# DB_HOST=database
# DB_PORT=5432
```

Docker Compose usa estas variables automáticamente.

### Personalizar Puertos

En `docker-compose.yml`, cambiar sección `ports:`:

```yaml
backend:
  ports:
    - "8001:8000"      # Cambiar puerto externo (8001)

frontend:
  ports:
    - "3001:3000"      # Cambiar puerto externo (3001)
```

---

## 🔧 Comandos Útiles

### Ver Estado

```bash
# Listar contenedores
docker-compose ps

# Ver logs
docker-compose logs backend       # Solo backend
docker-compose logs frontend      # Solo frontend
docker-compose logs -f            # Todos (tiempo real)

# Ver recursos usados
docker stats
```

### Acceder a Contenedores

```bash
# Terminal en backend
docker-compose exec backend bash

# Terminal en frontend
docker-compose exec frontend bash

# Terminal en database
docker-compose exec database psql -U postgres -d appdb
```

### Ejecutar Comandos

```bash
# Backend: crear base de datos
docker-compose exec backend python -c "from setup_database import setup_db; setup_db()"

# Backend: verificar dependencias
docker-compose exec backend pip list

# Frontend: verificar node_modules
docker-compose exec frontend bun list
```

### Limpiar

```bash
# Detener servicios
docker-compose down

# Detener + eliminar volúmenes (⚠️ borra datos)
docker-compose down -v

# Eliminar imágenes construidas
docker image rm phylloleads_backend phylloleads_frontend

# Limpiar todo (solo si quieres resetear completamente)
docker system prune -a
```

---

## 🐛 Troubleshooting

### "Port already in use"

```bash
# Encontrar qué usa el puerto
lsof -i :3000      # Frontend
lsof -i :8000      # Backend
lsof -i :5432      # Database

# Opción 1: Usar diferentes puertos en docker-compose.yml
# Opción 2: Matar el proceso
kill -9 <PID>

# Opción 3: Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "Cannot connect to Docker daemon"

```bash
# Windows/Mac: Asegurar que Docker Desktop está corriendo
# Verificar:
docker ps

# Si falla, reiniciar Docker Desktop
```

### "Backend no responde"

```bash
# Ver logs del backend
docker-compose logs backend

# Si hay errores de dependencias:
docker-compose rebuild backend

# Reiniciar
docker-compose restart backend

# Acceder para debugging
docker-compose exec backend bash
  # Dentro:
  python -c "import required_module"
```

### "Frontend no conecta a Backend"

```bash
# Verificar desde dentro del contenedor frontend:
docker-compose exec frontend bash
  # Dentro:
  curl http://backend:8000/health

# Si funciona, el problema es CORS - verificar backend/main.py

# Si no funciona, el problema es DNS - reiniciar:
docker-compose restart
```

### "Base de datos no inicializa"

```bash
# Ver logs de database
docker-compose logs database

# Verificar PostgreSQL está healthy
docker-compose ps  # Buscar "health: healthy"

# Reiniciar database
docker-compose restart database

# Limpiar volumen (⚠️ borra datos)
docker-compose down -v
docker-compose up -d database
```

### "Cambios no se reflejan en Backend"

El Dockerfile incluye `--reload` para uvicorn. Si cambian archivos Python deberían reflejarse automáticamente:

```bash
# Si no se refleja, reiniciar
docker-compose restart backend

# Verificar volúmenes montados
docker-compose exec backend ls /app

# Si falta algún archivo, reconstruir
docker-compose down
docker-compose up -d --build
```

---

## 📊 Verificación Post-Startup

```bash
#!/bin/bash
# Script de verificación

echo "🔍 Verificando sistema..."

# 1. Frontend
echo -n "Frontend: "
curl -s http://localhost:3000 > /dev/null && echo "✅" || echo "❌"

# 2. Backend API
echo -n "Backend API: "
curl -s http://localhost:8000/health > /dev/null && echo "✅" || echo "❌"

# 3. WebSocket
echo -n "WebSocket: "
curl -s http://localhost:8000 > /dev/null && echo "✅" || echo "❌"

# 4. Database
echo -n "Database: "
docker-compose exec -T database pg_isready -U postgres > /dev/null 2>&1 && echo "✅" || echo "❌"

echo "✅ Sistema listo!"
```

---

## 🔄 Flujo Típico de Desarrollo

```bash
# 1. Iniciar sistema
docker-compose up -d

# 2. Esperar que todo inicie (30 segundos)
sleep 30

# 3. Verificar estado
docker-compose ps

# 4. Abrir navegador
# http://localhost:3000

# 5. Si necesitas debugging
docker-compose logs -f backend    # Terminal 1: logs backend
docker-compose logs -f frontend   # Terminal 2: logs frontend
# Terminal 3: trabajar en el código

# 6. Hacer cambios (se reflejan automáticamente con --reload)

# 7. Ver cambios en el navegador (refresh)

# 8. Si algo no funciona
docker-compose restart backend
docker-compose restart frontend

# 9. Cuando termines
docker-compose down
```

---

## 🌍 Networking Docker

### Intra-contenedor (Docker Network)

- **Frontend → Backend**: `http://backend:8000`
- **Backend → Frontend**: `http://frontend:3000` (raro, no necesario)
- **Backend → Database**: `postgresql://postgres:password@database:5432/appdb`

### Extra-contenedor (Desde host)

- **Frontend**: `http://localhost:3000`
- **Backend**: `http://localhost:8000`
- **Database**: `postgresql://localhost:5432/appdb`

### WebSocket

Dentro del Frontend Docker:
```javascript
const ws = new WebSocket('ws://backend:8000/api/scraper/ws')
```

Desde el navegador (fuera del Docker):
```javascript
const ws = new WebSocket('ws://localhost:8000/api/scraper/ws')
```

---

## 📦 Persistencia de Datos

### Volúmenes

```yaml
volumes:
  postgres_data:        # Datos de PostgreSQL
    driver: local
  sqlite_data:          # Datos de SQLite
    driver: local
```

### Backup de Database

```bash
# Exportar PostgreSQL
docker-compose exec database pg_dump -U postgres appdb > backup.sql

# Importar
docker-compose exec -T database psql -U postgres < backup.sql

# Copiar volumen
docker run -v phylloleads_postgres_data:/data --rm alpine tar czf - /data > backup.tar.gz
```

---

## 🚀 Production Considerations

Para un ambiente de producción (no development):

1. **Cambiar `.env`**:
```env
DB_PASSWORD=<secure_password>  # No use "postgres"
```

2. **Deshabilitar `--reload`** en backend:
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000
```

3. **Agregar HTTPS**:
```yaml
# Usar nginx como reverse proxy
```

4. **Cambiar NODE_ENV**:
```yaml
frontend:
  environment:
    NODE_ENV: production
```

5. **Limitar recursos**:
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
```

---

## 📚 Archivos de Configuración

```
phylloleads/
├── docker-compose.yml       ← Configuración principal
├── .env                      ← Variables de entorno (crear si no existe)
├── frontend/
│   ├── Dockerfile           ← Build multi-stage con Bun
│   └── .env                 ← Variables frontend
└── backend/
    ├── Dockerfile           ← Python + Selenium + Firefox
    └── entrypoint.sh        ← Script de inicialización
```

---

## ✅ Checklist

- [ ] Docker Desktop instalado y corriendo
- [ ] Proyecto en raíz sin espacios en la ruta
- [ ] Puertos 3000, 8000, 5432 disponibles
- [ ] `docker-compose up -d` ejecutado
- [ ] Esperar 30 segundos para que inicie
- [ ] `docker-compose ps` muestra todo "healthy"
- [ ] http://localhost:3000 carga sin errores
- [ ] http://localhost:8000/health responde 200
- [ ] WebSocket conecta (`ws://localhost:8000/api/scraper/ws`)
- [ ] Logs sin errores (`docker-compose logs`)

---

## 🎯 Próximos Pasos

1. ✅ Sistema corriendo en Docker
2. ⏳ Configurar API URLs en Frontend
3. ⏳ Conectar scrapers a POST `/api/scraper/submit-leads`
4. ⏳ Testear flujo completo
5. ⏳ Optimizar para producción

---

## 📞 Soporte

Si algo no funciona:

1. Revisar logs: `docker-compose logs -f`
2. Verificar puertos: `lsof -i :3000`, `lsof -i :8000`
3. Reiniciar: `docker-compose restart`
4. Reset completo: `docker-compose down -v && docker-compose up -d --build`
5. Verificar archivo `.env` existe

¡Listo! Tu sistema está dockerizado y listo para deployment. 🚀
