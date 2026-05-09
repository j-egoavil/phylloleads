# 🐳 Phylloleads - Guía Docker

## 📋 Requisitos

- Docker
- Docker Compose
- (Opcional) Git

## 🚀 Inicio Rápido

### **OPCIÓN 1: Producción (Recomendado)**

```bash
# 1. Clonar/descargar el proyecto
cd phylloleads

# 2. Construir y ejecutar
docker-compose up --build

# 3. Acceder a:
#    - Frontend: http://localhost:3000
#    - Backend API: http://localhost:8000
#    - API Docs: http://localhost:8000/docs
#    - Database: localhost:5432
```

**Puertos:**
- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432

---

### **OPCIÓN 2: Desarrollo (Con Hot-Reload)**

Edita `docker-compose.yml` y:

1. **Comenta** la sección `frontend` (líneas ~6-32)
2. **Descomenta** la sección `frontend-dev` (líneas ~34-60)

```bash
# Ejecutar con hot-reload
docker-compose up --build

# Acceder a:
#    - Frontend: http://localhost:5173 (Vite dev server)
#    - Backend: http://localhost:8000
```

---

## 📦 Estructura

```
phylloleads/
├── docker-compose.yml    ← Configuración multi-contenedor
├── frontend/
│   ├── Dockerfile        ← Para producción (Nginx)
│   ├── Dockerfile.dev    ← Para desarrollo (Vite)
│   ├── nginx.conf        ← Configuración Nginx
│   └── ...
├── backend/
│   ├── Dockerfile        ← FastAPI + Scraper
│   ├── main.py
│   ├── requirements.txt
│   └── ...
└── docker/
    └── (otra config)
```

---

## 🛠️ Comandos Útiles

### Construcción

```bash
# Construir todas las imágenes
docker-compose build

# Construir solo frontend
docker-compose build frontend

# Construir solo backend
docker-compose build backend

# Construir sin cache
docker-compose build --no-cache
```

### Ejecución

```bash
# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f database

# Detener
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Depuración

```bash
# Entrar a un contenedor
docker-compose exec frontend sh
docker-compose exec backend bash
docker-compose exec database psql -U postgres

# Ver estado de servicios
docker-compose ps

# Reiniciar un servicio
docker-compose restart frontend
```

---

## 🌐 Endpoints

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:3000 | React App |
| Backend | http://localhost:8000 | FastAPI |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/health | Estado del backend |
| Database | localhost:5432 | PostgreSQL |

---

## 🔧 Variables de Entorno

### Backend (en docker-compose.yml)
```
DB_HOST=database          # Nombre del servicio en Docker
DB_PORT=5432              # Puerto PostgreSQL
DB_NAME=phylloleads       # Nombre de la BD
DB_USER=postgres          # Usuario PostgreSQL
DB_PASSWORD=postgres      # Contraseña
```

### Frontend (en docker-compose.yml)
```
VITE_API_URL=http://localhost:8000/api  # URL del backend
```

---

## 🐛 Troubleshooting

### "Cannot connect to database"
```bash
# Asegurar que PostgreSQL esté corriendo
docker-compose ps

# Ver logs del database
docker-compose logs database

# Reiniciar servicios
docker-compose restart database backend
```

### "Port 3000 already in use"
```bash
# Cambiar puerto en docker-compose.yml
# Cambiar: "3000:3000" a "3001:3000"
docker-compose up -d
```

### "Frontend no conecta con Backend"
```bash
# Verificar que ambos estén en la misma red
docker network ls
docker network inspect phylloleads_network

# Verificar logs
docker-compose logs backend
docker-compose logs frontend
```

### "npm/bun dependencies not installed"
```bash
# Reconstruir sin cache
docker-compose build --no-cache frontend
docker-compose up
```

---

## 📊 Verificación de Servicios

### Frontend
```bash
# Comprobar que está servido
curl http://localhost:3000

# En desarrollo (Vite)
curl http://localhost:5173
```

### Backend
```bash
# Health check
curl http://localhost:8000/health

# Ver API docs
curl http://localhost:8000/docs
```

### Database
```bash
# Conectar a PostgreSQL
docker-compose exec database psql -U postgres -d phylloleads

# Ver tablas
\dt

# Ver usuarios
\du
```

---

## 🚀 Despliegue a Producción

1. **Actualizar imagen base:**
   ```dockerfile
   FROM node:20-alpine  # usar versión LTS
   ```

2. **Optimizaciones:**
   - Desabilitar volúmenes en producción
   - Usar variables de entorno seguras
   - Revisar permisos de contenedores

3. **Registrarse en Docker Hub:**
   ```bash
   docker tag frontend:latest tu-usuario/phylloleads-frontend:latest
   docker push tu-usuario/phylloleads-frontend:latest
   ```

---

## 📚 Documentación Adicional

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [React + Vite](https://vitejs.dev/)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Nginx Config](https://nginx.org/en/docs/)

---

**Versión:** 1.0  
**Última actualización:** Mayo 2026
