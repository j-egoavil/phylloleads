/**
 * Configuración dinámica de API URL
 * Detecta si estamos en localhost o producción
 */

export function getApiUrl(): string {
  if (typeof window === 'undefined') {
    return 'http://localhost:12001';
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;

  // En localhost, conectar directamente al puerto 12001
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0') {
    return `${protocol}//${hostname}:12001`;
  }

  // En producción (app.orbit.best, etc), usar rutas relativas
  // El nginx redirige /api al backend interno
  return '';
}

export function getWsUrl(): string {
  if (typeof window === 'undefined') {
    return 'ws://localhost:12001';
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';

  // En localhost, conectar directamente al puerto 12001
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0') {
    return `${wsProtocol}//${hostname}:12001`;
  }

  // En producción, construir URL completa con protocolo
  // El nginx redirige /api al backend interno
  return `${wsProtocol}//${hostname}`;
}
