# ⚡ Comandos Rápidos - Solución Docker

## 🚀 Ejecuta en Orden (Copia-Pega)

### Paso 1: Detener contenedores
```bash
docker-compose down
```

### Paso 2: Limpiar (opcional pero recomendado)
```bash
docker system prune -a
```
Presiona `y` cuando pregunte.

### Paso 3: Reconstruir
```bash
docker-compose up --build
```

Espera a ver:
```
✓ phylloleads_frontend started
✓ phylloleads_backend started
✓ phylloleads_database started
```

### Paso 4: Verificar que funciona
En otra terminal:
```bash
docker-compose logs -f backend
```

Busca: `Firefox iniciado` o `Driver de Firefox inicializado`

### Paso 5: Probar API
Abre en navegador:
```
http://localhost:8000/docs
```

---

## 📋 Si Algo Falla

### Ver más detalles del error
```bash
docker-compose logs backend
```

### Reconstruir sin cache
```bash
docker-compose build --no-cache backend
docker-compose up
```

### Ver estado de contenedores
```bash
docker-compose ps
```

### Entrar al contenedor
```bash
docker-compose exec backend bash
```

---

## ✅ Checklist de Verificación

- [ ] `docker-compose down` ejecutado
- [ ] `docker system prune -a` ejecutado
- [ ] `docker-compose up --build` ejecutado
- [ ] Contenedores iniciaron exitosamente
- [ ] Frontend disponible en http://localhost:3000
- [ ] Backend disponible en http://localhost:8000
- [ ] API docs disponibles en http://localhost:8000/docs

---

## 🎯 Resultado Esperado

```
phylloleads-backend       | Firefox iniciado
phylloleads-backend       | INFO:     Application startup complete
phylloleads-backend       | INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 📞 Que Se Cambió

✅ Firefox en lugar de Chromium (disponible en Debian)
✅ Geckodriver para controlar Firefox
✅ Scripts actualizados para intentar Firefox primero
✅ Compatible tanto local como en Docker

---

¡Listo! 🎉
