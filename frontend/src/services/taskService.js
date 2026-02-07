import api from './api';

const ENDPOINTS = {
    TAREAS: 'tareas/tareas/',
    CATEGORIAS: 'tareas/categorias-tareas/',
    COLUMNAS: 'tareas/columnas-kanban/',
    COMENTARIOS: 'tareas/comentarios/',
};

export const TaskService = {
    tareas: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.TAREAS, { params });
            // Add method to get kanban board if needed? 
            // Usually we fetch all tasks and group them by column in frontend
            return response;
        },
        getById: async (id) => {
            const response = await api.get(`${ENDPOINTS.TAREAS}${id}/`);
            return response;
        },
        create: async (data) => {
            const response = await api.post(ENDPOINTS.TAREAS, data);
            return response;
        },
        update: async (id, data) => {
            const response = await api.put(`${ENDPOINTS.TAREAS}${id}/`, data);
            return response;
        },
        patch: async (id, data) => {
            const response = await api.patch(`${ENDPOINTS.TAREAS}${id}/`, data);
            return response;
        },
        delete: async (id) => {
            const response = await api.delete(`${ENDPOINTS.TAREAS}${id}/`);
            return response;
        },
        addComment: async (tareaId, data) => {
            const response = await api.post(`${ENDPOINTS.TAREAS}${tareaId}/comentarios/`, data);
            return response;
        }
    },
    categorias: {
        getAll: async () => api.get(ENDPOINTS.CATEGORIAS),
    },
    columnas: {
        getAll: async () => api.get(ENDPOINTS.COLUMNAS),
    }
};
