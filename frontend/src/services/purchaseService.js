import api from './api';

const ENDPOINTS = {
    ORDENES: 'compras/ordenes/',
    ITEMS: 'compras/items/',
};

export const PurchaseService = {
    ordenes: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.ORDENES, { params });
            return response;
        },
        getById: async (id) => {
            const response = await api.get(`${ENDPOINTS.ORDENES}${id}/`);
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.ORDENES, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.ORDENES}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.ORDENES}${id}/`);
            return response;
        },
        aprobar: async (id) => {
            const response = await api.post(`${ENDPOINTS.ORDENES}${id}/aprobar/`);
            return response;
        },
        rechazar: async (id) => {
            const response = await api.post(`${ENDPOINTS.ORDENES}${id}/rechazar/`);
            return response;
        }
    },
    items: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.ITEMS, { params });
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.ITEMS, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.ITEMS}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.ITEMS}${id}/`);
            return response;
        }
    }
};
