import api from './api';

const ENDPOINTS = {
    VEHICULOS: 'flota/vehiculos/',
    TIPOS: 'flota/tipos-vehiculos/',
    MANTENIMIENTO: 'flota/mantenimiento/',
    ASIGNACIONES: 'flota/asignaciones/',
};

export const FleetService = {
    vehiculos: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.VEHICULOS, { params });
            return response;
        },
        getById: async (id) => {
            const response = await api.get(`${ENDPOINTS.VEHICULOS}${id}/`);
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.VEHICULOS, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.VEHICULOS}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.VEHICULOS}${id}/`);
            return response;
        }
    },
    tipos: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.TIPOS, { params });
            return response;
        }
    },
    mantenimiento: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.MANTENIMIENTO, { params });
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.MANTENIMIENTO, data);
            return response;
        }
    },
    asignaciones: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.ASIGNACIONES, { params });
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.ASIGNACIONES, data);
            return response;
        },
        devolver: async (id, data) => {
            const response = await api.post(`${ENDPOINTS.ASIGNACIONES}${id}/finalizar/`, data);
            return response;
        }
    }
};
