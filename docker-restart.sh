#!/bin/bash
# Script para limpiar y reiniciar Docker completamente

echo "🧹 Limpiando Docker..."

# Detener todos los contenedores
docker-compose down -v 2>/dev/null || true

# Esperar un poco
sleep 2

# Limpiar imágenes no usadas
echo "🗑️  Removiendo imágenes viejas..."
docker image prune -f 2>/dev/null || true

# Rebuild y start
echo "🔨 Reconstruyendo imágenes..."
docker-compose build --no-cache

echo "🚀 Iniciando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios inicien (30 segundos)..."
sleep 30

echo ""
echo "✅ Verificando estado..."
docker-compose ps

echo ""
echo "📝 Mostrando logs (Ctrl+C para salir)..."
docker-compose logs -f
