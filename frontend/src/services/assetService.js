import api from './api';

const ENDPOINTS = {
    MATERIALES: 'activos/materiales/',
    ACTIVOS_FIJOS: 'activos/activos-fijos/',
};

export const AssetService = {
    materiales: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.MATERIALES, { params });
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.MATERIALES, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.MATERIALES}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.MATERIALES}${id}/`);
            return response;
        }
    },
    activosFijos: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.ACTIVOS_FIJOS, { params });
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.ACTIVOS_FIJOS, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.ACTIVOS_FIJOS}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.ACTIVOS_FIJOS}${id}/`);
            return response;
        }
    }
};
