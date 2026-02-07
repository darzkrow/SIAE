import api from './api';

const ENDPOINT = 'movimientos/';

export const MovementService = {
    getAll: async (params = {}) => {
        const response = await api.get(ENDPOINT, { params });
        return response;
    },
    getById: async (id) => {
        const response = await api.get(`${ENDPOINT}${id}/`);
        return response;
    },
    create: async (data) => {
        const response = await api.post(ENDPOINT, data);
        return response;
    },
    // Movements generally shouldn't be updated or deleted directly to maintain audit trail, 
    // but specific corrections might be allowed.
    update: async (id, data) => {
        const response = await api.put(`${ENDPOINT}${id}/`, data);
        return response;
    },
    delete: async (id) => {
        const response = await api.delete(`${ENDPOINT}${id}/`);
        return response;
    }
};
