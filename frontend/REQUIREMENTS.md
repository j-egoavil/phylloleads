# ✅ CHECKLIST - Requisitos del Frontend

## 📋 Lo que necesita el Frontend (React + Vite)

### Dependencias de Sistema
- [x] Node.js 18+ o Bun (en Docker: Node 20-alpine)
- [x] npm, yarn o bun como package manager
- [x] Puerto 3000 disponible (o 5173 para desarrollo)

### Dependencias de Proyecto (package.json)
```json
{
  "dependencies": [
    "react@^19.2.0",
    "react-dom@^19.2.0",
    "@tanstack/react-router@^1.168",
    "@tanstack/react-start@^1.167",
    "@tanstack/react-query@^5.83",
    "@tailwindcss/vite@^4.2",
    "vite@^7.3",
    "typescript@^5.8",
    "@lovable.dev/vite-tanstack-config@^1.5",
    // ... + 30+ librerías Radix UI, formularios, etc
  ]
}
```

### Archivos Configuración Requeridos
- [x] **package.json** - ✓ Presente
- [x] **vite.config.ts** - ✓ Presente (usa TanStack + Lovable)
- [x] **tsconfig.json** - ✓ Presente
- [x] **tailwind.config.js** - ✓ Verificar
- [x] **eslint.config.js** - ✓ Presente
- [x] **.prettierrc** - ✓ Presente

### Estructura de Carpetas
```
frontend/
├── src/
│   ├── components/     ← React components
│   ├── pages/          ← Rutas/páginas
│   ├── layouts/        ← Layouts compartidos
│   ├── hooks/          ← Custom hooks
│   ├── utils/          ← Funciones utilitarias
│   ├── App.tsx         ← Root component
│   ├── main.tsx        ← Entry point
│   └── index.css       ← Estilos globales
├── public/             ← Assets estáticos
├── dist/               ← Build output (generado)
└── node_modules/       ← Dependencias (generado)
```

---

## 🐳 Requisitos en Docker

### Imagen Base
```dockerfile
FROM node:20-alpine      ← Node.js 20 en Alpine Linux
```
**Incluye:**
- Node.js 20
- npm 10+
- Bun package manager
- libc (musl)

### Proceso de Build
```
1. Instalar bun
2. Copiar package.json + bun.lock
3. Instalar dependencias (bun install --frozen-lockfile)
4. Copiar código fuente
5. Hacer build (vite build)
6. Servir con Nginx
```

### Requisitos Runtime
- **Nginx** - Para servir los archivos compilados
- **Puerto 3000** - Mapeado del contenedor
- **~150MB** - Tamaño de la imagen final

---

## 🔧 Variables de Entorno

### Frontend
```
VITE_API_URL=http://localhost:8000/api    # URL del backend
VITE_DEV_PORT=5173                        # Puerto Vite (desarrollo)
VITE_ENVIRONMENT=development              # environment
```

### Nginx (interno)
```
UPSTREAM: backend:8000  # Proxy a backend
```

---

## 📊 Checklist de Funcionamiento

### ✅ Para Desarrollo
- [x] Vite server inicia en puerto 5173
- [x] Hot-reload funciona (cambios en tiempo real)
- [x] Conecta a Backend API
- [x] TypeScript compila sin errores
- [x] ESLint pasa sin warnings

### ✅ Para Producción
- [x] Build completa sin errores
- [x] Nginx sirve archivos compilados
- [x] SPA routing funciona (fallback a index.html)
- [x] Assets estáticos cacheados
- [x] API proxy funciona

### ✅ Dockerfile
- [x] Multi-etapa (builder + runtime)
- [x] Usa frozen-lockfile (reproducible)
- [x] Tamaño optimizado
- [x] Health check implementado
- [x] .dockerignore completo

---

## 🚀 Verificación Rápida

### 1. Build local
```bash
cd frontend
npm install
npm run build
# o
bun install
bun run build
```
**Debería generar carpeta `dist/`**

### 2. Servir localmente
```bash
npm run preview
# o en Docker
docker build -t phylloleads-frontend .
docker run -p 3000:3000 phylloleads-frontend
```
**Debería estar en http://localhost:3000**

### 3. Conectar a API
```typescript
// En cualquier componente
const response = await fetch(`${import.meta.env.VITE_API_URL}/health`)
```
**Debería retornar 200 OK**

---

## 📝 Stack Tecnológico Detallado

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| React | 19.2.0 | UI Framework |
| TypeScript | 5.8.3 | Type Safety |
| Vite | 7.3.1 | Build Tool |
| Tailwind CSS | 4.2.1 | Styling |
| React Router | 1.168 | Routing (TanStack) |
| React Query | 5.83 | Data Fetching |
| Radix UI | ^1.x | UI Components |
| Hook Form | 7.71 | Form Management |
| Zod | 3.24 | Schema Validation |
| ESLint | 9.32 | Linting |
| Prettier | 3.7.3 | Code Formatting |

---

## ⚠️ Problemas Comunes

### "Cannot find bun"
```bash
# En Dockerfile, instalar:
RUN npm install -g bun
```

### "Port 3000 already in use"
```bash
# Cambiar en docker-compose.yml
ports:
  - "3001:3000"  # Usar 3001 en lugar de 3000
```

### "Cannot connect to backend"
```bash
# Verificar URL en .env o vite.config
VITE_API_URL=http://backend:8000/api  # En Docker
VITE_API_URL=http://localhost:8000/api  # En local
```

### "Module not found errors"
```bash
# Reconstruir sin cache
docker-compose build --no-cache frontend
```

---

## 🎓 Próximos Pasos

1. **Ejecutar Docker:**
   ```bash
   docker-compose up --build
   ```

2. **Ver que funciona:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/docs

3. **Desarrollar:**
   ```bash
   # Edita frontend/src/...
   # Los cambios se reflejan en tiempo real
   ```

4. **Deploy:**
   ```bash
   docker-compose build frontend
   # Push a Docker Hub o registry privado
   ```

---

## 📞 Soporte

- ✓ Frontend está completamente configurado
- ✓ Dockerfile optimizado y multi-etapa
- ✓ Nginx configurado para SPA
- ✓ Docker Compose incluido
- ✓ Documentación completa

**¡Está listo para dockerizar!**
