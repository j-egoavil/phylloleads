# 🐳 INICIO RÁPIDO - DOCKER (Recomendado)

## ⚠️ TODO DEBE CORRER EN DOCKER

Este proyecto está totalmente dockerizado. **NO instales nada localmente.**

---

## 📋 Pre-requisitos

✅ **Docker Desktop** instalado y corriendo
✅ **Docker Compose v2.0+** (incluido en Docker Desktop)
✅ **4GB RAM** mínimo disponible

---

## 🚀 Iniciar Sistema (3 pasos)

### Paso 1: Abrir Terminal en el Proyecto

```bash
cd phylloleads
```

### Paso 2: Ejecutar Docker Compose

```bash
# Modo recomendado: background
docker-compose up -d

# O ver logs en vivo:
docker-compose up
```

### Paso 3: Esperar a Inicialización

```bash
# Esperar 30-60 segundos

# Verificar estado
docker-compose ps

# Debería mostrar:
# NAME              SERVICE       STATUS      HEALTH
# phylloleads_frontend   frontend  Up 30s      (healthy)
# phylloleads_backend    backend   Up 30s      (healthy)
# phylloleads_database   database  Up 30s      (healthy)
```

---

## ✅ Sistema Listo

Cuando todo está "healthy":

| Servicio | URL |
|----------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

---

## 🧪 Verificar que Funciona

### En Terminal

```bash
curl http://localhost:8000/health
# Debería responder: {"status":"ok"}
```

### En Navegador

1. Abrir: http://localhost:3000
2. Deberías ver página de Leads sin errores
3. Si hay error, ver [Troubleshooting](#troubleshooting)

---

## 🎯 Usar el Sistema

### 1. Configurar Búsqueda

En http://localhost:3000:
- Selecciona nichos (ej: veterinarias, restaurantes)
- Establece target de leads (ej: 50)
- Click "Iniciar Búsqueda"

### 2. El Sistema Espera Leads

El backend está listo para recibir. Puedes:

**Opción A: Enviar Leads de Prueba**
```bash
curl -X POST http://localhost:8000/api/scraper/submit-leads \
  -H "Content-Type: application/json" \
  -d '{
    "niche": "veterinarias",
    "leads": [
      {
        "id": 1,
        "name": "Clínica Veterinaria X",
        "phone": "3001234567",
        "website": "www.x.com",
        "address": "Cll 10",
        "city": "bogota"
      }
    ]
  }'
```

**Opción B: Usar Scraper Interno**
```bash
docker-compose exec backend python scripts/run_scraper_maestro.py
```

### 3. Ver Leads en Tiempo Real

Los leads deberían aparecer inmediatamente en el frontend:
- Nombre, teléfono, website, dirección
- **Puntuación 0-100**
- **Categoría A/B/C** (colores)
- Desglose de puntuación

### 4. Aceptar/Rechazar

- ✓ **Aceptar**: Guarda el lead, solicita el siguiente
- ✗ **Rechazar**: Descarta, solicita el siguiente

---

## 🔧 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f backend
docker-compose logs -f frontend

# Entrar a un contenedor
docker-compose exec backend bash
docker-compose exec frontend bash

# Reiniciar servicios
docker-compose restart
docker-compose restart backend

# Detener todo
docker-compose down

# Limpiar y reiniciar desde cero
docker-compose down -v
docker-compose up -d --build
```

---

## 🐛 Troubleshooting

### ❌ "Port already in use :3000 o :8000"

```bash
# Cambiar puertos en docker-compose.yml:
# Buscar "ports:" y cambiar el primer número
#
# Ej: de "3000:3000" a "3001:3000"
# Luego usar http://localhost:3001
```

### ❌ "Cannot connect to Docker daemon"

```bash
# Abrir Docker Desktop (si está cerrado)
# Verificar que está corriendo
docker ps
```

### ❌ "Contenedor se reinicia (Restarting)"

```bash
# Ver qué está fallando
docker-compose logs backend

# Causas comunes:
# 1. PostgreSQL no inicia → docker-compose restart database
# 2. Falta dependencia → docker-compose rebuild backend
# 3. Puerto ya en uso → Ver error arriba

# Reset completo
docker-compose down -v
docker-compose up -d --build
```

### ❌ "Frontend no ve Backend"

```bash
# Dentro del frontend:
docker-compose exec frontend bash
  curl http://backend:8000/health

# Si falla, reiniciar todo:
docker-compose restart
```

### ❌ "Base de datos no inicializa"

```bash
# Ver logs
docker-compose logs database

# Esperar más tiempo o reiniciar
docker-compose restart database
sleep 10
docker-compose ps
```

---

## 📚 Documentación Completa

- **Docker Detallado**: [DOCKER_SETUP.md](./DOCKER_SETUP.md)
- **Sistema Completo**: [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Arquitectura**: [LEAD_SYSTEM.md](./docs/LEAD_SYSTEM.md)

---

## ✅ Checklist Final

- [ ] Docker Desktop corriendo
- [ ] `docker-compose ps` muestra todos "healthy"
- [ ] http://localhost:3000 carga sin errores
- [ ] http://localhost:8000/health responde 200
- [ ] Página de Leads visible
- [ ] Sistema listo para usar

---

## 🆘 Si Nada Funciona

```bash
# Reset nuclear
docker-compose down -v
docker system prune -a

# Reiniciar Docker Desktop completamente

# Intentar de nuevo
docker-compose up -d --build

# Esperar 60 segundos
sleep 60
docker-compose ps

# Ver logs
docker-compose logs
```

---

¡Listo! Tu sistema Docker está corriendo. 🐳🚀

**Próximo paso**: Ver [DOCKER_SETUP.md](./DOCKER_SETUP.md) para comandos avanzados o [LEAD_SYSTEM.md](./docs/LEAD_SYSTEM.md) para arquitectura.
