// Configuración centralizada de la API
// Use the VITE_API_URL if provided, otherwise default to the server IP:port
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://10.10.50.26:8000';
// El prefijo se usa en la instancia de axios
export const API_PREFIX = '/api';
