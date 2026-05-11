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

  // En localhost o 127.0.0.1, conectar al puerto 12001 localmente
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:12001`;
  }

  // En producción, usar string vacío para rutas relativas
  // El nginx redirige /api/* al backend automáticamente
  return '';
}

export function getWsUrl(): string {
  if (typeof window === 'undefined') {
    return 'ws://localhost:12001';
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';

  // En localhost, conectar al puerto 12001
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${wsProtocol}//${hostname}:12001`;
  }

  // En producción, usar rutas relativas con el mismo host
  return `${wsProtocol}//${hostname}`;
}
