/**
 * GUÍA DE INTEGRACIÓN - FRONTEND CON API DE SCRAPER
 * 
 * Este archivo contiene ejemplos de cómo integrar el scraper en tu
 * aplicación React/Frontend
 */

// ============================================================================
// 1. CONFIGURACIÓN BASE
// ============================================================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Crear instancia de cliente HTTP
const apiClient = {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error en ${endpoint}:`, error);
      throw error;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// ============================================================================
// 2. SERVICIO DE SCRAPER
// ============================================================================

export const scraperService = {
  /**
   * Realiza búsqueda sincrónica (espera resultado)
   * Útil para búsquedas rápidas (1-2 páginas)
   */
  async searchCompanies(niche, pages = 1) {
    try {
      const response = await apiClient.post('/api/search', {
        niche: niche.trim(),
        pages: Math.min(Math.max(pages, 1), 10),
      });

      if (!response.success) {
        throw new Error(response.message || 'Error en la búsqueda');
      }

      return response;
    } catch (error) {
      console.error('Error en búsqueda sincrónica:', error);
      throw error;
    }
  },

  /**
   * Realiza búsqueda asincrónica (en background)
   * Ideal para búsquedas largas (3+ páginas)
   * Retorna inmediatamente, búsqueda continúa en servidor
   */
  async searchCompaniesAsync(niche, pages = 1) {
    try {
      const response = await apiClient.post('/api/search-async', {
        niche: niche.trim(),
        pages: Math.min(Math.max(pages, 1), 10),
      });

      if (!response.success) {
        throw new Error(response.message || 'Error iniciando búsqueda');
      }

      return response;
    } catch (error) {
      console.error('Error en búsqueda asincrónica:', error);
      throw error;
    }
  },

  /**
   * Obtiene empresas guardadas de un nicho
   * Se usa para recuperar resultados de búsquedas anteriores
   */
  async getCompaniesByNiche(niche, limit = 100) {
    try {
      const response = await apiClient.get(
        `/api/companies/${encodeURIComponent(niche)}?limit=${limit}`
      );

      if (!response.success) {
        throw new Error('Error obteniendo empresas');
      }

      return response.companies || [];
    } catch (error) {
      console.error('Error obteniendo empresas:', error);
      throw error;
    }
  },

  /**
   * Obtiene estadísticas generales del scraper
   */
  async getStatistics() {
    try {
      return await apiClient.get('/api/stats');
    } catch (error) {
      console.error('Error obteniendo estadísticas:', error);
      throw error;
    }
  },

  /**
   * Verifica si la API está disponible
   */
  async healthCheck() {
    try {
      const response = await apiClient.get('/health');
      return response.status === 'healthy';
    } catch (error) {
      console.error('API no disponible:', error);
      return false;
    }
  },
};

// ============================================================================
// 3. REACT HOOK - PARA USO EN COMPONENTES
// ============================================================================

import { useState, useCallback } from 'react';

export function useScraperSearch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [progress, setProgress] = useState(0);

  const search = useCallback(async (niche, pages = 1, useAsync = false) => {
    setLoading(true);
    setError(null);
    setData(null);
    setProgress(0);

    try {
      let response;

      if (useAsync) {
        // Búsqueda asincrónica
        response = await scraperService.searchCompaniesAsync(niche, pages);
        setProgress(50); // 50% inicial

        // Esperar resultados con polling
        let attempts = 0;
        const maxAttempts = 120; // 10 minutos (5s * 120)

        while (attempts < maxAttempts) {
          await new Promise((resolve) => setTimeout(resolve, 5000)); // Esperar 5s

          const companies = await scraperService.getCompaniesByNiche(niche);

          if (companies.length > 0) {
            setProgress(100);
            setData({
              success: true,
              niche,
              total_companies: companies.length,
              companies,
              message: `Búsqueda completada: ${companies.length} empresas`,
            });
            setLoading(false);
            return;
          }

          setProgress(50 + (attempts / maxAttempts) * 50);
          attempts++;
        }

        throw new Error('Timeout esperando resultados de búsqueda');
      } else {
        // Búsqueda sincrónica
        response = await scraperService.searchCompanies(niche, pages);
        setProgress(100);
        setData(response);
      }

      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      setProgress(0);
    }
  }, []);

  return { loading, error, data, progress, search };
}

// ============================================================================
// 4. COMPONENTE REACT - BUSCADOR
// ============================================================================

import React, { useState, useEffect } from 'react';

export function SearchForm() {
  const [niche, setNiche] = useState('');
  const [pages, setPages] = useState(1);
  const [useAsync, setUseAsync] = useState(false);
  const { loading, error, data, progress, search } = useScraperSearch();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!niche.trim()) {
      alert('Por favor ingresa un nicho');
      return;
    }
    await search(niche, pages, useAsync);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSearch}>
        <div className="form-group">
          <label htmlFor="niche">Nicho de búsqueda:</label>
          <input
            id="niche"
            type="text"
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
            placeholder="ej: veterinarias, restaurantes, farmacias"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="pages">Páginas a scrapear:</label>
          <input
            id="pages"
            type="number"
            min="1"
            max="10"
            value={pages}
            onChange={(e) => setPages(parseInt(e.target.value))}
            disabled={loading}
          />
        </div>

        <div className="form-group checkbox">
          <label>
            <input
              type="checkbox"
              checked={useAsync}
              onChange={(e) => setUseAsync(e.target.checked)}
              disabled={loading}
            />
            Búsqueda en background (para muchas páginas)
          </label>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? `Buscando... ${Math.round(progress)}%` : 'Buscar Empresas'}
        </button>
      </form>

      {/* Barra de progreso */}
      {loading && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      )}

      {/* Mostrar errores */}
      {error && <div className="error-message">❌ Error: {error}</div>}

      {/* Mostrar resultados */}
      {data && !loading && (
        <div className="results">
          <h2>Resultados: {data.total_companies} empresas</h2>
          {data.companies && data.companies.length > 0 && (
            <CompaniesTable companies={data.companies} />
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// 5. COMPONENTE - TABLA DE EMPRESAS
// ============================================================================

export function CompaniesTable({ companies }) {
  const [sortBy, setSortBy] = useState('name');
  const [filterCity, setFilterCity] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Obtener ciudades únicas
  const cities = [...new Set(companies.map((c) => c.city))];
  const statuses = ['Activa', 'Inactiva'];

  // Filtrar y ordenar
  let filtered = companies.filter((c) => {
    if (filterCity && c.city !== filterCity) return false;
    if (filterStatus && c.status !== filterStatus) return false;
    return true;
  });

  filtered.sort((a, b) => {
    const aVal = a[sortBy] || '';
    const bVal = b[sortBy] || '';
    return aVal.toString().localeCompare(bVal.toString());
  });

  return (
    <div className="companies-table-container">
      {/* Controles de filtro */}
      <div className="filters">
        <select
          value={filterCity}
          onChange={(e) => setFilterCity(e.target.value)}
        >
          <option value="">Todas las ciudades</option>
          {cities.map((city) => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">Todos los estados</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>

        <span className="result-count">{filtered.length} resultados</span>
      </div>

      {/* Tabla */}
      <table className="companies-table">
        <thead>
          <tr>
            <th onClick={() => setSortBy('name')}>
              Nombre {sortBy === 'name' && '↓'}
            </th>
            <th>RUES</th>
            <th onClick={() => setSortBy('city')}>
              Ciudad {sortBy === 'city' && '↓'}
            </th>
            <th>Estado</th>
            <th>Tamaño</th>
            <th>Enlace</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((company) => (
            <tr key={company.id || company.url}>
              <td>{company.name}</td>
              <td>{company.rues || '-'}</td>
              <td>{company.city}</td>
              <td>
                <span className={`status ${company.is_active ? 'active' : 'inactive'}`}>
                  {company.status}
                </span>
              </td>
              <td>{company.company_size}</td>
              <td>
                <a href={company.url} target="_blank" rel="noopener noreferrer">
                  Ver →
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================================================
// 6. COMPONENTE - ESTADÍSTICAS
// ============================================================================

import React, { useEffect, useState } from 'react';

export function Statistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await scraperService.getStatistics();
        setStats(data);
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
    // Recargar cada 30 segundos
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !stats) {
    return <div>Cargando estadísticas...</div>;
  }

  return (
    <div className="statistics">
      <h2>Estadísticas del Scraper</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.total_companies}</h3>
          <p>Empresas Total</p>
        </div>
        <div className="stat-card">
          <h3>{stats.active_companies}</h3>
          <p>Empresas Activas</p>
        </div>
        <div className="stat-card">
          <h3>{stats.inactive_companies}</h3>
          <p>Empresas Inactivas</p>
        </div>
        <div className="stat-card">
          <h3>{stats.companies_by_niche.length}</h3>
          <p>Nichos Scrapeados</p>
        </div>
      </div>

      {stats.companies_by_niche.length > 0 && (
        <div className="niches-breakdown">
          <h3>Empresas por Nicho:</h3>
          <ul>
            {stats.companies_by_niche.slice(0, 10).map((niche) => (
              <li key={niche.niche}>
                {niche.niche}: <strong>{niche.count}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// 7. ESTILOS CSS (OPCIONAL)
// ============================================================================

const styles = `
.search-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox input {
  width: auto;
  margin-right: 8px;
}

button {
  background: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

button:hover {
  background: #0056b3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #eee;
  border-radius: 4px;
  margin: 15px 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #28a745;
  transition: width 0.3s ease;
}

.error-message {
  padding: 10px;
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin: 15px 0;
}

.results {
  margin-top: 20px;
}

.companies-table-container {
  margin-top: 20px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.result-count {
  padding: 8px 12px;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}

.companies-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.companies-table th {
  background: #f0f0f0;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
}

.companies-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.companies-table tr:hover {
  background: #f9f9f9;
}

.status {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.status.active {
  background: #d4edda;
  color: #155724;
}

.status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.statistics {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  font-size: 32px;
  color: #007bff;
  margin: 0;
}

.stat-card p {
  color: #666;
  margin: 5px 0 0 0;
}
`;

export default styles;
