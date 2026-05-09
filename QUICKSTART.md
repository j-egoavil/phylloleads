# 🚀 GUÍA DE INICIO RÁPIDO

## ¿Qué se ha creado?

Un scraper completo para **empresas.larepublica.co** con:

✅ **Backend (Python):**
- `scraper_la_republica.py` - Scraper principal (Selenium + BeautifulSoup + PostgreSQL)
- `main.py` - API REST con FastAPI
- `examples.py` - Ejemplos interactivos de uso
- `requirements.txt` - Dependencias Python
- `Dockerfile` - Contenedor para backend

✅ **Frontend (JavaScript/React):**
- `FRONTEND_INTEGRATION.js` - Componentes React listos para usar
- Ejemplos de integración
- Servicio HTTP reutilizable

✅ **Base de Datos:**
- Tablas PostgreSQL (companies, search_logs)
- Manejo automático de duplicados
- Indexación optimizada

---

## 🏃 Inicio Rápido (5 minutos)

### Opción 1: Con Docker (Recomendado)
```bash
# En la raíz del proyecto
docker-compose up --build

# Esperar que inicie (1-2 minutos)
# API disponible en: http://localhost:8000
```

### Opción 2: Local (Sin Docker)

```bash
# 1. Instalar PostgreSQL
# 2. Crear base de datos
createdb appdb

# 3. Instalar dependencias Python
cd backend
pip install -r requirements.txt

# 4. Iniciar servidor
python main.py
```

---

## 📡 Primeras Búsquedas

### Por Terminal (Pruebas rápidas)
```bash
cd backend

# Una página
python scraper_la_republica.py "veterinarias"

# Múltiples páginas
python scraper_la_republica.py "restaurantes" 3

# Ejemplos interactivos
python examples.py
```

### Por API REST (Curl)
```bash
# Búsqueda básica
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"niche": "veterinarias", "pages": 1}'

# Ver resultados guardados
curl http://localhost:8000/api/companies/veterinarias

# Estadísticas
curl http://localhost:8000/api/stats

# Docs interactiva
# Abre en navegador: http://localhost:8000/docs
```

### Desde Frontend (JavaScript)
```javascript
import { scraperService } from './FRONTEND_INTEGRATION';

// Búsqueda rápida
const result = await scraperService.searchCompanies('veterinarias', 1);
console.log(`Encontradas ${result.total_companies} empresas`);

// Obtener resultados guardados
const companies = await scraperService.getCompaniesByNiche('veterinarias');
console.log(companies);

// Estadísticas
const stats = await scraperService.getStatistics();
console.log(stats);
```

---

## 🎯 Lo que Extrae

Para cada empresa:

```json
{
  "name": "JAH PET CLINICA VETERINARIA S.A.S.",
  "url": "https://empresas.larepublica.co/colombia/bolivar/cartagena/...",
  "rues": "901531076",
  "city": "cartagena",
  "is_active": true,
  "status": "Activa",
  "company_size": "Pequeña",
  "search_niche": "veterinarias",
  "scraped_at": "2024-05-09T10:30:00"
}
```

---

## 📊 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/search` | Búsqueda sincrónica (espera resultado) |
| POST | `/api/search-async` | Búsqueda asincrónica (background) |
| GET | `/api/companies/{niche}` | Obtener empresas guardadas |
| GET | `/api/stats` | Estadísticas generales |
| GET | `/health` | Health check |

---

## 🔍 Nichos Populares para Probar

- `veterinarias`
- `restaurantes`
- `farmacias`
- `peluquerías`
- `hoteles`
- `cafeterías`
- `supermercados`
- `librerías`
- `gyms`
- `dentistas`

---

## ⚙️ Configuración

### Variables de Entorno (`.env`)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
DB_USER=postgres
DB_PASSWORD=postgres
API_HOST=0.0.0.0
API_PORT=8000
HEADLESS_MODE=true
```

---

## 🚨 Problemas Comunes

### "No se conecta a PostgreSQL"
```bash
# Verificar que PostgreSQL esté corriendo
# Si usas Docker:
docker-compose up -d db
```

### "Chrome no encontrado"
```bash
# Instalar Chromium
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install chromium

# Windows
# Usar Docker o instalar Chrome desde google.com/chrome
```

### "Timeout en búsqueda"
- El servidor está saturado
- Usar menos páginas
- O usar `/api/search-async` para búsquedas largas

---

## 📚 Documentación Completa

- `README.md` - Documentación completa de API
- `backend/examples.py` - 7 ejemplos de uso
- `FRONTEND_INTEGRATION.js` - Componentes React
- `docker-compose.yaml` - Stack completo

---

## 🔄 Flujo de Datos

```
Frontend (React)
       ↓
API REST (FastAPI)
       ↓
Scraper (Selenium)
       ↓
Website (empresas.larepublica.co)
       ↓
Parser (BeautifulSoup)
       ↓
Base de Datos (PostgreSQL)
       ↓
Frontend (Mostrar resultados)
```

---

## 💡 Tips

✅ **Para búsquedas largas:** Usa `/api/search-async`
✅ **Para scrapear múltiples nichos:** Usa `examples.py` opción 3
✅ **Para exportar datos:** Usa opción 5 en `examples.py`
✅ **Respeta el servidor:** El scraper ya tiene delays incluidos

---

## 🎓 Próximos Pasos

1. ✅ Probar con Docker Compose
2. ✅ Hacer primera búsqueda (`veterinarias`)
3. ✅ Integrar en frontend React
4. ✅ Agregar filtros (ciudad, tamaño, estado)
5. ⏳ Agregar autenticación
6. ⏳ Agregar caché de resultados
7. ⏳ Exportar a CSV/Excel

---

## 📞 Necesitas Ayuda?

Revisa:
- Docs de API: http://localhost:8000/docs
- `examples.py`: Ejecuta ejemplos interactivos
- `README.md`: Guía completa
- `FRONTEND_INTEGRATION.js`: Código de React

---

**¡Listo para empezar!** 🎉

```bash
# Solo ejecuta esto:
docker-compose up --build
```

Luego abre: http://localhost:8000/docs

