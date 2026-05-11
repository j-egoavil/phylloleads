# 🔍 Auditoría de API - Frontend & Backend

**Fecha:** 10/05/2026  
**Estado:** ⚠️ Se encontraron 7 problemas críticos y 5 de menor importancia

---

## 🔴 PROBLEMAS CRÍTICOS

### 1. **Mismatch de campos en Lead (leads.$id.tsx)**
- **Localización:** `frontend/src/routes/leads.$id.tsx`, línea 70
- **Problema:** El componente intenta acceder a `lead.company` y `lead.source`
- **Realidad:** El backend devuelve `lead.name` (no `lead.company`) y `lead.niche` (no `lead.source`)
- **Impacto:** 🔴 CRÍTICO - La página de detalles crasheará
- **Solución requerida:**
```typescript
// ❌ ACTUAL (línea 70)
<p className="text-muted-foreground mt-1">{lead.name}</p>
<div className="text-xs uppercase...">{SOURCE_LABELS[lead.source]}</div>

// ✅ DEBE SER
<p className="text-muted-foreground mt-1">{lead.company}</p> // ← lead.company no existe
<div className="text-xs uppercase...">{NICHE_LABELS[lead.niche]}</div> // ← usar niche
```

---

### 2. **Falta de manejo de WebSocket en useLeadScraper**
- **Localización:** `frontend/src/hooks/useLeadScraper.js`, línea 28
- **Problema:** El WebSocket se conecta a `/api/scraper/ws` pero:
  - El URL está hardcodeado y no usa `API_URL`
  - No hay reintentos de conexión si falla
  - No hay heartbeat para mantener la conexión viva
- **Impacto:** 🔴 CRÍTICO - La conexión WebSocket puede caerse sin notificación
- **Solución requerida:**
```javascript
// Línea 28 - Usar API_URL correctamente
const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
const wsUrl = `${protocol}://${window.location.host}/api/scraper/ws` // ← Correcto

// Pero mejor:
const apiUrlParts = new URL(API_URL)
const wsProtocol = apiUrlParts.protocol === 'https:' ? 'wss' : 'ws'
const wsUrl = `${wsProtocol}//${apiUrlParts.host}/api/scraper/ws`

// Agregar heartbeat
ws.onopen = () => {
  setInterval(() => ws.send(JSON.stringify({ type: 'ping' })), 30000)
}
```

---

### 3. **Inconsistencia en query parameters - accept-lead**
- **Localización:** `frontend/src/hooks/useLeadScraper.js`, línea 107
- **Problema:** Envía `niche` como query param pero el backend lo espera como parámetro POST
- **Backend espera:**
```python
@router.post("/accept-lead/{lead_id}")
async def accept_lead(lead_id: int, niche: str):  # ← niche debe estar en body o query
```
- **Frontend envía:**
```javascript
fetch(`${API_URL}/api/scraper/accept-lead/${leadId}?niche=${niche}`, { method: 'POST' })
```
- **Impacto:** 🔴 CRÍTICO - El backend no recibirá el parámetro `niche` correctamente
- **Solución:**
```javascript
// Cambiar a:
fetch(`${API_URL}/api/scraper/accept-lead/${leadId}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ niche })
})

// O en backend, cambiar a:
@router.post("/accept-lead/{lead_id}")
async def accept_lead(lead_id: int, niche: str = Query(...)):
  # Aceptar como query param
```

---

### 4. **Falta de error handling para respuestas no-JSON**
- **Localización:** `frontend/src/hooks/useLeadScraper.js`, múltiples líneas
- **Problema:** No se valida que `response.json()` sea válido
- **Escenario:** Si el backend devuelve HTML error (500), el frontend crashea
- **Impacto:** 🔴 CRÍTICO - Los errores del servidor no se manejan correctamente
- **Solución requerida:**
```javascript
// Agregar a TODOS los fetch:
const getNextLead = useCallback(async () => {
  try {
    const response = await fetch(`${API_URL}/api/scraper/next-lead`)
    
    if (!response.ok) {
      const contentType = response.headers.get('content-type')
      let errorData
      if (contentType?.includes('application/json')) {
        errorData = await response.json()
        throw new Error(errorData.detail || `Error ${response.status}`)
      } else {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`)
      }
    }
    
    const data = await response.json()
    // ... resto del código
  } catch (err) {
    setError(err.message)
  }
}, [])
```

---

### 5. **Confusión entre source_niche en BD vs API**
- **Localización:** `backend/app/routes/scraper.py` y BD
- **Problema:** 
  - La BD guarda `search_niche`
  - El frontend envía `niches` en array
  - El API devuelve `niche` singular
  - Frontend espera `source` (que no existe)
- **Impacto:** 🔴 CRÍTICO - Inconsistencia de nombrado
- **Solución:**
```python
# backend/app/routes/scraper.py - Unificar nomenclatura
class StartScraperRequest(BaseModel):
    niches: List[str]  # ✅ Correcto
    target_count: int
    min_category: str = 'C'

# En respuestas:
"lead": {
    "niche": niche,  # ✅ Usar "niche" consistentemente
    # NO "source" o "search_niche"
}
```

---

### 6. **Falta de validación de tipo en POST /submit-leads**
- **Localización:** `backend/app/routes/scraper.py`, línea 88
- **Problema:** El endpoint no tiene modelo Pydantic, recibe `niche` y `leads` como parámetros sueltos
- **Frontend NO LO LLAMA**, pero si lo hiciera fallaría
- **Impacto:** 🔴 CRÍTICO - Endpoint vulnerable a malformed requests
- **Solución:**
```python
class SubmitLeadsRequest(BaseModel):
    niche: str
    leads: List[dict]

@router.post("/submit-leads")
async def submit_leads(request: SubmitLeadsRequest):
    niche = request.niche
    leads = request.leads
    # ... resto
```

---

### 7. **CORS y protocolos en WebSocket confundidos**
- **Localización:** `frontend/src/hooks/useLeadScraper.js`, línea 28
- **Problema:** 
  - Frontend usa `window.location.host` que puede ser `localhost:5173`
  - Pero API está en `localhost:8000`
  - El WebSocket intenta conectar a puerto incorrecto
- **Impacto:** 🔴 CRÍTICO - WebSocket fallará 100% del tiempo
- **Solución:**
```javascript
// ❌ ACTUAL (INCORRECTO)
const wsUrl = `${protocol}://${window.location.host}/api/scraper/ws`
// Esto genera: ws://localhost:5173/api/scraper/ws ← PUERTO INCORRECTO

// ✅ CORRECTO
const apiUrl = new URL(API_URL)
const wsUrl = `${wsProtocol}://${apiUrl.host}/api/scraper/ws`
// Esto genera: ws://localhost:8000/api/scraper/ws ✓
```

---

## 🟡 PROBLEMAS DE MENOR IMPORTANCIA

### 8. **No hay try-catch en requestStatus()**
- **Línea:** `frontend/src/hooks/useLeadScraper.js`, línea 149
- **Problema:** Los errores se consolean pero no se setean en estado
- **Severidad:** MEDIA

### 9. **Falta de tipos en useLeadScraper.js**
- **Línea:** Todo el archivo
- **Problema:** No hay tipos TypeScript, debería ser `.ts`
- **Severidad:** BAJA (funcional pero no safe)

### 10. **No se valida `target_count` en frontend**
- **Línea:** `frontend/src/routes/leads.tsx`, línea 93
- **Problema:** El slider permite 10-500 pero no valida server-side
- **Severidad:** BAJA (backend tiene validación)

### 11. **Falta de loading state durante submit**
- **Localización:** `frontend/src/routes/leads.tsx`
- **Problema:** El botón no desactiva durante POST, permite duplicados
- **Severidad:** MEDIA

### 12. **No hay reintentos en fetch fallidos**
- **Localización:** `frontend/src/hooks/useLeadScraper.js`
- **Problema:** Un error de red detiene todo, sin reintentos
- **Severidad:** MEDIA

---

## 📋 CHECKLIST DE CORRECCIONES PRIORITARIAS

- [ ] **P1:** Cambiar `leads.$id.tsx` - Usar `lead.niche` en lugar de `lead.source`
- [ ] **P1:** Corregir WebSocket URL para usar `API_URL` correctamente
- [ ] **P1:** Arreglar query param `niche` en `/accept-lead` endpoint
- [ ] **P1:** Agregar error handling en todos los fetch
- [ ] **P2:** Unificar nomenclatura niche/source en API
- [ ] **P2:** Agregar Pydantic model a `/submit-leads`
- [ ] **P3:** Convertir `useLeadScraper.js` a TypeScript
- [ ] **P3:** Agregar reintentos y heartbeat a WebSocket

---

## 🧪 TEST DE INTEGRACIÓN SUGERIDO

```bash
# 1. Verificar que WebSocket se conecta correctamente
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/api/scraper/ws

# 2. Verificar inicio de scraper
curl -X POST http://localhost:8000/api/scraper/start \
  -H "Content-Type: application/json" \
  -d '{"niches": ["restaurantes"], "target_count": 10}'

# 3. Obtener siguiente lead
curl http://localhost:8000/api/scraper/next-lead

# 4. Aceptar lead (con correcciones)
curl -X POST http://localhost:8000/api/scraper/accept-lead/1 \
  -H "Content-Type: application/json" \
  -d '{"niche": "restaurantes"}'
```

---

## 📊 RESUMEN

| Categoría | Cantidad | Estado |
|-----------|----------|--------|
| 🔴 Críticos | 7 | ⚠️ Requiere fix inmediato |
| 🟡 Medios | 3 | ⚠️ Arreglar antes de producción |
| 🟢 Bajos | 2 | ℹ️ Mejoría de código |

**Recomendación:** No lanzar a producción hasta que se corrijan los 7 problemas críticos.
