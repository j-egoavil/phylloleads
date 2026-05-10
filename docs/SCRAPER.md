# 🚀 Phylloleads - Scraper Automático

Sistema automatizado para extraer y enriquecer datos de empresas colombianas desde múltiples fuentes.

## 📋 Características

✅ **Extracción de La República** - Busca empresas por nicho  
✅ **Enriquecimiento Multi-fuente** - Google Maps + DuckDuckGo + Páginas Amarillas  
✅ **Ejecución Automática** - Sin intervención manual  
✅ **API REST** - Endpoints para ejecutar y monitorear  
✅ **Base de Datos SQLite** - Almacenamiento local

---

## 🎯 Opciones de Ejecución

### **OPCIÓN 1: Terminal (Más rápido)**

```bash
cd backend
python run_scraper_maestro.py
```

**Qué hace:**
1. ✓ Extrae empresas de La República
2. ✓ Enriquece con datos automáticos
3. ✓ Muestra estadísticas finales
4. ✓ Genera reporte

**Tiempo:** ~5-10 minutos

---

### **OPCIÓN 2: API REST (Más flexible)**

**Iniciar servidor:**
```bash
cd backend
python -m uvicorn main:app --reload
```

**Luego ejecutar scraper:**

#### a) Vía HTTP POST
```bash
curl -X POST "http://localhost:8000/api/scraper/enrich-automatic?limit=10"
```

#### b) Vía navegador
Abre: `http://localhost:8000/docs`

Click en:
1. "POST /api/scraper/enrich-automatic"
2. "Try it out"
3. "Execute"

#### c) Ver estadísticas
```bash
curl "http://localhost:8000/api/scraper/status"
```

---

### **OPCIÓN 3: Ejecución por Pasos (Depuración)**

```bash
cd backend

# Paso 1: Extraer de La República
python scraper_la_republica.py

# Paso 2: Enriquecimiento automático
python scraper_automatico.py

# Paso 3: Ver resultados
python ver_empresas_con_detalles.py
```

---

## 📊 Resultados Esperados

Después de ejecutar el scraper, verás:

```
================================================================================
ESTADÍSTICAS FINALES
================================================================================

Total empresas en BD: 6
  • Con teléfono: 5 (83.3%)
  • Con website: 5 (83.3%)
  • Con dirección: 5 (83.3%)

```

**Datos en la base de datos:**
- Teléfono: +57 301 5052787
- Website: https://clinicamonteverde.co
- Dirección: Centro Historico, Cartagena

---

## 🔧 Configuración

### Variables de Entorno
```bash
# .env (opcional)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
DB_USER=postgres
DB_PASSWORD=postgres
```

### Archivo de Configuración
```
backend/
├── appdb.sqlite         # Base de datos
├── main.py             # API FastAPI
├── scraper_la_republica.py
├── scraper_automatico.py
└── run_scraper_maestro.py
```

---

## 🌐 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verifica que API esté activa |
| POST | `/api/search` | Busca empresas en La República |
| GET | `/api/companies/{niche}` | Lista empresas por nicho |
| POST | `/api/search-async` | Búsqueda en background |
| GET | `/api/companies-with-details` | Empresas con detalles enriquecidos |
| GET | `/api/companies/{id}/details` | Detalles de una empresa |
| **POST** | **`/api/scraper/enrich-automatic`** | **Ejecuta enriquecimiento automático** |
| GET | `/api/scraper/status` | Estado del scraper |
| GET | `/api/stats` | Estadísticas generales |

---

## 📡 Ejemplo de Respuesta API

### GET /api/scraper/status

```json
{
  "success": true,
  "status": "operational",
  "statistics": {
    "total_companies": 6,
    "enriched": {
      "phone": 5,
      "website": 5,
      "address": 5
    },
    "coverage": {
      "phone": "83.3%",
      "website": "83.3%",
      "address": "83.3%"
    },
    "companies_by_niche": {
      "veterinarias": 6
    }
  }
}
```

---

## 🛠️ Troubleshooting

### "selenium.common.exceptions.WebDriverException"
```
Solución: El navegador no está disponible
→ Instalar: pip install selenium --upgrade
```

### "connection refused" (BD)
```
Solución: SQLite está bloqueado
→ Cerrar otros procesos de Python
→ Reiniciar: python run_scraper_maestro.py
```

### "Too many requests"
```
Solución: Las fuentes están bloqueando
→ Aumentar delays en scraper_automatico.py
→ Cambiar User-Agent
```

---

## 📈 Próximos Pasos

```python
# 1. Ejecutar scraper inicial
python run_scraper_maestro.py

# 2. Verificar datos
python ver_empresas_con_detalles.py

# 3. (Opcional) Corregir datos manualmente
python actualizar_datos.py

# 4. Exportar para frontend
# Los datos están en empresas_con_detalles.json
```

---

## 🔄 Actualizar Datos Regularmente

### Opción A: Vía Script
```bash
# Ejecutar diariamente
python run_scraper_maestro.py
```

### Opción B: Vía API (recomendado)
```bash
# En cron o scheduler
curl -X POST "http://localhost:8000/api/scraper/enrich-automatic?limit=20"
```

### Opción C: Docker Compose
```bash
docker-compose up -d
# Ejecutar en contenedor
docker exec phylloleads_backend python run_scraper_maestro.py
```

---

## 📝 Archivos Generados

```
backend/
├── appdb.sqlite                    # Base de datos (SQLite)
├── empresas_con_detalles.json      # JSON export
├── empresas_para_corregir.csv      # (Si se exporta)
└── logs/
    └── scraper.log                 # Logs de ejecución
```

---

## 🎓 Conceptos Principales

### Fuentes de Datos
1. **La República** - Empresa principal, NIT, ciudad
2. **Google Maps** - Teléfono, dirección, website
3. **DuckDuckGo** - Búsqueda alternativa
4. **Páginas Amarillas** - Directorios locales

### Flujo Automatizado
```
1. Buscar en La República
   ↓
2. Para cada empresa: buscar en múltiples fuentes
   ↓
3. Guardar datos en BD
   ↓
4. Generar reportes
```

---

## 🤝 Soporte

- **API Docs**: http://localhost:8000/docs
- **Logs**: Ver consola durante ejecución
- **Debug**: Activar modo verbose en scripts

---

**Última actualización**: Mayo 2026  
**Estado**: ✅ Producción
