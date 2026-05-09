# GUÍA: Descargar e Instalar ChromeDriver

## Opción 1: Descargar Manualmente

1. **Ve a:** https://chromedriver.chromium.org/

2. **Descarga la versión que coincida con tu navegador Chrome**
   - Abre Chrome → Menú (⋮) → Ayuda → Acerca de Google Chrome
   - Verifica tu versión (ej: 127.0.6533.120)

3. **Descarga ChromeDriver correspondiente:**
   - Busca la versión que coincida
   - Descargar `.zip`
   - Extraer `chromedriver-win64/chromedriver.exe`

4. **Coloca en tu proyecto:**
```
phylloleads/
├── backend/
│   ├── chromedriver.exe  ← Aquí!
│   ├── main.py
│   ├── google_maps_scraper_combined.py
│   └── ...
└── frontend/
```

5. **Verifica que funciona:**
```bash
cd backend
.\chromedriver.exe --version
```

---

## Opción 2: Descargar desde CMD PowerShell (si tienes conexión)

```powershell
# 1. Ve a la carpeta del proyecto
cd c:\Users\davir\OneDrive\Documentos\proyectos\phylloleads\backend

# 2. Descargar (reemplaza VERSION con tu versión de Chrome)
$url = "https://edgedl.me.chromium.org/edgedl/chrome/chrome-win64/127.0.6533.120/chromedriver-win64.zip"
Invoke-WebRequest -Uri $url -OutFile chromedriver.zip

# 3. Extraer
Expand-Archive chromedriver.zip -DestinationPath .
Move-Item -Path ".\chromedriver-win64\chromedriver.exe" -Destination ".\" -Force

# 4. Limpiar
Remove-Item chromedriver.zip
Remove-Item chromedriver-win64 -Recurse -Force

# 5. Verificar
.\chromedriver.exe --version
```

---

## Opción 3: Usar sin ChromeDriver (ACTUAL)

Tenemos 3 opciones funcionando:

### A. **Datos Mock en BD** (Sin scraping real)
```bash
python ver_empresas_con_detalles.py
# Muestra 5 empresas con datos simulados
# LISTO PARA USAR EN FRONTEND
```

### B. **Scraper Mejorado** (Requiere internet)
```bash
python google_maps_scraper_improved.py
# Busca en Páginas Amarillas, Dato360, Google Maps
# SIN necesidad de ChromeDriver
```

### C. **Usar Google Maps API** (Costo: $7/1000 búsquedas)
```python
from google.maps import places_api
# Más efectivo pero requiere pago
```

---

## Una vez tengas ChromeDriver

### Actualizar scraper para usar Selenium:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def __init__(self):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    self.driver = webdriver.Chrome('./chromedriver.exe', options=options)

def search_with_selenium(self, company_name, city):
    self.driver.get(f"https://www.google.com/maps/search/{company_name}+{city}")
    # ... extraer datos del DOM de Maps
```

---

## Status Actual

✅ **COMPLETADO:**
- La República scraper → 6 empresas en BD
- Búsqueda combinada → Código listo
- API REST → 5 endpoints disponibles
- Datos mock → En uso (80% completitud)

⏳ **BLOQUEADO POR:**
- Sin conexión a internet para descargar ChromeDriver
- Directorios locales no accesibles

🚀 **PRÓXIMOS PASOS:**
1. Descargar ChromeDriver manualmente (Ver arriba)
2. Ejecutar scraper real
3. Llenar BD con datos verdaderos
4. Usar en frontend

---

## Troubleshooting

**Error: "chromedriver not found"**
```bash
# Verifica que está en la carpeta correcta
Get-ChildItem -Name chromedriver.exe
```

**Error: "Version mismatch"**
```bash
# ChromeDriver version debe coincidir con Chrome
chrome.exe --version
.\chromedriver.exe --version
```

**Error: "Permission denied"**
```bash
# Dale permisos de ejecución
Unblock-File -Path ".\chromedriver.exe"
```
