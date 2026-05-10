# =============================================================================
# STAGE 1: Build (Multi-etapa)
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Instalar bun
RUN npm install -g bun

# Copiar archivos de dependencias
COPY package.json bun.lock ./

# Instalar dependencias
RUN bun install --frozen-lockfile

# Copiar código fuente
COPY . .

# Hacer build con variables de entorno
ARG VITE_API_URL=http://backend:8000
ARG VITE_WS_URL=ws://backend:8000
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WS_URL=${VITE_WS_URL}

RUN bun run build || true

# =============================================================================
# STAGE 2: Runtime (Bun - TanStack Start Dev Server)
# =============================================================================
FROM oven/bun:latest

WORKDIR /app

# Copiar package.json y lock
COPY package.json bun.lock ./

# Instalar todas las dependencias (incluyendo dev para dev server)
RUN bun install --frozen-lockfile

# Copiar código fuente COMPLETO
COPY . .

# Copiar archivos compilados desde el builder (si existen)
COPY --from=builder /app/dist ./dist

# Variables de entorno por defecto
ARG VITE_API_URL=http://backend:8000
ARG VITE_WS_URL=ws://backend:8000
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WS_URL=${VITE_WS_URL}
ENV NODE_ENV=production

# Puerto donde se ejecuta TanStack Start
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl --silent --fail http://localhost:3000 || exit 1

# Usar el dev server de TanStack Start (que soporta SSR + estáticos)
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

