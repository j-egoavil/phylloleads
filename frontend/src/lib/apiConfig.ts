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

  // Siempre conectar al puerto 12001 del backend
  // Funciona tanto en localhost como en producción
  return `${protocol}//${hostname}:12001`;
}

export function getWsUrl(): string {
  if (typeof window === 'undefined') {
    return 'ws://localhost:12001';
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';

  // Siempre conectar al puerto 12001 del backend
  return `${wsProtocol}//${hostname}:12001`;
}
