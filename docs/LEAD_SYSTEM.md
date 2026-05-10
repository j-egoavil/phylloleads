# Sistema de Scraping con Scoring en Tiempo Real

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│  - LeadsPage: Interfaz de usuario para gestionar leads      │
│  - useLeadScraper: Hook para conectar con la API            │
│  - WebSocket: Conexión en tiempo real                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP + WebSocket
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│                                                              │
│  📍 Endpoints:                                              │
│  ├── POST /api/scraper/start        (Iniciar búsqueda)     │
│  ├── GET  /api/scraper/next-lead    (Obtener lead)         │
│  ├── POST /api/scraper/accept-lead  (Aceptar lead)         │
│  ├── GET  /api/scraper/status       (Estado)               │
│  ├── WS   /api/scraper/ws           (Tiempo real)          │
│  └── GET  /api/companies/...        (Datos)                │
│                                                              │
│  🔄 Servicios:                                              │
│  ├── LeadScorer: Califica leads 0-100 (A/B/C)             │
│  ├── LeadQueue: Cola por nichos + tracking                │
│  ├── Scrapers: Extrae datos (La República, Maps, etc)     │
│  └── ConnectionManager: WebSockets para actualiz. real     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 BASE DE DATOS (SQLite)                       │
│  - companies: Empresas extraídas                            │
│  - company_details: Información enriquecida                 │
│  - sent_leads: Tracking de leads ya enviados               │
└─────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos

### 1. Iniciar Búsqueda

```
Usuario selecciona nichos → Frontend envía:
  {
    "niches": ["veterinarias", "restaurantes"],
    "target_count": 50,
    "min_category": "C"
  }
  
→ Backend crea colas por nicho
→ WebSocket broadcast: "scraper_started"
```

### 2. Scraper Backend Envía Leads

```
Scraper encuentra empresas → Envía a /api/scraper/submit-leads
{
  "niche": "veterinarias",
  "leads": [
    {
      "id": 1,
      "name": "Clínica Veterinaria X",
      "phone": "3001234567",
      "website": "www.clinica-x.com",
      "address": "Cll 10 #20-30",
      "city": "bogota"
    },
    ...
  ]
}

→ Backend filtra duplicados
→ Agrega a LeadQueue
→ Broadcast: "leads_queued"
```

### 3. Frontend Solicita Lead

```
Frontend → GET /api/scraper/next-lead

Backend:
  1. Obtiene lead de cola
  2. LeadScorer lo califica (0-100)
  3. Asigna categoría (A/B/C)
  4. Retorna con metadata

Frontend recibe:
{
  "lead": {
    "id": 1,
    "name": "Clínica Veterinaria X",
    "score": 92,
    "category": "A",
    "scoring_details": {
      "name": 10,
      "phone": 25,
      "website": 25,
      ...
    }
  },
  "queue_status": {
    "niche": "veterinarias",
    "remaining": 45,
    "target": 50,
    "sent": 5
  }
}
```

### 4. Usuario Acepta/Rechaza

```
Si ACEPTA:
  → POST /api/scraper/accept-lead/{lead_id}?niche=veterinarias
  → Backend marca como enviado (sent_leads table)
  → WebSocket broadcast status
  → Frontend solicita siguiente

Si RECHAZA:
  → Solo solicita siguiente sin guardar
  → Lead descartado
```

---

## Sistema de Scoring (LeadScorer)

### Criterios y Puntuación

| Criterio | Máx Puntos | Detalles |
|----------|-----------|----------|
| Nombre | 10 | Válido si >3 caracteres |
| Teléfono | 25 | ✅ Completo: 25pts |
| Website | 25 | ✅ URL válida: 25pts |
| Dirección | 20 | Basado en cantidad de palabras |
| Email | 10 | Formato válido: 10pts |
| Tamaño Empresa | 5 | Si disponible: 5pts |
| Estado Activo | 5 | Si is_active=true: 5pts |
| **TOTAL** | **100** | |

### Categorías

```
Score ≥ 85 → A (Excelente)
60-84     → B (Bueno)
0-59      → C (Aceptable)
```

### Ejemplos

```
Lead 1 (Completo):
  - Nombre: 10 ✓
  - Teléfono: 25 ✓
  - Website: 25 ✓
  - Dirección: 20 ✓
  - Email: 0
  - Tamaño: 5 ✓
  - Estado: 5 ✓
  TOTAL: 90 → Categoría A

Lead 2 (Parcial):
  - Nombre: 10 ✓
  - Teléfono: 15 (corto)
  - Website: 0
  - Dirección: 10 (corta)
  - Email: 0
  - Tamaño: 5 ✓
  - Estado: 5 ✓
  TOTAL: 45 → Categoría C
```

---

## Cola de Nichos (LeadQueue)

### Funcionamiento

```
1. Frontend inicia: niches = ["veterinarias", "restaurantes"]
   → LeadQueue crea 2 colas independientes
   → Tracking de enviados por nicho

2. Scraper envía leads por nicho
   → Filtro de duplicados (sent_leads)
   → Agrega a queue si es nuevo

3. Frontend solicita lead
   → get_next_niche() retorna próximo con leads
   → Si veterinarias tiene 45 leads y restaurantes 30
   → Prioriza veterinarias (está antes en la lista)

4. Cuando nicho cumple target (ej: 50 leads)
   → Se marca como completo
   → Frontend puede ver progreso
```

### Tracking de Leads Enviados

```
sent_leads table (SQLite):
┌────────────────┬──────────────┬──────────────┐
│ company_id     │ niche        │ sent_at      │
├────────────────┼──────────────┼──────────────┤
│ 1              │ veterinarias │ 2026-05-10...|
│ 2              │ veterinarias │ 2026-05-10...|
│ 45             │ restaurantes │ 2026-05-10...|
└────────────────┴──────────────┴──────────────┘

Previene:
✓ Duplicados (mismo lead enviado 2x)
✓ Pérdida de tracking entre reinicios
✓ Conflictos entre nichos
```

---

## WebSocket para Tiempo Real

### Eventos

```
Frontend → Backend:
  { "type": "get_status" }
  { "type": "get_next_lead", "niche": "veterinarias" }

Backend → Frontend (Broadcast):
  { 
    "type": "scraper_started",
    "niches": ["veterinarias"],
    "timestamp": "2026-05-10T11:30:00"
  }
  
  {
    "type": "lead_accepted",
    "lead_id": 1,
    "niche": "veterinarias",
    "status": {...}
  }
  
  {
    "type": "status_update",
    "data": {
      "niches": {
        "veterinarias": {
          "target": 50,
          "sent": 25,
          "queued": 20
        }
      }
    }
  }
```

### Conexión

```javascript
// Frontend conecta automáticamente cuando scraping=true
const ws = new WebSocket('ws://localhost:8000/api/scraper/ws')

// Recibe actualizaciones en tiempo real
// No necesita refresh manual
// Dashboard siempre sincronizado
```

---

## Endpoints API

### POST /api/scraper/start
**Inicia scraper con parámetros**

Request:
```json
{
  "niches": ["veterinarias", "restaurantes"],
  "target_count": 50,
  "min_category": "C",
  "max_concurrent": 3
}
```

Response:
```json
{
  "success": true,
  "message": "Scraper iniciado para 2 nicho(s)",
  "niches": ["veterinarias", "restaurantes"],
  "target_count": 50
}
```

---

### POST /api/scraper/submit-leads
**Backend envía leads nuevos (solo no duplicados)**

Request:
```json
{
  "niche": "veterinarias",
  "leads": [
    {
      "id": 1,
      "name": "Clínica X",
      "phone": "3001234567",
      "website": "www.x.com",
      "address": "Cll 10",
      "city": "bogota"
    }
  ]
}
```

Response:
```json
{
  "added": 5,
  "duplicates": 2,
  "queued": 47
}
```

---

### GET /api/scraper/next-lead?niche=veterinarias
**Frontend solicita siguiente lead**

Response:
```json
{
  "success": true,
  "lead": {
    "id": 1,
    "name": "Clínica Veterinaria X",
    "phone": "3001234567",
    "website": "www.x.com",
    "city": "bogota",
    "score": 92,
    "category": "A",
    "scoring_details": {
      "name": 10,
      "phone": 25,
      "website": 25,
      "address": 20,
      "email": 0,
      "company_size": 5,
      "active_status": 5
    }
  },
  "queue_status": {
    "niche": "veterinarias",
    "remaining": 45,
    "target": 50,
    "sent": 5
  }
}
```

---

### POST /api/scraper/accept-lead/{lead_id}?niche=veterinarias
**Marca lead como aceptado**

Response:
```json
{
  "success": true,
  "lead_id": 1,
  "niche": "veterinarias"
}
```

---

### GET /api/scraper/status?niche=veterinarias
**Obtiene estado**

Response:
```json
{
  "status": "processing",
  "target": 50,
  "sent": 25,
  "queued": 20,
  "started_at": "2026-05-10T11:30:00",
  "last_update": "2026-05-10T11:35:45"
}
```

---

## Configuración

### Backend (.env)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
SQLITE_DB=appdb.sqlite
HEADLESS=True
APP_DB_PATH=./appdb.sqlite
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Ejecución

### Iniciar Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Iniciar Frontend
```bash
cd frontend
npm install
npm run dev
```

### Iniciar Scraper
```bash
cd backend
python scripts/run_scraper_maestro.py
```

---

## Flujo Completo del Usuario

```
1. Usuario abre Frontend (http://localhost:3000)
   ↓
2. Ve página de Leads con configuración
   ↓
3. Selecciona:
   - Nichos: [veterinarias, restaurantes]
   - Target: 50 leads por nicho
   ↓
4. Hace click "Iniciar Búsqueda"
   ↓
5. Backend inicia scraper en background
   Scraper comienza a buscar y enviar leads
   ↓
6. Frontend muestra primer lead:
   - Nombre, teléfono, website, dirección
   - Puntuación: 92/100
   - Categoría: A (verde)
   - Desglose de puntuación
   ↓
7. Usuario puede:
   - ✓ Aceptar → Se guarda, obtiene siguiente
   - ✗ Rechazar → Se descarta, obtiene siguiente
   ↓
8. Panel lateral muestra:
   - Progreso por nicho (barra de progreso)
   - Leads aceptados totales
   - Estado en tiempo real
   ↓
9. Cuando completa target en todos:
   - Se detiene automáticamente
   - Muestra historial de leads aceptados
   ↓
10. Usuario puede exportar/ver leads completos
```

---

## Características Destacadas

✅ **Scoring Inteligente**
- Múltiples criterios evaluados
- Ponderación equilibrada
- Categorías claras A/B/C

✅ **Tiempo Real**
- WebSocket para actualizaciones
- Sin necesidad de refresh
- Dashboard siempre sincronizado

✅ **Gestión de Colas**
- Múltiples nichos simultáneamente
- Tracking de enviados
- Prevención de duplicados

✅ **Interfaz Limpia**
- Diseño intuitivo
- Indicadores visuales
- Progreso claro

✅ **Scalable**
- Arquitectura modular
- Fácil de extender
- Soporta muchos nichos
