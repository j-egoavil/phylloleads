# GUÍA: Instalar Opera + Usar OperaDriver

## Paso 1: Instalar Opera (si no lo tienes)

### Opción A: Descargar desde la web
1. Ve a: https://www.opera.com/es
2. Descarga e instala Opera
3. La instalación la pone automáticamente en la ruta correcta

### Opción B: Instalar desde PowerShell (con Chocolatey)
```powershell
# Si tienes Chocolatey instalado
choco install opera -y

# Si no tienes Chocolatey:
# Descarga desde: https://chocolatey.org/install
```

---

## Paso 2: Verificar que Opera esté instalado

```powershell
# Buscar Opera en el sistema
Get-ChildItem -Path "C:\Program Files" -Name "opera.exe" -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\Program Files (x86)" -Name "opera.exe" -Recurse -ErrorAction SilentlyContinue
```

---

## Paso 3: Instalar OperaDriver

```bash
# Selenium ya incluye soporte para Opera
# Solo necesitas instalar selenium si no lo tienes:
pip install selenium

# Verificar que funciona:
python -c "from selenium.webdriver.opera.options import Options; print('OperaDriver disponible')"
```

---

## Paso 4: Ejecutar el Scraper con Opera

```bash
cd c:\Users\davir\OneDrive\Documentos\proyectos\phylloleads\backend

# Ejecutar scraper
python google_maps_scraper_opera.py
```

---

## ¿Cómo funciona?

```python
from selenium import webdriver
from selenium.webdriver.opera.options import Options

# Configurar Opera
options = Options()
options.add_argument('--headless')

# Crear driver
driver = webdriver.Opera(options=options)

# Usar como Chrome (mismo motor Chromium)
driver.get("https://www.google.com/maps/search/...")
```

---

## Troubleshooting

**Error: "Opera not found"**
```
✅ Solución: Instala Opera desde https://www.opera.com/
```

**Error: "OperaDriver not found"**
```
✅ Solución: pip install selenium
```

**Error: "Permission denied"**
```
✅ Solución: Ejecuta PowerShell como Administrador
```

---

## Comparación: Chrome vs Opera vs Firefox

| Feature | Chrome | Opera | Firefox |
|---------|--------|-------|---------|
| Selenium | ✅ | ✅ | ✅ |
| Headless | ✅ | ✅ | ✅ |
| Maps | ✅ | ✅ | ✅ |
| Costo | Gratis | Gratis | Gratis |
| Instalación | Fácil | Fácil | Fácil |

**RECOMENDACIÓN:** Opera es mejor opción si ya lo tienes instalado.

---

## Próximos pasos

1. ✅ Instala Opera
2. ✅ Ejecuta: `python google_maps_scraper_opera.py`
3. ✅ Datos se guardan en BD automáticamente
4. ✅ Usa API para obtener datos

```bash
# Ver datos en API
python -m uvicorn main:app --reload
# Abre: http://localhost:8000/docs
```
