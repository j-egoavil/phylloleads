# Scraper La República - Documentación

## Descripción
Scraper automatizado para extraer información de empresas desde **empresas.larepublica.co**

### Datos extraídos
- **Nombre** de la empresa
- **Enlace** a la empresa en el sitio
- **RUES** (número de registro)
- **Ciudad** 
- **Estado** (Activa/Inactiva)
- **Tamaño** de la empresa (Micro, Pequeña, Mediana, Grande)

---

## Instalación Local

### Requisitos
- Python 3.11+
- PostgreSQL 16
- Chrome/Chromium (para Selenium)
- Docker (opcional)

### Instalación

```bash
# 1. Clonar o descargar el proyecto
cd phylloleads/backend

# 2. Crear ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=appdb
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### Uso Directo del Script

```bash
# Búsqueda básica (1 página)
python scraper_la_republica.py "veterinarias"

# Búsqueda múltiples páginas
python scraper_la_republica.py "restaurantes" 5
```

---

## API REST

### Iniciar servidor

```bash
# Desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

---

## Endpoints

### 1. Health Check
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-05-09T10:30:00.123456"
}
```

---

### 2. Búsqueda Sincrónica (Espera resultado)
```http
POST /api/search
Content-Type: application/json

{
  "niche": "veterinarias",
  "pages": 2
}
```

**Respuesta:**
```json
{
  "success": true,
  "niche": "veterinarias",
  "total_companies": 45,
  "message": "Scrape completado: 45 empresas",
  "companies": [
    {
      "name": "JAH PET CLINICA VETERINARIA S.A.S.",
      "url": "https://empresas.larepublica.co/colombia/bolivar/cartagena/jah-pet-clinica-veterinaria-s-a-s-901531076",
      "rues": "901531076",
      "city": "cartagena",
      "is_active": true,
      "status": "Activa",
      "company_size": "Pequeña",
      "search_niche": "veterinarias",
      "scraped_at": "2024-05-09T10:30:00.123456"
    }
    // ... más empresas
  ]
}
```

---

### 3. Búsqueda Asincrónica (Background)
```http
POST /api/search-async
Content-Type: application/json

{
  "niche": "restaurantes",
  "pages": 5
}
```

**Respuesta (inmediata):**
```json
{
  "success": true,
  "message": "Búsqueda de 'restaurantes' iniciada en background",
  "niche": "restaurantes",
  "status": "processing"
}
```
⚠️ **Nota:** La búsqueda continúa en background. Use el endpoint `/api/companies/{niche}` para consultar resultados.

---

### 4. Obtener Empresas por Nicho
```http
GET /api/companies/veterinarias?limit=50
```

**Respuesta:**
```json
{
  "success": true,
  "niche": "veterinarias",
  "total": 45,
  "companies": [
    {
      "id": 1,
      "name": "JAH PET CLINICA VETERINARIA S.A.S.",
      "url": "https://empresas.larepublica.co/...",
      "rues": "901531076",
      "city": "cartagena",
      "is_active": true,
      "status": "Activa",
      "company_size": "Pequeña",
      "search_niche": "veterinarias",
      "scraped_at": "2024-05-09T10:30:00.123456"
    }
    // ... más empresas
  ]
}
```

---

### 5. Estadísticas
```http
GET /api/stats
```

**Respuesta:**
```json
{
  "total_companies": 234,
  "companies_by_niche": [
    {
      "niche": "veterinarias",
      "count": 45
    },
    {
      "niche": "restaurantes",
      "count": 89
    }
  ],
  "active_companies": 210,
  "inactive_companies": 24
}
```

---

## Docker Compose

```bash
# Desde la raíz del proyecto
docker-compose up --build

# La API estará en http://localhost:8000
# PostgreSQL estará en localhost:5432
```

---

## Ejemplo de Uso desde Frontend (React/JavaScript)

```javascript
// Búsqueda sincrónica
async function searchCompanies(niche, pages = 1) {
  try {
    const response = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        niche: niche,
        pages: pages
      })
    });
    
    const data = await response.json();
    console.log(`Encontradas ${data.total_companies} empresas`);
    return data.companies;
  } catch (error) {
    console.error('Error en búsqueda:', error);
  }
}

// Búsqueda asincrónica
async function searchCompaniesAsync(niche, pages = 1) {
  try {
    const response = await fetch('http://localhost:8000/api/search-async', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        niche: niche,
        pages: pages
      })
    });
    
    const data = await response.json();
    console.log('Búsqueda iniciada en background');
    
    // Poll para obtener resultados
    let attempts = 0;
    const maxAttempts = 60; // 5 minutos (5s * 60)
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000)); // Esperar 5s
      
      const resultsResponse = await fetch(
        `http://localhost:8000/api/companies/${niche}`
      );
      const resultsData = await resultsResponse.json();
      
      if (resultsData.total > 0) {
        console.log(`Búsqueda completada: ${resultsData.total} empresas`);
        return resultsData.companies;
      }
      
      attempts++;
    }
    
    console.log('Timeout esperando resultados');
  } catch (error) {
    console.error('Error en búsqueda async:', error);
  }
}

// Obtener estadísticas
async function getStats() {
  try {
    const response = await fetch('http://localhost:8000/api/stats');
    const data = await response.json();
    console.log('Estadísticas:', data);
    return data;
  } catch (error) {
    console.error('Error obteniendo estadísticas:', error);
  }
}

// Uso
searchCompanies('veterinarias', 2).then(companies => {
  companies.forEach(company => {
    console.log(`${company.name} - ${company.city}`);
  });
});
```

---

## Estructura de Base de Datos

### Tabla: `companies`
```sql
CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(500) NOT NULL,
  url VARCHAR(1000),
  rues VARCHAR(100),
  city VARCHAR(200),
  is_active BOOLEAN DEFAULT true,
  status VARCHAR(50),
  company_size VARCHAR(50),
  search_niche VARCHAR(200),
  scraped_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(url)
);
```

### Tabla: `search_logs`
```sql
CREATE TABLE search_logs (
  id SERIAL PRIMARY KEY,
  niche VARCHAR(200) NOT NULL,
  total_companies INT,
  pages_scraped INT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  status VARCHAR(50)
);
```

---

## Notas Importantes

⚠️ **Respectar el sitio:**
- El scraper tiene delays entre requests (1-2 segundos)
- No aumentar la velocidad para evitar bloqueos
- Usar con responsabilidad

📊 **Performance:**
- Búsqueda de 1 página: ~30-45 segundos
- Búsqueda de 5 páginas: ~2-3 minutos
- Para búsquedas largas, usar `/api/search-async`

🔄 **Duplicados:**
- El scraper evita duplicados usando `UNIQUE(url)`
- Si repites búsqueda, actualiza los datos existentes

---

## Troubleshooting

### Error: "No se encontraron resultados"
- El nicho no existe o está mal escrito
- Probar con términos más comunes

### Timeout en búsqueda
- El servidor puede estar saturado
- Intentar con menos páginas
- Usar endpoint asincrónico (`/api/search-async`)

### Error de conexión PostgreSQL
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en variables de entorno
- Si usa Docker: `docker-compose up -d db`

### Chrome/Chromium no encontrado
- Instalar Chrome o Chromium
- En Docker ya está incluido

---

## Roadmap

- [ ] Agregar cache de resultados
- [ ] Información detallada por empresa (al hacer click)
- [ ] Exportar a CSV/Excel
- [ ] Filtrado avanzado (ciudad, tamaño, etc)
- [ ] Webhook para notificar nuevas empresas
- [ ] Rate limiting y autenticación

