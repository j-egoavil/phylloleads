// ARCHIVO ARCHIVADO - No usar
// Este archivo era un store de Zustand con datos simulados (mocks)
//
// El nuevo sistema usa useLeadScraper que:
// - Conecta a la API real del backend
// - Maneja estado localmente (no necesita store global)
// - Proporciona datos en tiempo real vía WebSocket
//
// MIGRACIÓN:
// Remover: import { useLeadStore } from "@/store/leadStore"
// Usar:    import { useLeadScraper } from "@/hooks/useLeadScraper"
//
// El nuevo hook retorna el mismo estado pero conectado a API real

export function useLeadStore() {
  throw new Error(
    'leadStore.ts ha sido archivado. ' +
    'Usar useLeadScraper hook en lugar. ' +
    'Ver: frontend/src/hooks/useLeadScraper.js'
  )
}
