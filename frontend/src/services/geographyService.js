import api from './api';

const ENDPOINTS = {
    ESTADOS: 'geografia/estados/',
    MUNICIPIOS: 'geografia/municipios/',
    PARROQUIAS: 'geografia/parroquias/',
    UBICACIONES: 'geografia/ubicaciones/',
    ACUEDUCTOS: 'geografia/acueductos/', // If moved here
};

export const GeographyService = {
    estados: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.ESTADOS, { params });
            return response;
        }
    },
    municipios: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.MUNICIPIOS, { params });
            return response;
        }
    },
    parroquias: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.PARROQUIAS, { params });
            return response;
        }
    },
    ubicaciones: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.UBICACIONES, { params });
            return response;
        }
    },
    acueductos: {
        getAll: async (params = {}) => {
            const response = await api.get('acueductos/', { params }); // Keep original path if not changed in backend or use new if moved
            return response;
        }
    }
};
