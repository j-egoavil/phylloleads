# Phylloleads Docker Makefile
# Comandos útiles para gestionar la aplicación con Docker

.PHONY: help build up down logs shell-backend shell-db migrate clean reset

help:
	@echo "╔════════════════════════════════════════════════╗"
	@echo "║      PHYLLOLEADS - Docker Commands              ║"
	@echo "╚════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 BUILD & SETUP"
	@echo "  make build              - Construir imágenes Docker"
	@echo "  make build-backend      - Reconstruir solo backend"
	@echo "  make up                 - Levantar servicios (logs activos)"
	@echo "  make up-d               - Levantar servicios (background)"
	@echo "  make down               - Detener servicios"
	@echo "  make restart            - Reiniciar servicios"
	@echo ""
	@echo "📊 DATABASE"
	@echo "  make migrate            - Inicializar BD desde init.sql"
	@echo "  make db-shell           - Conectar a PostgreSQL shell"
	@echo "  make db-reset           - BORRAR Y RECREAR BD (⚠️  cuidado)"
	@echo ""
	@echo "📝 LOGS & DEBUG"
	@echo "  make logs               - Ver logs de todos los servicios"
	@echo "  make logs-backend       - Ver logs solo del backend"
	@echo "  make logs-db            - Ver logs solo de la BD"
	@echo "  make shell-backend      - Entrar al contenedor backend"
	@echo ""
	@echo "🧹 CLEANUP"
	@echo "  make clean              - Limpiar contenedores (mantiene BD)"
	@echo "  make reset              - Limpiar TODO (⚠️  cuidado, borra datos)"
	@echo ""
	@echo "🚀 SCRAPERS"
	@echo "  make run-scrapers       - Ejecutar todos los scrapers"
	@echo "  make migrate-data       - Migrar datos de SQLite a PostgreSQL"
	@echo ""

# ============================================================================
# BUILD
# ============================================================================
build:
	@echo "🔨 Construyendo imágenes Docker..."
	docker-compose build

build-backend:
	@echo "🔨 Reconstruyendo backend..."
	docker-compose build backend

# ============================================================================
# SERVICES
# ============================================================================
up:
	@echo "🚀 Levantando servicios (Ctrl+C para detener)..."
	docker-compose up

up-d:
	@echo "🚀 Levantando servicios en background..."
	docker-compose up -d
	@echo "✅ Servicios levantados"
	@echo "📍 Frontend: http://localhost:3000"
	@echo "📍 Backend:  http://localhost:8000"
	@echo "📍 DB:       localhost:5432"

down:
	@echo "⏹️  Deteniendo servicios..."
	docker-compose down

restart:
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart
	@echo "✅ Servicios reiniciados"

# ============================================================================
# DATABASE
# ============================================================================
migrate:
	@echo "🔄 Inicializando BD desde init.sql..."
	docker-compose exec -T database psql -U postgres -d appdb -f /docker-entrypoint-initdb.d/01-init.sql
	@echo "✅ BD inicializada"

db-shell:
	@echo "🔌 Conectando a PostgreSQL shell..."
	docker-compose exec database psql -U postgres -d appdb

db-reset:
	@echo "⚠️  ADVERTENCIA: Esto borrará TODA la BD"
	@echo "¿Estás seguro? (escribe 'si' para confirmar)"
	@read CONFIRM; \
	if [ "$$CONFIRM" = "si" ]; then \
		echo "🗑️  Borrando BD..."; \
		docker-compose exec -T database psql -U postgres -c "DROP DATABASE IF EXISTS appdb;"; \
		docker-compose exec -T database psql -U postgres -c "CREATE DATABASE appdb;"; \
		$(MAKE) migrate; \
		echo "✅ BD recreada"; \
	else \
		echo "❌ Cancelado"; \
	fi

# ============================================================================
# LOGS
# ============================================================================
logs:
	@echo "📋 Mostrando logs de todos los servicios..."
	docker-compose logs -f

logs-backend:
	@echo "📋 Logs del backend..."
	docker-compose logs -f backend

logs-db:
	@echo "📋 Logs de la BD..."
	docker-compose logs -f database

logs-frontend:
	@echo "📋 Logs del frontend..."
	docker-compose logs -f frontend

# ============================================================================
# SHELL ACCESS
# ============================================================================
shell-backend:
	@echo "🐚 Entrando al contenedor backend..."
	docker-compose exec backend bash

shell-db:
	@echo "🐚 Entrando a PostgreSQL..."
	docker-compose exec database bash

# ============================================================================
# CLEANUP
# ============================================================================
clean:
	@echo "🧹 Limpiando contenedores (BD se mantiene)..."
	docker-compose down
	@echo "✅ Limpieza completada"

reset:
	@echo "⚠️  ADVERTENCIA: Esto eliminará TODOS los contenedores y volúmenes"
	@echo "¿Estás seguro? (escribe 'si' para confirmar)"
	@read CONFIRM; \
	if [ "$$CONFIRM" = "si" ]; then \
		echo "🗑️  Eliminando TODO..."; \
		docker-compose down -v; \
		echo "✅ Reset completado"; \
	else \
		echo "❌ Cancelado"; \
	fi

# ============================================================================
# SCRAPERS
# ============================================================================
run-scrapers:
	@echo "🕷️  Ejecutando scrapers en el contenedor..."
	docker-compose exec backend python run_scraper_maestro.py --timeout 900

migrate-data:
	@echo "📊 Migrando datos de SQLite a PostgreSQL..."
	docker-compose exec backend python migrate_sqlite_to_postgres.py

# ============================================================================
# STATUS
# ============================================================================
ps:
	@echo "📦 Estado de contenedores:"
	docker-compose ps

status:
	@echo "🔍 Status de servicios:"
	docker-compose ps -a
	@echo ""
	@echo "🌐 Puertos activos:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  DB:       localhost:5432"
	@echo ""
	@echo "💾 Volúmenes:"
	@docker volume ls | grep phylloleads

# ============================================================================
# ENV FILE
# ============================================================================
env:
	@echo "📝 Copiando .env.example a .env..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Archivo .env creado. Edita tus variables en .env"; \
	else \
		echo "⚠️  .env ya existe, no se sobrescribe"; \
	fi

shell-db:
	docker-compose exec database psql -U postgres -d phylloleads

# Test
test:
	docker-compose exec backend python -m pytest || true

# Development flow
dev-build: build up logs

# One command to start everything
start: build up status
