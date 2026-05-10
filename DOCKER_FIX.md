# 🚨 DOCKER NO CARGA - SOLUCIÓN RÁPIDA

## Problema
- Frontend no carga
- Backend se queda trabado
- Contenedores en "Restarting"

## Causa
- Volúmenes conflictivos
- Dependencias mal configuradas
- Imágenes corrompidas

## ✅ SOLUCIÓN (Copiar y ejecutar)

### Opción 1: PowerShell (Windows)

```powershell
# Copiar y ejecutar en terminal PowerShell
cd c:\Users\davir\OneDrive\Documentos\proyectos\phylloleads

# Reset nuclear
docker-compose down -v
docker system prune -af
docker volume prune -f

# Reconstruir
docker-compose build --no-cache

# Iniciar
docker-compose up -d

# Esperar 30 segundos
Start-Sleep -Seconds 30

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Opción 2: Bash (Mac/Linux)

```bash
cd /path/to/phylloleads

# Reset nuclear
docker-compose down -v
docker system prune -af
docker volume prune -f

# Reconstruir
docker-compose build --no-cache

# Iniciar
docker-compose up -d

# Esperar
sleep 30

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

## 🔍 Verificar que Funciona

Cuando veas en la terminal:

```
NAME              SERVICE       STATUS
phylloleads_frontend   frontend  Up (healthy)
phylloleads_backend    backend   Up (healthy)
phylloleads_database   database  Up (healthy)
```

Entonces:

1. Abre: http://localhost:5173 (Frontend)
2. Abre: http://localhost:8000/docs (Backend)

## 📊 Lo Que Cambié

✅ Frontend ahora en puerto 5173 (Vite dev server)
✅ Frontend usa Dockerfile.dev con hot-reload
✅ Backend en puerto 8000 (FastAPI)
✅ Quitamos conflicto de volúmenes
✅ Database healthcheck properly configured
✅ NODE_ENV=development para frontend

## 🆘 Si Sigue Sin Funcionar

### Error: "Cannot connect to Docker daemon"
```powershell
# Abre Docker Desktop (busca en Applications)
docker ps  # Verifica que funciona
```

### Error: "Port already in use"
```powershell
# Encontrar qué usa el puerto
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# Matar el proceso
taskkill /PID <PID> /F
```

### Error: "Build failed"
```powershell
# Limpiar y reintentar
docker-compose down -v
docker system prune -af
docker-compose build --no-cache --progress=plain
```

### Ver logs específicos
```powershell
docker-compose logs frontend -f
docker-compose logs backend -f
docker-compose logs database -f
```

## ✅ Checklist

- [ ] Docker Desktop abierto
- [ ] Ejecuté: docker-compose down -v
- [ ] Ejecuté: docker-compose build --no-cache
- [ ] Ejecuté: docker-compose up -d
- [ ] Espera 30 segundos
- [ ] docker-compose ps muestra "healthy"
- [ ] http://localhost:5173 carga (Frontend)
- [ ] http://localhost:8000/health responde (Backend)

---

**PRÓXIMAS PRUEBAS:**

Una vez que todo cargue:

1. En http://localhost:5173:
   - Debería ver página de Leads
   - Selecciona un nicho
   - Click "Iniciar Búsqueda"

2. En otra terminal:
   ```
   curl http://localhost:8000/health
   # Debe responder: {"status":"ok"}
   ```

3. Test API:
   ```
   curl -X POST http://localhost:8000/api/scraper/start ^
     -H "Content-Type: application/json" ^
     -d "{\"niches\":[\"veterinarias\"],\"target_count\":10}"
   ```

---

¡Avísame cuando esté corriendo! 🚀
