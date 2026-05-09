## Cambios solicitados

### 1. Fechas absolutas en lugar de relativas
- Reemplazar `formatRelative(...)` por `formatAbsolute(...)` en:
  - `src/components/dashboard/LeadTable.tsx` (columna "Creado")
  - `src/routes/configuration.tsx` (log de scrapes)
  - `src/routes/leads.$id.tsx` (historial de fases)
- Mantener `formatAbsolute` con formato `dd/MM/yyyy HH:mm` (es-CO).
- El tooltip al hover puede mantenerse o invertirse (mostrar relativa al hover).

### 2. Límite de scrapeo configurable
- En `src/store/leadStore.ts`:
  - Añadir `scrapeLimit: number` (default 20) y `setScrapeLimit(n)`.
  - `triggerScrape()` respetará `Math.min(count, scrapeLimit)`.
  - El simulador (`useRealtimeSimulator`) dejará de añadir leads cuando `leads.length >= scrapeLimit * algún factor` o se respetará por scrape — usaremos límite por ejecución.
- En `src/routes/configuration.tsx`: nuevo input numérico (1–100) con slider o input para ajustar el límite por ejecución, con toast al guardar.

### 3. Nichos (categorías de negocio)
- En `src/lib/mockData.ts`:
  - Añadir tipo `LeadNiche` con valores: `restaurantes`, `tecnologia`, `salud`, `retail`, `servicios`, `construccion`, `educacion`, `finanzas`.
  - Cada lead recibe un `niche` aleatorio. Asignar nicho coherente según el nombre de la empresa cuando sea posible (mapa simple) o aleatorio.
  - Añadir `NICHE_LABELS`.
- En `src/store/leadStore.ts`:
  - Añadir `niches: Record<LeadNiche, boolean>` (todas activas por defecto) y `toggleNiche(n)`.
  - Filtrar visibilidad de leads en el dashboard: si un nicho está desactivado, sus leads no se muestran (filtro adicional en `LeadTable` y métricas que dependan).
- En `src/routes/configuration.tsx`:
  - Nueva sección "Nichos" con cards/toggles igual que "Fuentes de Leads", mostrando cada nicho con un icono lucide y conteo de leads en ese nicho.
- En `src/components/dashboard/LeadTable.tsx`:
  - Añadir filtro por `niches` activos.
  - Mostrar nicho como badge en la tabla (columna nueva o junto a empresa).

### Archivos a modificar
- `src/lib/mockData.ts` — tipo Niche, generación, labels
- `src/lib/formatters.ts` — sin cambios (usar `formatAbsolute` existente)
- `src/store/leadStore.ts` — nuevas propiedades y acciones
- `src/components/dashboard/LeadTable.tsx` — fecha absoluta + filtro nicho + columna nicho
- `src/routes/configuration.tsx` — sección límite scrapeo + sección nichos + fechas absolutas en log
- `src/routes/leads.$id.tsx` — fechas absolutas en historial
- `src/routes/analytics.tsx` — verificar si filtra por nichos visibles (sí, aplicar)

### Notas
- El simulador en tiempo real seguirá generando leads, pero los que pertenezcan a nichos desactivados quedarán ocultos en la UI (no se eliminan del store).
- El límite de scrapeo solo aplica a `triggerScrape()` (ejecución manual + automática del countdown), no al stream realtime de 1 lead cada 8s.
