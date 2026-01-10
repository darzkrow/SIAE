import axios from 'axios';
import { API_BASE_URL, API_PREFIX } from '../config';

// Limpiar la URL base y asegurar que el prefijo se asigne correctamente
const getBaseURL = () => {
    let base = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
    let prefix = API_PREFIX.startsWith('/') ? API_PREFIX : `/${API_PREFIX}`;

    // Evitar duplicación si la base ya tiene el prefijo (caso común en despliegues)
    if (base.endsWith(prefix)) {
        return `${base}/`;
    }

    return `${base}${prefix}/`;
};

const api = axios.create({
    baseURL: getBaseURL(),
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para agregar token (si existe)
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token'); // Ajustar según donde se guarde el token
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;
