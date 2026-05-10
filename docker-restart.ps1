# Script para limpiar y reiniciar Docker completamente (Windows/PowerShell)

Write-Host "🧹 Limpiando Docker..." -ForegroundColor Yellow

# Detener y remover
Write-Host "Deteniendo contenedores..." -ForegroundColor Cyan
docker-compose down -v 2>$null

# Esperar
Start-Sleep -Seconds 2

# Limpiar imágenes
Write-Host "🗑️ Removiendo imágenes viejas..." -ForegroundColor Yellow
docker image prune -f 2>$null

# Rebuild
Write-Host "🔨 Reconstruyendo imágenes..." -ForegroundColor Yellow
docker-compose build --no-cache

# Start
Write-Host "🚀 Iniciando servicios..." -ForegroundColor Green
docker-compose up -d

# Esperar inicialización
Write-Host ""
Write-Host "⏳ Esperando a que los servicios inicien (30 segundos)..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Verificar estado
Write-Host ""
Write-Host "✅ Verificando estado..." -ForegroundColor Green
docker-compose ps

# Logs
Write-Host ""
Write-Host "📝 Mostrando logs (Ctrl+C para salir)..." -ForegroundColor Cyan
docker-compose logs -f
