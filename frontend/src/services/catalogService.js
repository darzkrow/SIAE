import api from './api';

const ENDPOINTS = {
    CATEGORIAS: 'catalog/categorias/',
    MARCAS: 'catalog/marcas/',
    TAGS: 'catalog/tags/',
};

export const CatalogService = {
    categorias: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.CATEGORIAS, { params });
            return response;
        },
        getById: async (id) => {
            const response = await api.get(`${ENDPOINTS.CATEGORIAS}${id}/`);
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.CATEGORIAS, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.CATEGORIAS}${id}/`, data);
            return response;
        },
        patch: async (id, data) => {
            const response = await api.patch(`${ENDPOINTS.CATEGORIAS}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.CATEGORIAS}${id}/`);
            return response;
        }
    },
    marcas: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.MARCAS, { params });
            return response;
        },
        getById: async (id) => {
            const response = await api.get(`${ENDPOINTS.MARCAS}${id}/`);
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.MARCAS, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.MARCAS}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.MARCAS}${id}/`);
            return response;
        }
    },
    tags: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.TAGS, { params });
            return response;
        }
    }
};
