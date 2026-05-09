# 🚀 GUÍA RÁPIDA - Scraper Automático

## ⚡ 3 Formas de Ejecutar (Elige 1)

### **FORMA 1: Menu Interactivo (FÁCIL)**
```bash
cd backend
python menu.py
```
Selecciona opción y listo ✓

---

### **FORMA 2: Terminal Directa (RÁPIDO)**  
```bash
cd backend
python run_scraper_maestro.py
```
Ejecuta todo automáticamente ✓

---

### **FORMA 3: API REST (FLEXIBLE)**
```bash
# Terminal 1: Iniciar servidor
cd backend
python -m uvicorn main:app --reload

# Terminal 2: Ejecutar scraper
curl -X POST "http://localhost:8000/api/scraper/enrich-automatic?limit=10"

# Ver status
curl "http://localhost:8000/api/scraper/status"
```

O abre: `http://localhost:8000/docs` (interfaz visual) ✓

---

## 📊 Qué Hace el Scraper

```
ENTRADA:
  • Lista de empresas (niche: "veterinarias")
  • Búsqueda en: La República Colombia

PROCESAMIENTO:
  • Extrae: Nombre, NIT, Ciudad, URL
  • Busca: Teléfono, Website, Dirección
  • Fuentes: Google Maps + DuckDuckGo + Páginas Amarillas

SALIDA:
  • Base de datos actualizada (appdb.sqlite)
  • JSON export (empresas_con_detalles.json)
  • Estadísticas (% con teléfono, website, etc)
```

---

## 📍 Archivos Importantes

```
backend/
├── run_scraper_maestro.py    ← Script maestro (forma 2)
├── menu.py                   ← Menú interactivo (forma 1)
├── main.py                   ← API FastAPI (forma 3)
├── scraper_automatico.py     ← Motor de búsqueda
├── appdb.sqlite              ← Base de datos
└── empresas_con_detalles.json ← Datos exportados
```

---

## ✅ Checklist

- [ ] Python 3.12+ instalado (`python --version`)
- [ ] Venv activado (`.\venv\Scripts\activate`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Selenium disponible (`pip install selenium --upgrade`)
- [ ] Navegador (Chrome, Edge, Firefox) instalado

---

## 📈 Resultado Esperado

Después de ejecutar (5-10 min):

```
ESTADÍSTICAS FINALES
====================
Total empresas: 6
Con teléfono:   5 (83.3%)
Con website:    5 (83.3%)
Con dirección:  5 (83.3%)
```

**Ejemplo de datos extraídos:**
```json
{
  "nombre": "CLÍNICA VETERINARIA MONTE VERDE S.A.",
  "telefono": "+57 301 5052787",
  "website": "https://clinicamonteverde.co",
  "direccion": "Centro Historico, Cartagena"
}
```

---

## 🔥 RECOMENDACIÓN

**Para empezar ahora:**

```bash
cd backend
python run_scraper_maestro.py
```

Ese comando:
✅ Ejecuta todo automáticamente  
✅ No necesita config  
✅ Genera datos en ~5 minutos  
✅ Guarda en BD + JSON  

---

## 🆘 Problemas Comunes

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: selenium` | `pip install selenium --upgrade` |
| `connection refused` | Cerrar otros procesos Python |
| "No navegador detectado" | Instalar Chrome, Edge o Firefox |
| Datos incompletos | Esperar a que termine de procesar |

---

**¿Necesitas más ayuda?** Ver `README_SCRAPER.md` para documentación completa.
