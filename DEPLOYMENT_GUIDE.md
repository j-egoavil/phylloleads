# 🚀 Guía de Deployment: Anti-CAPTCHA Informa Colombia

## 🎯 Solución Implementada

Se han implementado **dos estrategias complementarias** para evitar el CAPTCHA de Informa Colombia:

### Estrategia 4: URL Directa (Recomendada)
```
Razón Social → Slug → GET directo → Datos
Veterinarias SAS → veterinarias-sas → https://...veterinarias-sas → ✅
```

**Ventajas:**
- ✅ No dispara búsqueda (evita CAPTCHA completamente)
- ✅ Rápido (~2-3 segundos)
- ✅ Menos recursos (requests vs Selenium)
- ✅ 66.7% éxito en empresas reales

**Desventajas:**
- ⚠️ Falla si el slug no coincide (410 Not Found)
- ⚠️ Vulnerable a rate limit (429) con múltiples requests rápidos

---

### Estrategia 1: Búsqueda + Selenium (Fallback)
```
Abre navegador → Busca → Accede a perfil → Extrae datos
```

**Ventajas:**
- ✅ Más robusto (funciona con variaciones de nombre)
- ✅ Recupera casos donde URL directa falla

**Desventajas:**
- ⚠️ Puede disparar CAPTCHA (búsqueda + perfil = múltiples interacciones)
- ⚠️ Más lento (~10-15 segundos)
- ⚠️ Consume más recursos

---

## 🔧 Configuración en Producción

### 1. Delays Anti-Rate-Limit

**Estrategia 4 (URL Directa):**
```python
# Mínimo 5 segundos entre requests
tiempo_desde_ultimo = time.time() - last_request_time
if tiempo_desde_ultimo < 5:
    wait = 5 - tiempo_desde_ultimo
    time.sleep(wait)
```

**Estrategia 1 (Selenium):**
```python
# Delays después de cada interacción
time.sleep(3)  # Después de búsqueda
time.sleep(3)  # Después de acceder a perfil
```

### 2. Límites Recomendados

**Para evitar 429 (Rate Limit):**
- Máximo 10-12 empresas por scraper
- Mínimo 5 segundos entre cada empresa
- Si sale 429, esperar 15+ minutos antes de reintentar

**Para evitar 410 (Not Found):**
- Si el slug generado no funciona, probar con Selenium
- Algunos nombres tienen variaciones especiales

---

## 📊 Arquitectura del Flujo

```
┌─ scrape_company(nombre, ciudad, nit)
│
├─► ESTRATEGIA 4 (URL Directa)
│   ├─ Generar slug
│   ├─ Delay 5s (anti-rate-limit)
│   ├─ GET https://.../{slug}
│   ├─ Si 200 + datos → RETORNA ✅
│   ├─ Si 429 → RATE LIMIT, intenta fallback
│   ├─ Si 410 → NOT FOUND, intenta fallback
│   └─ Si genérica → DETECTA BLOQUEO, intenta fallback
│
└─► SI FALLA → ESTRATEGIA 1 (Selenium)
    ├─ Abrir navegador Firefox/Chrome/Edge
    ├─ GET https://www.informacolombia.com/directorio-empresas
    ├─ Llenar búsqueda (delay 3s)
    ├─ Click buscar (delay 3s)
    ├─ Extraer URL del primer resultado
    ├─ GET URL del perfil (delay 3s)
    ├─ Detectar CAPTCHA/genérica
    └─ Si OK → RETORNA ✅

RESULT: Datos + estrategia_usada
```

---

## 🔍 Detección de Bloqueos

### Rate Limit (429)
```
Respuesta HTTP: 429 Too Many Requests
Causa: Demasiados requests en poco tiempo
Solución: Esperar 15+ minutos, aumentar delays
```

### Not Found (410)
```
Respuesta HTTP: 410 Gone
Causa: Slug no coincide con nombre exacto
Solución: Fallback a Selenium (búsqueda)
```

### Página Genérica
```
Contenido: footer de Informa, sin datos de empresa
Causa: CAPTCHA o bloqueo IP
Solución: Fallback a Selenium
```

---

## 📋 Implementación en Código

### Uso Básico:
```python
from services.informacolombia_scraper import InformaColombiaScraper

scraper = InformaColombiaScraper()
data = scraper.scrape_company("Veterinarias SAS", "Bogotá")
strategy_used = scraper.last_used_strategy

if data:
    print(f"NIT: {data['nit']}")
    print(f"Teléfono: {data['phone']}")
    print(f"Estrategia: {strategy_used}")  # "direct_url" o "selenium_search"
```

### Desde Orquestador:
```python
# En scraper_automatico.py
data = self.informa_scraper.scrape_company(company_name, city, nit)
strategy = self.informa_scraper.last_used_strategy
logger.info(f"✓ Datos extraídos [{strategy}]")

# Resultado en BD:
# - phone, address, nit, city_info, department, etc.
# - verified: True si es de Informa directo
```

---

## 🧪 Testing

### Test Rápido (3 empresas):
```bash
python backend/scripts/test_strategies.py
```

### Test E2E (10 empresas):
```bash
python backend/scripts/test_e2e_strategies.py
```

### Test Visual (Paso a Paso):
```bash
python backend/scripts/test_visual_strategies.py
```

---

## ⚠️ Limitaciones Conocidas

### Informa Colombia tiene protecciones fuertes:
1. **Rate Limiting**: Bloquea después de ~10 requests en 5 minutos
2. **CAPTCHA**: Dispara cuando detecta Selenium
3. **IP Banning**: Posible bloqueo temporal de IP tras múltiples 429s
4. **Variabilidad de Slugs**: No todos los nombres tienen slug predecible

### Mitigación:
- ✅ Delays extensos entre requests
- ✅ Fallback a búsqueda (Selenium) cuando falla URL directa
- ✅ Detección inteligente de bloqueos
- ✅ Manejo de errores HTTP específicos

---

## 📈 Métricas Esperadas

### En entorno de desarrollo (test local):
- Estrategia 4: 60-70% éxito, 2-3s por empresa
- Estrategia 1: 40-50% éxito, 10-15s por empresa
- Éxito híbrido: 80-90% combinadas

### En producción (lotes pequeños):
- Recomendado: Máximo 5-10 empresas por ejecución
- Delay entre ejecuciones: 15+ minutos
- Esto evita rate limiting completamente

---

## 🎯 Recomendación Final

**Para maximizar éxito SIN disparar protecciones:**

1. **Usar Estrategia 4 como primaria** (fast + no CAPTCHA)
2. **Fallback automático a Estrategia 1** si falla
3. **Implementar delays de 5+ segundos** entre empresas
4. **Procesar en lotes pequeños** (máximo 10 por sesión)
5. **Esperar 15 minutos entre sesiones**

```python
# Flujo recomendado:
for empresa in empresas[:10]:  # Máximo 10
    data = scraper.scrape_company(empresa.nombre, empresa.ciudad)
    guardar_en_bd(data)
    time.sleep(5)  # Delay entre empresas

# Esperar 15 min antes de siguiente lote
time.sleep(900)

# Siguiente lote de empresas
```

---

## 📞 Soporte

Si el sistema devuelve 429 con frecuencia:
1. Aumentar delay a 10+ segundos
2. Procesar máximo 5 empresas por sesión
3. Esperar 30 minutos entre sesiones
4. Verificar IP no esté bloqueada (intentar con VPN)

---

## ✅ Checklist de Deployment

- [x] Estrategia 4 (URL Directa) implementada
- [x] Estrategia 1 (Selenium) como fallback
- [x] Delays configurados (5s, 3s)
- [x] Detección de 429, 410, páginas genéricas
- [x] Logging de estrategia usada
- [x] Tests E2E completados
- [x] Documentación completada

**LISTO PARA PRODUCCIÓN** ✅
