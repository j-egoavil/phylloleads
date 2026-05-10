"""
Hook de React para integración con API de Phylloleads
- Inicia scraper
- Obtiene leads en tiempo real
- Marca leads como aceptados
- Actualiza estado
"""

import { useState, useCallback, useEffect, useRef } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useLeadScraper() {
  const [scraping, setScraping] = useState(false)
  const [leads, setLeads] = useState([])
  const [currentLead, setCurrentLead] = useState(null)
  const [status, setStatus] = useState({})
  const [selectedNiches, setSelectedNiches] = useState([])
  const [targetCount, setTargetCount] = useState(50)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  // Conectar WebSocket
  useEffect(() => {
    if (scraping) {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const wsUrl = `${protocol}://${window.location.host}/api/scraper/ws`
      
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket conectado')
        requestStatus()
      }
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        
        if (message.type === 'status_update') {
          setStatus(message.data)
        } else if (message.type === 'new_lead') {
          setCurrentLead(message.lead)
          setLeads(prev => [...prev, message.lead])
        } else if (message.type === 'lead_accepted') {
          setStatus(message.status)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('Error en conexión WebSocket')
      }
      
      ws.onclose = () => {
        console.log('WebSocket desconectado')
      }
      
      wsRef.current = ws
      
      return () => {
        if (wsRef.current) {
          wsRef.current.close()
        }
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
      
      const response = await fetch(`${API_URL}/api/scraper/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          niches: niches,
          target_count: target,
          min_category: 'C'
        })
      })
      
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
      const response = await fetch(`${API_URL}/api/scraper/next-lead`)
      const data = await response.json()
      
      if (data.success) {
        setCurrentLead(data.lead)
        setStatus(data.queue_status)
      } else {
        console.log(data.message)
      }
    } catch (err) {
      setError(err.message)
    }
  }, [])

  // Aceptar lead
  const acceptLead = useCallback(async (leadId, niche) => {
    try {
      const response = await fetch(
        `${API_URL}/api/scraper/accept-lead/${leadId}?niche=${niche}`,
        { method: 'POST' }
      )
      
      const data = await response.json()
      
      if (data.success) {
        // Solicitar siguiente lead
        setTimeout(() => getNextLead(), 500)
      }
    } catch (err) {
      setError(err.message)
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
      const response = await fetch(`${API_URL}/api/scraper/status`)
      const data = await response.json()
      setStatus(data)
    } catch (err) {
      console.error('Error obteniendo estado:', err)
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
        const response = await fetch(`${API_URL}/api/companies/${leadId}`)
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
