import api from './api';

const ENDPOINT = 'proveedores/';

export const SupplierService = {
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
    update: async (id, data) => {
        const response = await api.put(`${ENDPOINT}${id}/`, data);
        return response;
    },
    delete: async (id) => {
        const response = await api.delete(`${ENDPOINT}${id}/`);
        return response;
    }
};
