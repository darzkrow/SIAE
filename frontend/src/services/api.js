import axios from 'axios';
import { getApiUrl } from '../config';

// Instancia centralizada de Axios
// Todas las llamadas al backend pasan por aquí
const api = axios.create({
    baseURL: getApiUrl(), // Utiliza la URL centralizada (punto único de modificación)
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para inyectar el token de autenticación
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para manejar errores globales (ej: 401 Unauthorized)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Opcional: Redirigir al login o limpiar sesión
            // localStorage.removeItem('token');
            // window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
