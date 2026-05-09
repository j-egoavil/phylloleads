# =============================================================================
# PHYLLOLEADS - Makefile
# =============================================================================
# Uso: make [target]
# =============================================================================

.PHONY: help build build-frontend build-backend up down dev logs clean

help:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║        PHYLLOLEADS - Docker Commands (Makefile)        ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "CONSTRUCCIÓN:"
	@echo "  make build              Construir todas las imágenes"
	@echo "  make build-frontend     Construir solo frontend"
	@echo "  make build-backend      Construir solo backend"
	@echo ""
	@echo "EJECUCIÓN:"
	@echo "  make up                 Iniciar servicios"
	@echo "  make down               Detener servicios"
	@echo "  make dev                Modo desarrollo"
	@echo ""
	@echo "LOGS Y ESTADO:"
	@echo "  make logs               Ver logs"
	@echo "  make logs-f             Ver logs (frontend)"
	@echo "  make logs-b             Ver logs (backend)"
	@echo "  make ps                 Ver estado"
	@echo ""
	@echo "UTILIDADES:"
	@echo "  make clean              Limpiar todo"
	@echo "  make restart            Reiniciar"
	@echo "  make health             Verificar salud"
	@echo ""

# Build
build:
	docker-compose build

build-frontend:
	docker-compose build frontend

build-backend:
	docker-compose build backend

# Run
up:
	docker-compose up -d

down:
	docker-compose down

dev:
	docker-compose up

restart:
	docker-compose restart

# Logs
logs:
	docker-compose logs -f

logs-f:
	docker-compose logs -f frontend

logs-b:
	docker-compose logs -f backend

logs-db:
	docker-compose logs -f database

# Status
ps:
	docker-compose ps

status:
	@echo "Estado de servicios:"
	@docker-compose ps
	@echo ""
	@echo "URLs:"
	@echo "  Frontend:   http://localhost:3000"
	@echo "  Backend:    http://localhost:8000"
	@echo "  API Docs:   http://localhost:8000/docs"

# Clean
clean:
	docker-compose down -v

# Health
health:
	@echo "Verificando servicios..."
	@curl -s http://localhost:3000 > /dev/null && echo "✓ Frontend" || echo "✗ Frontend"
	@curl -s http://localhost:8000/health > /dev/null && echo "✓ Backend" || echo "✗ Backend"

# Shell access
shell-f:
	docker-compose exec frontend sh

shell-b:
	docker-compose exec backend bash

shell-db:
	docker-compose exec database psql -U postgres -d phylloleads

# Test
test:
	docker-compose exec backend python -m pytest || true

# Development flow
dev-build: build up logs

# One command to start everything
start: build up status
