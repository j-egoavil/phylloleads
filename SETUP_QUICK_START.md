# 🚀 Inicio Rápido - Sistema de Scraping con Scoring

## Pre-requisitos
- Python 3.10+
- Node.js 18+
- SQLite (incluido)
- Docker (opcional)

---

## 1️⃣ Configurar Backend

### Paso 1: Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### Paso 2: Inicializar base de datos

```bash
# SQLite se crea automáticamente
# Para schema inicial:
python -c "from setup_database import setup_db; setup_db()"
```

### Paso 3: Configurar variables de entorno

Crear `backend/.env`:
```env
DB_PATH=appdb.sqlite
HEADLESS=True
APP_DB_PATH=./appdb.sqlite
```

### Paso 4: Iniciar API

```bash
python -m uvicorn main:app --reload --port 8000
```

✅ API disponible en: `http://localhost:8000`
✅ Docs en: `http://localhost:8000/docs`

---

## 2️⃣ Configurar Frontend

### Paso 1: Instalar dependencias

```bash
cd frontend
npm install
```

### Paso 2: Configurar variables de entorno

Crear `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Paso 3: Iniciar servidor de desarrollo

```bash
npm run dev
```

✅ Frontend disponible en: `http://localhost:5173`

---

## 3️⃣ Verificar Sistema

### Verificar Backend

```bash
# En otra terminal
curl http://localhost:8000/health

# Respuesta esperada:
# {"status": "ok"}
```

### Verificar Conexión

1. Abre Frontend: http://localhost:5173
2. Deberías ver la página de Leads
3. Si hay error de conexión, verifica:
   - ✓ Backend corriendo en puerto 8000
   - ✓ VITE_API_URL en frontend/.env es correcto

---

## 4️⃣ Usar el Sistema

### Opción A: Con Scraper Automático

```bash
# Terminal 3: Iniciar scraper
cd backend
python scripts/run_scraper_maestro.py
```

Luego:
1. Abre Frontend
2. Selecciona nichos (ej: veterinarias, restaurantes)
3. Establece target (ej: 50 leads)
4. Click "Iniciar Búsqueda"
5. El scraper enviará leads automáticamente
6. Acepta/rechaza en tiempo real

### Opción B: Prueba Manual

```bash
# Terminal alternativa para testing

# 1. Iniciar scraper
curl -X POST http://localhost:8000/api/scraper/start \
  -H "Content-Type: application/json" \
  -d '{
    "niches": ["veterinarias"],
    "target_count": 10,
    "min_category": "C"
  }'

# 2. Enviar leads de prueba
curl -X POST http://localhost:8000/api/scraper/submit-leads \
  -H "Content-Type: application/json" \
  -d '{
    "niche": "veterinarias",
    "leads": [
      {
        "id": 1,
        "name": "Clínica Veterinaria X",
        "phone": "3001234567",
        "website": "www.clinica-x.com",
        "address": "Cll 10 #20-30",
        "city": "bogota"
      }
    ]
  }'

# 3. Obtener lead
curl http://localhost:8000/api/scraper/next-lead

# 4. Aceptar lead
curl -X POST http://localhost:8000/api/scraper/accept-lead/1?niche=veterinarias

# 5. Ver estado
curl http://localhost:8000/api/scraper/status
```

---

## 5️⃣ Debugging

### Backend no responde

```bash
# Verificar puerto
lsof -i :8000
netstat -tlnp | grep 8000

# Reiniciar (Windows)
taskkill /F /IM python.exe
```

### Frontend no conecta

```bash
# Verificar console del navegador (F12)
# Buscar errores de conexión

# Verificar CORS
curl -i http://localhost:8000/api/scraper/status
# Debería ver: Access-Control-Allow-Origin: *
```

### Base de datos corrupta

```bash
# Eliminar y recrear
rm backend/appdb.sqlite
cd backend
python -c "from setup_database import setup_db; setup_db()"
```

### WebSocket no conecta

```bash
# Verificar en console del navegador
# ws://localhost:8000/api/scraper/ws

# Test manual con websocat
# pip install websocat
# websocat ws://localhost:8000/api/scraper/ws
```

---

## 📊 Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│  USUARIO                                                 │
│  1. Abre Frontend (http://localhost:5173)                │
│  2. Selecciona nichos y target                           │
│  3. Click "Iniciar Búsqueda"                             │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP + WebSocket
                       ▼
┌──────────────────────────────────────────────────────────┐
│  BACKEND (http://localhost:8000)                         │
│  1. Recibe /api/scraper/start                            │
│  2. Crea colas para nichos                               │
│  3. Broadcast status vía WebSocket                       │
└──────────────────────┬──────────────────────────────────┘
                       │
     ┌─────────────────┴─────────────────┐
     ▼                                   ▼
┌──────────────────┐            ┌──────────────────┐
│ SCRAPER BACKEND  │            │ FRONTEND         │
│ 1. Busca empresas│            │ 1. Muestra UI    │
│ 2. POST /submit  │            │ 2. Solicita lead │
│    -leads        │            │ 3. GET /next     │
│ 3. Recibe count  │            │ 4. Muestra score │
│    de agregados  │            │ 5. Espera click  │
└──────────────────┘            │ 6. POST /accept  │
                                │ 7. Repite        │
                                └──────────────────┘
```

---

## 🔌 Endpoints Clave

| Método | Endpoint | Parámetros | Descripción |
|--------|----------|-----------|-------------|
| POST | `/api/scraper/start` | niches, target_count | Inicia búsqueda |
| POST | `/api/scraper/submit-leads` | niche, leads[] | Backend envía leads |
| GET | `/api/scraper/next-lead` | - | Obtiene lead siguiente |
| POST | `/api/scraper/accept-lead/{id}` | niche | Marca como enviado |
| GET | `/api/scraper/status` | - | Ve estado actual |
| WS | `/api/scraper/ws` | - | Conexión tiempo real |

---

## 📝 Logs

### Backend logs
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process [12345]
INFO:     POST /api/scraper/start - received
INFO:     Created queues for 2 niches
INFO:     Added 5 leads to veterinarias queue
```

### Frontend logs (Console)
```
[11:30:00] Conectando a ws://localhost:8000/api/scraper/ws
[11:30:01] WebSocket conectado
[11:30:02] Solicitud GET /api/scraper/next-lead
[11:30:03] Lead recibido: Clínica Veterinaria X (Score: 92)
```

---

## ⚙️ Customización

### Cambiar scoring

Editar `backend/services/lead_scorer.py`:
```python
WEIGHTS = {
    'name': 10,           # ← cambiar aquí
    'phone': 25,
    'website': 25,
    'address': 20,
    'email': 10,
    'company_size': 5,
    'active_status': 5
}
```

### Cambiar categorías

Editar `backend/services/lead_scorer.py`:
```python
def _get_category(self, score):
    if score >= 90:        # ← cambiar aquí
        return 'A'
    elif score >= 60:
        return 'B'
    else:
        return 'C'
```

### Agregar nichos

1. En Frontend, editar `frontend/src/routes/leads.tsx` - lista de nichos
2. Sistema soporta N nichos automáticamente

---

## 🐛 Troubleshooting

### Error: `Address already in use :8000`
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: `ModuleNotFoundError`
```bash
cd backend
pip install -r requirements.txt --upgrade
```

### Error: `CORS error from frontend`
- ✓ Verificar `http://localhost:8000` es accesible
- ✓ Verificar CORS headers: `curl -i http://localhost:8000/health`
- ✓ Verificar VITE_API_URL en .env

### Error: `WebSocket connection refused`
- ✓ Verificar backend corriendo
- ✓ Verificar puerto 8000 disponible
- ✓ Verificar firewall no bloquea

---

## 📚 Documentación Completa

Ver [LEAD_SYSTEM.md](./LEAD_SYSTEM.md) para:
- Arquitectura detallada
- Diagramas de flujo
- Especificación de scoring
- Todos los endpoints
- Ejemplos de requests/responses

---

## ✅ Checklist de Inicio

- [ ] Backend instalado y dependencias correctas
- [ ] Frontend instalado y dependencias correctas
- [ ] Backend running en puerto 8000
- [ ] Frontend running en puerto 5173
- [ ] Verificada conexión con curl
- [ ] Verificada conexión desde browser
- [ ] .env files configurados correctamente
- [ ] Base de datos inicializada
- [ ] Listo para iniciar scraper y usar sistema

---

## 📞 Soporte

Si algo no funciona:

1. ✓ Verifica los logs (terminal donde corre backend/frontend)
2. ✓ Prueba endpoints directamente con curl
3. ✓ Verifica console del navegador (F12)
4. ✓ Verifica puertos: 8000 (backend), 5173 (frontend)
5. ✓ Verifica .env files existen y son correctos
6. ✓ Lee [LEAD_SYSTEM.md](./LEAD_SYSTEM.md)

---

¡Listo! El sistema está configurado y listo para usar. 🎉
