# 🗄️ Setup PostgreSQL para Phylloleads

## Opción 1: Instalar PostgreSQL Localmente (Windows)

### 1. Descargar e Instalar PostgreSQL
- Descargar desde: https://www.postgresql.org/download/windows/
- Recomendado: PostgreSQL 14 o superior
- Durante la instalación:
  - Usuario: `postgres`
  - Contraseña: `postgres` (o tu contraseña preferida)
  - Puerto: `5432`
  - Locale: `Spanish`

### 2. Verificar instalación
```powershell
psql --version
```

### 3. Conectar a PostgreSQL y crear BD
```powershell
psql -U postgres
```

En la consola de PostgreSQL:
```sql
CREATE DATABASE appdb;
\c appdb
\i init.sql
```

## Opción 2: PostgreSQL con Docker

### 1. Instalar Docker Desktop (Windows)
- Descargar desde: https://www.docker.com/products/docker-desktop

### 2. Crear contenedor PostgreSQL
```powershell
docker run --name phylloleads-db `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=appdb `
  -p 5432:5432 `
  -d postgres:15
```

### 3. Conectar y cargar schema
```powershell
docker exec -it phylloleads-db psql -U postgres -d appdb -f /init.sql
```

O manualmente:
```powershell
docker exec -it phylloleads-db psql -U postgres
```

```sql
\c appdb
\i init.sql
```

## Opción 3: PostgreSQL en la Nube (AWS RDS)

### 1. Crear RDS Postgres en AWS Console
- Motor: PostgreSQL 14
- Instancia: `db.t3.micro` (free tier eligible)
- Usuario: `postgres`
- Contraseña: genera una segura

### 2. Obtener endpoint y credenciales del RDS

### 3. Cargar schema en RDS
```powershell
psql -h <ENDPOINT> -U postgres -d appdb -f init.sql
```

## Configurar Variables de Entorno

### Windows PowerShell
```powershell
# Permanente (agregar al perfil de PowerShell)
$PROFILE

# Agregar estas líneas al archivo del perfil:
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "appdb"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
```

### Windows CMD
```cmd
setx DB_HOST "localhost"
setx DB_PORT "5432"
setx DB_NAME "appdb"
setx DB_USER "postgres"
setx DB_PASSWORD "postgres"
```

### Linux/Mac
```bash
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="appdb"
export DB_USER="postgres"
export DB_PASSWORD="postgres"
```

## Migrar Datos de SQLite a PostgreSQL

### 1. Exportar datos de SQLite
```bash
python backend/scripts/migrate_sqlite_to_postgres.py
```

## Verificar Conexión

```python
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="appdb",
        user="postgres",
        password="postgres"
    )
    print("✅ Conectado a PostgreSQL")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
```

## Ejecutar Scrapers con PostgreSQL

### Opción A: Automático (si env vars están configuradas)
```powershell
py -3 backend/run_scraper_maestro.py
```

### Opción B: Manual
```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
py -3 backend/run_scraper_maestro.py
```

## Troubleshooting

### Error: "FATAL:  password authentication failed"
- Verificar usuario y contraseña en variables de entorno
- Reiniciar la terminal después de setear env vars

### Error: "could not translate host name"
- Verificar que PostgreSQL esté corriendo
- En Docker: `docker ps` debe mostrar el contenedor

### Error: "database 'appdb' does not exist"
- Ejecutar: `CREATE DATABASE appdb;` en PostgreSQL
- Luego cargar el schema: `\i init.sql`

## Comandos Útiles PostgreSQL

```sql
-- Ver todas las BD
\l

-- Conectar a BD
\c appdb

-- Ver tablas
\dt

-- Ver estructura de tabla
\d companies

-- Ver índices
\di

-- Contar registros
SELECT COUNT(*) FROM companies;

-- Resetear BD (WARNING: elimina todo)
DROP DATABASE appdb;
CREATE DATABASE appdb;
\c appdb
\i init.sql
```
