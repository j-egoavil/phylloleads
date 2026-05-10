import React, { useState } from 'react'
import { useLeadScraper } from '../hooks/useLeadScraper'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'

export default function LeadsPage() {
  const {
    scraping,
    currentLead,
    leads,
    status,
    error,
    selectedNiches,
    targetCount,
    startScraper,
    acceptLead,
    rejectLead,
    stopScraper
  } = useLeadScraper()

  const [niches, setNiches] = useState([])
  const [target, setTarget] = useState(50)
  const [showConfig, setShowConfig] = useState(true)

  const handleStart = async () => {
    if (niches.length === 0) {
      alert('Selecciona al menos un nicho')
      return
    }
    setShowConfig(false)
    await startScraper(niches, target)
  }

  const handleAccept = () => {
    if (currentLead) {
      acceptLead(currentLead.id, currentLead.niche)
    }
  }

  const handleReject = () => {
    rejectLead()
  }

  const getCategoryColor = (category) => {
    switch(category) {
      case 'A': return 'bg-green-100 text-green-800'
      case 'B': return 'bg-yellow-100 text-yellow-800'
      case 'C': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100'
    }
  }

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Gestor de Leads</h1>
          <p className="text-gray-600">Scraping automático y calificación de leads en tiempo real</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 text-red-800 rounded-lg">
            {error}
          </div>
        )}

        {/* Panel de Configuración */}
        {showConfig && !scraping && (
          <Card className="mb-6 border-2 border-indigo-200">
            <CardHeader>
              <CardTitle>Configurar Búsqueda</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nichos</label>
                <div className="space-y-2">
                  {['veterinarias', 'restaurantes', 'peluquerías', 'gimnasios', 'consultorios'].map(niche => (
                    <label key={niche} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={niches.includes(niche)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNiches([...niches, niche])
                          } else {
                            setNiches(niches.filter(n => n !== niche))
                          }
                        }}
                        className="mr-2"
                      />
                      <span className="capitalize">{niche}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Cantidad de leads por nicho: {target}
                </label>
                <input
                  type="range"
                  min="10"
                  max="500"
                  step="10"
                  value={target}
                  onChange={(e) => setTarget(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <Button
                onClick={handleStart}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3"
              >
                Iniciar Búsqueda
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Panel en vivo */}
        {scraping && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            
            {/* Lead actual */}
            <div className="lg:col-span-2">
              {currentLead ? (
                <Card className="border-2 border-green-300 shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-2xl">{currentLead.name}</CardTitle>
                      <div className="flex gap-2 items-center">
                        <div className={`px-4 py-1 rounded-full font-bold text-lg ${getCategoryColor(currentLead.category)}`}>
                          {currentLead.category}
                        </div>
                        <div className={`text-3xl font-bold ${getScoreColor(currentLead.score)}`}>
                          {currentLead.score}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-6 space-y-4">
                    
                    {/* Información del lead */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Teléfono</p>
                        <p className="text-lg font-semibold">
                          {currentLead.phone || '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Ciudad</p>
                        <p className="text-lg font-semibold capitalize">
                          {currentLead.city}
                        </p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-sm text-gray-600">Website</p>
                        <p className="text-lg font-semibold break-all">
                          {currentLead.website ? (
                            <a href={currentLead.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                              {currentLead.website}
                            </a>
                          ) : '—'}
                        </p>
                      </div>
                      {currentLead.address && (
                        <div className="col-span-2">
                          <p className="text-sm text-gray-600">Dirección</p>
                          <p className="text-lg">{currentLead.address}</p>
                        </div>
                      )}
                    </div>

                    {/* Desglose de puntuación */}
                    {currentLead.scoring_details && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Desglose de Puntuación:</p>
                        <div className="space-y-1 text-sm">
                          {Object.entries(currentLead.scoring_details).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="capitalize text-gray-600">{key}:</span>
                              <span className="font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Botones de acción */}
                    <div className="flex gap-3 pt-4">
                      <Button
                        onClick={handleAccept}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3"
                      >
                        ✓ Aceptar
                      </Button>
                      <Button
                        onClick={handleReject}
                        className="flex-1 bg-gray-400 hover:bg-gray-500 text-white font-bold py-3"
                      >
                        ✗ Rechazar
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="border-2 border-dashed border-gray-300">
                  <CardContent className="pt-12 pb-12 text-center">
                    <p className="text-gray-500 text-lg">Cargando leads...</p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Panel de estado */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Estado General</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600">Nichos Activos</p>
                    <p className="text-2xl font-bold">{selectedNiches.length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Leads Aceptados</p>
                    <p className="text-2xl font-bold">{leads.length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Target Total</p>
                    <p className="text-2xl font-bold">
                      {selectedNiches.length * targetCount}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Por Nicho</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {status.niches && Object.entries(status.niches).map(([niche, data]) => (
                    <div key={niche} className="text-sm">
                      <p className="font-medium capitalize">{niche}</p>
                      <div className="flex justify-between text-gray-600">
                        <span>{data.sent}/{data.target}</span>
                        <span>{data.queued} en cola</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-green-500 h-2 rounded-full transition-all"
                          style={{
                            width: `${(data.sent / data.target) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Button
                onClick={stopScraper}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2"
              >
                Detener
              </Button>
            </div>
          </div>
        )}

        {/* Historial de leads */}
        {leads.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Leads Aceptados ({leads.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-2 text-left">Nombre</th>
                      <th className="px-4 py-2 text-left">Nicho</th>
                      <th className="px-4 py-2 text-left">Ciudad</th>
                      <th className="px-4 py-2 text-center">Puntuación</th>
                      <th className="px-4 py-2 text-center">Categoría</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.slice(-10).reverse().map(lead => (
                      <tr key={lead.id} className="border-t hover:bg-gray-50">
                        <td className="px-4 py-2 font-medium">{lead.name}</td>
                        <td className="px-4 py-2 capitalize">{lead.niche}</td>
                        <td className="px-4 py-2 capitalize">{lead.city}</td>
                        <td className={`px-4 py-2 text-center font-bold ${getScoreColor(lead.score)}`}>
                          {lead.score}
                        </td>
                        <td className="px-4 py-2 text-center">
                          <span className={`px-3 py-1 rounded-full font-bold ${getCategoryColor(lead.category)}`}>
                            {lead.category}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
