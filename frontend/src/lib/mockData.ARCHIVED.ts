// ARCHIVO ARCHIVADO - No usar
// Este archivo contenía generadores de datos simulados (mocks)
//
// ⚠️ TODOS LOS DATOS AHORA VIENEN DE LA API REAL
//
// Tipos reales de la API:
// - Ver: frontend/src/lib/types.ts
//
// Mocks que fueron removidos:
// - generateLead() → Ahora viene de /api/scraper/next-lead
// - seedLeads() → No necesario, API retorna datos reales
// - LeadSource, LeadStatus → No más tipos simulados
//
// El nuevo sistema:
// 1. useLeadScraper() conecta a API real
// 2. Todos los tipos están en types.ts
// 3. WebSocket proporciona actualizaciones en tiempo real
// 4. No hay simulación - datos 100% reales

export const MOCKS_DEPRECATED = true

console.error(
  'mockData.ts está archivado. ' +
  'El sistema ahora usa API real. ' +
  'Ver types.ts para los tipos reales de la API.'
)
