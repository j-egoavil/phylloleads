#!/bin/bash

# Abortar si algún comando falla
set -e

# Esperar a que la base de datos esté lista si las variables están definidas
if [ -n "$DB_HOST" ]; then
  echo "Esperando a la base de datos en $DB_HOST:$DB_PORT..."
  until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
  done
  echo "Base de datos conectada!"
fi

# Ejecutar el comando principal (uvicorn)
exec "$@"