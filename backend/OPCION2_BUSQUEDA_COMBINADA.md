# OPCION 2: BUSQUEDA COMBINADA (DIY)
## Google + Paginas Amarillas + LinkedIn

---

## DIAGRAMA DE FLUJO

```
USER REQUEST: "Buscar CENTRO VETERINARIO ESPECIALIZADO BOGOTÁ en bogota"
                                    |
                    __________________+__________________
                    |                  |                  |
                    v                  v                  v
            FUENTE 1:            FUENTE 2:            FUENTE 3:
            GOOGLE SEARCH        PAGINAS AMARILLAS    LINKEDIN
                 |                    |                   |
                 v                    v                   v
            Resultados:          Resultados:          Resultados:
            - URL empresa        - TELEFONO           - Perfil empresa
            - Snippet            - WEBSITE            - VERIFICACION
            - Direccion          - DIRECCION
                 |                    |                   |
                 +____________________+___________________+
                            |
                            v
                    CONSOLIDAR DATOS
                   (Sin duplicados)
                            |
         _____________________+_____________________
         |                   |                     |
         v                   v                     v
      TELEFONO           WEBSITE              DIRECCION
    +57 1 2345678      https://vet.co     Cra 5 #10-20 Bogotá
         |                   |                     |
         +___________________+_____________________+
                            |
                            v
                    GUARDAR EN BD
                (company_details table)
```

---

## PASO 1: BUSQUEDA EN GOOGLE (requests + BeautifulSoup)

```python
search_query = "CENTRO VETERINARIO ESPECIALIZADO BOGOTÁ bogota telefono"

URL: https://duckduckgo.com/?q=<query>
     (usamos DuckDuckGo porque no requiere API)

Resultado HTML:
  <a href="https://example.com/vet">
    CENTRO VETERINARIO ESPECIALIZADO BOGOTÁ
  </a>
  <span>Telefono: +57 1 2345678</span>
  <span>Cra 5 #10-20 Bogotá</span>
```

**Ventaja**: Rapido, datos de multiples sitios  
**Desventaja**: Google puede bloquear requests agresivos  

---

## PASO 2: PAGINAS AMARILLAS COLOMBIA

```python
URL: https://www.paginasamarillas.com.co/search?q=...

Estructura de resultados:
  <div class="business-item">
    <span class="phone">+57 1 2345678</span>
    <a class="website" href="https://vet.co">vet.co</a>
    <span class="address">Cra 5 #10-20 Bogotá</span>
  </div>

Extraemos:
  - TELEFONO: +57 1 2345678
  - WEBSITE: https://vet.co
  - DIRECCION: Cra 5 #10-20 Bogotá
```

**Ventaja**: Especializado en Colombia  
**Desventaja**: No todas las empresas tienen datos completos  

---

## PASO 3: VERIFICACION EN LINKEDIN

```python
URL: site:linkedin.com/company <empresa>

Busca en Google/DuckDuckGo:
  site:linkedin.com/company "CENTRO VETERINARIO"

Resultado:
  https://linkedin.com/company/centro-veterinario-especializado

Ventaja: Verifica que la empresa EXISTE realmente
```

---

## CONSOLIDACION DE DATOS

```
FUENTE 1 (Google):
  - TELEFONO: +57 1 2345678
  - DIRECCION: Cra 5 #10-20
  - WEBSITE: (no encontrado)

FUENTE 2 (Paginas Amarillas):
  - TELEFONO: +57 1 2345678 (IGUAL)
  - WEBSITE: https://vet.co
  - DIRECCION: Cra 5 #10-20 Bogotá

FUENTE 3 (LinkedIn):
  - VERIFICACION: OK (empresa existe)

RESULTADO FINAL:
  {
    "phone": "+57 1 2345678",
    "website": "https://vet.co",
    "address": "Cra 5 #10-20 Bogotá",
    "verified": true,
    "sources": ["google", "paginas_amarillas", "linkedin"]
  }
```

---

## COMPARACION DE LAS 3 OPCIONES

```
                    OPCION 1       OPCION 2         OPCION 3
                   (API Google)   (Combinada)    (Selenium)
                   
COSTO              $7/1000        $0              $0
VELOCIDAD          <1s/empresa    10-15s          5-10s
PRECISION          99%            75-85%          80%
COMPLEJIDAD        Facil          Media           Media
DEPENDENCIAS       API Key        requests        ChromeDriver
BLOQUEOS           Bajo           Medio           Alto
DATOS              Exactos        Aproximados     Aproximados
VERIFICACION       Si             Parcial         No

RECOMENDACION      Production     Desarrollo      Dev/Testing
```

---

## VENTAJAS DE OPCION 2

✅ **SIN COSTO**: No requiere APIs de pago  
✅ **SIN DEPENDENCIAS COMPLEJAS**: Solo requests y BeautifulSoup  
✅ **MULTIPLES FUENTES**: Aumenta precision combinando datos  
✅ **VERIFICACION**: Confirm en LinkedIn que empresa existe  
✅ **FLEXIBLE**: Agregar mas fuentes facilmente  
✅ **RAPIDO DE IMPLEMENTAR**: Ya tenemos el codigo  

---

## DESVENTAJAS DE OPCION 2

❌ **MAS LENTO**: 10-15 segundos por empresa  
❌ **RIESGO DE BLOQUEO**: Google/DuckDuckGo pueden bloquear  
❌ **DATOS INCOMPLETOS**: A veces faltan datos  
❌ **DEPENDENCIA DE SITIOS EXTERNOS**: Si cambian HTML, falla  
❌ **NECESITA DELAYS**: Para no bloquarse (2 segundos entre requests)  

---

## IMPLEMENTACION

```python
scraper = CombinedMapsScraper()

# Buscar 5 empresas
scraper.process_companies(limit=5)

# Resultado por empresa:
# 1. CENTRO VETERINARIO ESPECAIZADO BOGOTA
#    BUSCANDO EN: google, paginas_amarillas, linkedin
#    Telefono: +57 1 2345678
#    Website: https://vet.co
#    Direccion: Cra 5 #10-20 Bogota
#    Fuentes: google, paginas_amarillas, linkedin
#    GUARDADO EN BD
```

---

## PROXIMOS PASOS

1. Ejecutar scraper (comienza a buscar en multiples fuentes)
2. Datos se guardan en BD automaticamente
3. Verificar tabla company_details con datos completos
4. Crear API endpoint para mostrar datos combinados
5. (Opcional) Agregar mas fuentes: Tripadvisor, Google My Business, etc.

---

## ARCHIVOS GENERADOS

- `google_maps_scraper_combined.py`: Scraper con busqueda combinada
- Datos guardados en: `appdb.sqlite` (tabla company_details)

---
