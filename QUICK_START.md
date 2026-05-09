# 🚀 PHYLLOLEADS - Docker Quick Start

## ✅ Lo que se configuró

```
✓ Frontend (React + Vite)
  ├─ Dockerfile para producción (Nginx)
  ├─ Dockerfile.dev para desarrollo (Hot-reload)
  ├─ nginx.conf configurado
  └─ .dockerignore

✓ Backend (FastAPI + Scraper)
  ├─ Dockerfile existente actualizado
  └─ requirements.txt

✓ Database (PostgreSQL)
  └─ Configurado en Docker

✓ Docker Compose
  ├─ docker-compose.yml (multi-servicio)
  └─ Soporte para dev y producción

✓ Utilidades
  ├─ docker-utils.sh (Linux/Mac)
  ├─ Makefile (Windows/Linux/Mac)
  └─ DOCKER_GUIDE.md (documentación)
```

---

## 🎯 3 Formas de Empezar

### **OPCIÓN 1: Comando Único (Más Simple)**

```bash
# Windows
docker-compose up --build

# Mac/Linux
make start
```

**Qué hace:**
- Construye todas las imágenes
- Inicia todos los servicios
- Muestra URLs

---

### **OPCIÓN 2: Paso a Paso (Más Control)**

```bash
# Construir
docker-compose build

# Ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Acceder a
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

### **OPCIÓN 3: Desarrollo (Con Hot-Reload)**

1. **Edita `docker-compose.yml`:**
   - Comenta la sección `frontend` (líneas 6-32)
   - Descomenta la sección `frontend-dev` (líneas 34-60)

2. **Ejecuta:**
   ```bash
   docker-compose up --build
   ```

3. **Accede a:**
   - Frontend (Vite): http://localhost:5173
   - Backend: http://localhost:8000

---

## 📋 Checklist Pre-Requisitos

- [x] Docker instalado (`docker --version`)
- [x] Docker Compose instalado (`docker-compose --version`)
- [x] Puertos disponibles: 3000, 5173, 8000, 5432
- [x] Espacio en disco: ~2GB

---

## 🎮 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `docker-compose up -d` | Iniciar servicios (background) |
| `docker-compose down` | Detener servicios |
| `docker-compose logs -f` | Ver logs en tiempo real |
| `make build` | Construir imágenes (Makefile) |
| `make ps` | Ver estado (Makefile) |
| `./docker-utils.sh help` | Ayuda (Linux/Mac) |

---

## 🌐 URLs de Acceso

```
Frontend (Producción):  http://localhost:3000
Frontend (Desarrollo):  http://localhost:5173  (si usas Dockerfile.dev)
Backend:               http://localhost:8000
API Docs (Swagger):    http://localhost:8000/docs
Database:              localhost:5432
```

---

## 🔍 Verificar que Funciona

### Frontend OK?
```bash
curl http://localhost:3000
```

### Backend OK?
```bash
curl http://localhost:8000/health
```

### Database OK?
```bash
docker-compose exec database pg_isready -U postgres
```

---

## 🐛 Problemas Comunes

### "Port 3000 already in use"
```bash
# Opción 1: Usar otro puerto
# Edita docker-compose.yml: "3001:3000"

# Opción 2: Liberar el puerto
lsof -i :3000  # Ver qué usa el puerto
kill -9 <PID>   # Matar el proceso
```

### "Cannot connect to backend"
```bash
# Verificar que esté corriendo
docker-compose ps

# Ver logs
docker-compose logs backend

# Reiniciar
docker-compose restart backend
```

### "npm dependencies not installed"
```bash
# Reconstruir sin cache
docker-compose build --no-cache frontend
docker-compose up -d
```

---

## 📁 Estructura después de Docker

```
phylloleads/
├── docker-compose.yml        ← Principal (USAR ESTO)
├── docker-compose.yaml       ← Antigua (opcional eliminar)
├── DOCKER_GUIDE.md           ← Documentación completa
├── Makefile                  ← Comandos rápidos
├── docker-utils.sh           ← Script de utilidades
│
├── frontend/
│   ├── Dockerfile            ← Producción (Nginx)
│   ├── Dockerfile.dev        ← Desarrollo (Vite)
│   ├── nginx.conf            ← Config Nginx
│   ├── .dockerignore         ← Archivos ignorados
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│
├── backend/
│   ├── Dockerfile            ← FastAPI + Python
│   ├── requirements.txt
│   ├── main.py
│   └── scraper_automatico.py
│
└── ...
```

---

## 🎓 Próximos Pasos

1. **Ejecuta:**
   ```bash
   docker-compose up --build
   ```

2. **Espera a que inicie** (30-60 segundos)

3. **Abre en navegador:**
   - http://localhost:3000 (Frontend)
   - http://localhost:8000 (Backend)

4. **Verifica los logs:**
   ```bash
   docker-compose logs -f
   ```

5. **¡Listo!** Tu app está corriendo en Docker

---

## 📚 Documentación

- **DOCKER_GUIDE.md** - Guía completa con troubleshooting
- **Makefile** - Comandos rápidos
- **docker-utils.sh** - Script avanzado

---

## 🔐 Notas de Seguridad

⚠️ **Para Producción:**
- Cambiar contraseña de PostgreSQL
- Usar variables de entorno desde `.env`
- No montear volúmenes en producción
- Usar HTTPS
- Limitar recursos de CPU/memoria

---

**¿Necesitas ayuda?** Ver `DOCKER_GUIDE.md`
