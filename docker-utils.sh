#!/bin/bash

# =============================================================================
# PHYLLOLEADS - Docker Utility Script
# =============================================================================
# Uso: ./docker-utils.sh [comando]
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "╔═════════════════════════════════════════════════════════════╗"
    echo "║         PHYLLOLEADS - Docker Utility Script                 ║"
    echo "╚═════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Ayuda
show_help() {
    cat << EOF
${BLUE}Comandos disponibles:${NC}

${GREEN}Construcción:${NC}
  build              Construir todas las imágenes
  build-frontend     Construir solo frontend
  build-backend      Construir solo backend
  build-nc           Construir sin cache

${GREEN}Ejecución:${NC}
  up                 Iniciar todos los servicios
  down               Detener todos los servicios
  dev                Iniciar en modo desarrollo
  logs               Ver logs de todos los servicios
  logs-frontend      Ver logs del frontend
  logs-backend       Ver logs del backend
  logs-db            Ver logs de la base de datos

${GREEN}Utilidades:${NC}
  ps                 Ver estado de los servicios
  restart            Reiniciar todos los servicios
  restart-frontend   Reiniciar frontend
  restart-backend    Reiniciar backend
  clean              Detener y eliminar volúmenes
  shell-frontend     Entrar en el contenedor frontend
  shell-backend      Entrar en el contenedor backend
  shell-db           Conectar a PostgreSQL

${GREEN}Verificación:${NC}
  health             Verificar salud de los servicios
  status             Ver estado detallado
  test               Ejecutar tests

${GREEN}Otros:${NC}
  help               Mostrar esta ayuda
  version            Mostrar versión

EOF
}

# Funciones
build_all() {
    echo -e "${YELLOW}Construyendo todas las imágenes...${NC}"
    docker-compose build
    echo -e "${GREEN}✓ Construcción completada${NC}"
}

build_frontend() {
    echo -e "${YELLOW}Construyendo frontend...${NC}"
    docker-compose build frontend
    echo -e "${GREEN}✓ Frontend construido${NC}"
}

build_backend() {
    echo -e "${YELLOW}Construyendo backend...${NC}"
    docker-compose build backend
    echo -e "${GREEN}✓ Backend construido${NC}"
}

build_no_cache() {
    echo -e "${YELLOW}Construyendo sin cache...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}✓ Construcción completada${NC}"
}

up() {
    echo -e "${YELLOW}Iniciando servicios...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Servicios iniciados${NC}"
    sleep 2
    show_urls
}

dev() {
    echo -e "${YELLOW}Iniciando en modo desarrollo...${NC}"
    docker-compose up
}

down() {
    echo -e "${YELLOW}Deteniendo servicios...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Servicios detenidos${NC}"
}

logs_all() {
    docker-compose logs -f
}

logs_frontend() {
    docker-compose logs -f frontend
}

logs_backend() {
    docker-compose logs -f backend
}

logs_db() {
    docker-compose logs -f database
}

ps() {
    docker-compose ps
}

restart_all() {
    echo -e "${YELLOW}Reiniciando servicios...${NC}"
    docker-compose restart
    echo -e "${GREEN}✓ Servicios reiniciados${NC}"
}

restart_frontend() {
    echo -e "${YELLOW}Reiniciando frontend...${NC}"
    docker-compose restart frontend
    echo -e "${GREEN}✓ Frontend reiniciado${NC}"
}

restart_backend() {
    echo -e "${YELLOW}Reiniciando backend...${NC}"
    docker-compose restart backend
    echo -e "${GREEN}✓ Backend reiniciado${NC}"
}

clean() {
    echo -e "${RED}Eliminando servicios y volúmenes...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ Limpieza completada${NC}"
}

shell_frontend() {
    echo -e "${YELLOW}Entrando en frontend...${NC}"
    docker-compose exec frontend sh
}

shell_backend() {
    echo -e "${YELLOW}Entrando en backend...${NC}"
    docker-compose exec backend bash
}

shell_db() {
    echo -e "${YELLOW}Conectando a PostgreSQL...${NC}"
    docker-compose exec database psql -U postgres -d phylloleads
}

health_check() {
    echo -e "${YELLOW}Verificando salud de servicios...${NC}"
    
    echo -e "\n${BLUE}Frontend:${NC}"
    curl -s http://localhost:3000 > /dev/null && echo -e "${GREEN}✓ OK${NC}" || echo -e "${RED}✗ Fallo${NC}"
    
    echo -e "${BLUE}Backend:${NC}"
    curl -s http://localhost:8000/health > /dev/null && echo -e "${GREEN}✓ OK${NC}" || echo -e "${RED}✗ Fallo${NC}"
    
    echo -e "${BLUE}Database:${NC}"
    docker-compose exec database pg_isready -U postgres > /dev/null 2>&1 && echo -e "${GREEN}✓ OK${NC}" || echo -e "${RED}✗ Fallo${NC}"
}

status() {
    echo -e "\n${BLUE}Estado de contenedores:${NC}"
    ps
    echo -e "\n${BLUE}URLs accesibles:${NC}"
    show_urls
}

show_urls() {
    echo -e "\n${GREEN}URLs disponibles:${NC}"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend:      http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/docs"
    echo "  Database:     localhost:5432"
    echo ""
}

# Ejecutar comando
main() {
    show_banner
    
    case "${1:-help}" in
        build)
            build_all
            ;;
        build-frontend)
            build_frontend
            ;;
        build-backend)
            build_backend
            ;;
        build-nc)
            build_no_cache
            ;;
        up)
            build_all
            up
            ;;
        dev)
            dev
            ;;
        down)
            down
            ;;
        logs)
            logs_all
            ;;
        logs-frontend)
            logs_frontend
            ;;
        logs-backend)
            logs_backend
            ;;
        logs-db)
            logs_db
            ;;
        ps)
            ps
            ;;
        restart)
            restart_all
            ;;
        restart-frontend)
            restart_frontend
            ;;
        restart-backend)
            restart_backend
            ;;
        clean)
            clean
            ;;
        shell-frontend)
            shell_frontend
            ;;
        shell-backend)
            shell_backend
            ;;
        shell-db)
            shell_db
            ;;
        health)
            health_check
            ;;
        status)
            status
            ;;
        test)
            echo -e "${YELLOW}Ejecutando tests...${NC}"
            docker-compose exec backend python -m pytest || true
            ;;
        version)
            echo "Phylloleads Docker Utility v1.0"
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}Comando desconocido: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
