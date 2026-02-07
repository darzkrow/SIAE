import api from './api';

const ENDPOINTS = {
    USERS: 'users/',
};

export const UserService = {
    getAll: async (params = {}) => {
        const response = await api.get(ENDPOINTS.USERS, { params });
        return response;
    },
    getById: async (id) => {
        const response = await api.get(`${ENDPOINTS.USERS}${id}/`);
        return response;
    },
    create: async (data) => {
        const response = await api.post(ENDPOINTS.USERS, data);
        return response;
    },
    update: async (id, data) => {
        const response = await api.put(`${ENDPOINTS.USERS}${id}/`, data);
        return response;
    },
    delete: async (id) => {
        const response = await api.delete(`${ENDPOINTS.USERS}${id}/`);
        return response;
    }
};
