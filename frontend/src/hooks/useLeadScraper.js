/**
 * Hook de React para integración con API de Phylloleads
 * - Inicia scraper
 * - Obtiene leads en tiempo real
 * - Marca leads como aceptados
 * - Actualiza estado
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { useLeadStore } from '@/store/leadStore'
import { getApiUrl, getWsUrl } from '@/lib/apiConfig'

const getAPI_URL = () => getApiUrl()
const getWS_URL = () => getWsUrl()

export function useLeadScraper() {
  const [scraping, setScraping] = useState(false)
  const [leads, setLeads] = useState([])
  const [currentLead, setCurrentLead] = useState(null)
  const [status, setStatus] = useState({})
  const [selectedNiches, setSelectedNiches] = useState([])
  const [targetCount, setTargetCount] = useState(50)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)
  
  // Conectar con el store
  const addLead = useLeadStore((s) => s.addLead)

  // Conectar WebSocket
  useEffect(() => {
    if (scraping) {
      try {
        // Construir URL WebSocket usando la función dedicada
        const wsBaseUrl = getWS_URL()
        const wsUrl = `${wsBaseUrl}/api/scraper/ws`
        
        const ws = new WebSocket(wsUrl)
        let heartbeatInterval = null
        
        ws.onopen = () => {
          console.log('WebSocket conectado')
          requestStatus()
          // Enviar heartbeat cada 30 segundos para mantener conexión viva
          heartbeatInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'ping' }))
            }
          }, 30000)
        }
        
        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            
            if (message.type === 'status_update') {
              setStatus(message.data)
            } else if (message.type === 'new_lead') {
              setCurrentLead(message.lead)
              setLeads(prev => [...prev, message.lead])
            } else if (message.type === 'lead_accepted') {
              setStatus(message.status)
            }
          } catch (parseErr) {
            console.error('Error parsing WebSocket message:', parseErr)
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          setError('Error en conexión WebSocket')
        }
        
        ws.onclose = () => {
          console.log('WebSocket desconectado')
          if (heartbeatInterval) {
            clearInterval(heartbeatInterval)
          }
        }
        
        wsRef.current = ws
        
        return () => {
          if (heartbeatInterval) {
            clearInterval(heartbeatInterval)
          }
          if (wsRef.current) {
            wsRef.current.close()
          }
        }
      } catch (err) {
        console.error('WebSocket initialization error:', err)
        setError('Error inicializando WebSocket: ' + err.message)
      }
    }
  }, [scraping])

  // Iniciar scraper
  const startScraper = useCallback(async (niches, target) => {
    try {
      setError(null)
      setScraping(true)
      setLeads([])
      setSelectedNiches(niches)
      setTargetCount(target)
      
      const response = await fetch(`${getAPI_URL()}/api/scraper/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          niches: niches,
          target_count: target,
          min_category: 'C'
        })
      })
      
      if (!response.ok) {
        const contentType = response.headers.get('content-type')
        let errorMsg = `HTTP Error: ${response.status} ${response.statusText}`
        if (contentType?.includes('application/json')) {
          try {
            const errorData = await response.json()
            errorMsg = errorData.detail || errorMsg
          } catch (e) {
            // Si no puede parsear JSON, usa el mensaje genérico
          }
        }
        throw new Error(errorMsg)
      }
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.detail || 'Error iniciando scraper')
      }
      
      // Solicitar primer lead
      setTimeout(() => getNextLead(), 1000)
      
    } catch (err) {
      setError(err.message)
      setScraping(false)
    }
  }, [])

  // Obtener siguiente lead
  const getNextLead = useCallback(async () => {
    try {
      const response = await fetch(`${getAPI_URL()}/api/scraper/next-lead`)
      
      if (!response.ok) {
        const contentType = response.headers.get('content-type')
        let errorMsg = `Error ${response.status}: ${response.statusText}`
        if (contentType?.includes('application/json')) {
          try {
            const errorData = await response.json()
            errorMsg = errorData.detail || errorMsg
          } catch (e) {
            // Si no puede parsear JSON, usa el mensaje genérico
          }
        }
        throw new Error(errorMsg)
      }
      
      const data = await response.json()
      
      if (data.success) {
        const lead = {
          id: `${data.lead.id}`,
          name: data.lead.name,
          phone: data.lead.phone,
          website: data.lead.website,
          address: data.lead.address,
          city: data.lead.city,
          niche: data.lead.niche,
          status: 'search',
          source: 'la_republica',
          createdAt: new Date().toISOString(),
          rues: { validated: false },
          score: data.lead.score,
          category: data.lead.category,
        }
        setCurrentLead(lead)
        setLeads(prev => [...prev, lead])
        addLead(lead) // Agregar al store
        setStatus(data.queue_status)
        
        // Solicitar siguiente lead automáticamente
        setTimeout(() => getNextLead(), 500)
      } else {
        setError(data.message || 'No hay más leads disponibles')
        setScraping(false)
        console.log(data.message)
      }
    } catch (err) {
      setError(err.message)
      setScraping(false)
      console.error('Error en getNextLead:', err)
    }
  }, [addLead])

  // Aceptar lead
  const acceptLead = useCallback(async (leadId, niche) => {
    try {
      const response = await fetch(
        `${getAPI_URL()}/api/scraper/accept-lead/${leadId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ niche })
        }
      )
      
      if (!response.ok) {
        const contentType = response.headers.get('content-type')
        let errorMsg = `Error ${response.status}: ${response.statusText}`
        if (contentType?.includes('application/json')) {
          try {
            const errorData = await response.json()
            errorMsg = errorData.detail || errorMsg
          } catch (e) {
            // Si no puede parsear JSON, usa el mensaje genérico
          }
        }
        throw new Error(errorMsg)
      }
      
      const data = await response.json()
      
      if (data.success) {
        // Solicitar siguiente lead
        setTimeout(() => getNextLead(), 500)
      } else {
        setError(data.detail || 'Error aceptando lead')
      }
    } catch (err) {
      setError(err.message)
      console.error('Error en acceptLead:', err)
    }
  }, [getNextLead])

  // Rechazar lead
  const rejectLead = useCallback(async () => {
    // Solo pasar al siguiente, no guardar
    setTimeout(() => getNextLead(), 300)
  }, [getNextLead])

  // Obtener estado
  const requestStatus = useCallback(async () => {
    try {
      const response = await fetch(`${getAPI_URL()}/api/scraper/status`)
      
      if (!response.ok) {
        console.error(`Status request failed: ${response.status}`)
        return
      }
      
      const data = await response.json()
      setStatus(data)
    } catch (err) {
      console.error('Error obteniendo estado:', err)
      // No setear error global aquí porque es una solicitud de background
    }
  }, [])

  // Detener scraper
  const stopScraper = useCallback(() => {
    setScraping(false)
    if (wsRef.current) {
      wsRef.current.close()
    }
  }, [])

  return {
    // Estado
    scraping,
    currentLead,
    leads,
    status,
    error,
    selectedNiches,
    targetCount,
    
    // Acciones
    startScraper,
    getNextLead,
    acceptLead,
    rejectLead,
    stopScraper,
    requestStatus
  }
}

export function useLead(leadId) {
  const [lead, setLead] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!leadId) return

    const fetchLead = async () => {
      setLoading(true)
      try {
        const response = await fetch(`${getAPI_URL()}/api/companies/${leadId}`)
        const data = await response.json()
        
        if (data.success) {
          setLead(data.company)
        } else {
          setError(data.detail || 'Lead no encontrado')
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchLead()
  }, [leadId])

  return { lead, loading, error }
}
