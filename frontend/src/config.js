// Configuración centralizada de la API
// En producción, usar rutas relativas para aprovechar el proxy de Nginx
// En desarrollo, usar la variable de entorno VITE_API_URL
const isDevelopment = import.meta.env.DEV;
export const API_BASE_URL = isDevelopment
    ? (import.meta.env.VITE_API_URL || 'http://localhost:8080')
    : ''; // Ruta relativa en producción (usa el mismo dominio)
export const API_PREFIX = '/api';

