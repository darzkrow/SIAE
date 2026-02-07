import api from './api';

const ENDPOINTS = {
    UNIDADES: 'products/unidades/',
    QUIMICOS: 'products/quimicos/',
    TUBERIAS: 'products/tuberias/',
    EQUIPOS: 'products/equipos/',
    ACCESORIOS: 'products/accesorios/',
};

const createCrudService = (endpoint) => ({
    getAll: async (params = {}) => {
        const response = await api.get(endpoint, { params });
        return response;
    },
    getById: async (id) => {
        const response = await api.get(`${endpoint}${id}/`);
        return response;
    },
    create: async (data) => {
        const response = await api.post(endpoint, data);
        return response;
    },
    update: async (id, data) => {
        const response = await api.put(`${endpoint}${id}/`, data);
        return response;
    },
    delete: async (id) => {
        const response = await api.delete(`${endpoint}${id}/`);
        return response;
    }
});

export const ProductService = {
    unidades: createCrudService(ENDPOINTS.UNIDADES),
    quimicos: createCrudService(ENDPOINTS.QUIMICOS),
    tuberias: createCrudService(ENDPOINTS.TUBERIAS),
    equipos: createCrudService(ENDPOINTS.EQUIPOS),
    accesorios: createCrudService(ENDPOINTS.ACCESORIOS),
};
