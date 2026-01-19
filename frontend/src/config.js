/**
 * Configuración centralizada de la API
 * Implementa el patrón de punto único de modificación.
 */

// En producción y desarrollo con Docker, usamos rutas relativas.
// Nginx se encarga de redirigir /api/* al contenedor backend:8000
const isDevelopment = import.meta.env.DEV && !import.meta.env.VITE_DOCKER;

export const API_BASE_URL = isDevelopment
    ? (import.meta.env.VITE_API_URL || 'http://localhost:8000')
    : ''; // Ruta relativa para producción/docker (usa el mismo dominio que el frontend)

export const API_PREFIX = '/api';

/**
 * Función auxiliar para obtener la URL completa de la API
 * Evita duplicación de slashes y centraliza la lógica de construcción de URLs.
 */
export const getApiUrl = (endpoint = '') => {
    const cleanBase = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
    const cleanPrefix = API_PREFIX.startsWith('/') ? API_PREFIX : `/${API_PREFIX}`;
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    return `${cleanBase}${cleanPrefix}${cleanEndpoint}`;
};
