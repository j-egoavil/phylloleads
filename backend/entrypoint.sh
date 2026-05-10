#!/bin/bash
set -e

echo "================================"
echo "🚀 Iniciando Phylloleads Backend"
echo "================================"

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
while ! pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER}; do
    echo "⏳ PostgreSQL no está disponible, esperando..."
    sleep 2
done

echo "✅ PostgreSQL está disponible"

# Crear base de datos si no existe
echo "📦 Verificando base de datos..."
export PGPASSWORD=${DB_PASSWORD}
psql -h ${DB_HOST} -U ${DB_USER} -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}' " | grep -q 1 || psql -h ${DB_HOST} -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};"
echo "✅ Base de datos lista"

# Ejecutar migraciones/init si existe
if [ -f /app/init.sql ]; then
    echo "🔄 Cargando schema de BD..."
    psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -f /app/init.sql > /dev/null 2>&1 || true
    echo "✅ Schema verificado"
fi

# Ejecutar comando pasado
echo "▶️  Ejecutando comando: $@"
exec "$@"
