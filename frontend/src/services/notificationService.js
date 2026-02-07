import api from './api';

const ENDPOINTS = {
    NOTIFICACIONES: 'notificaciones/notificaciones/',
    ALERTAS: 'notificaciones/alertas/',
};

export const NotificationService = {
    notificaciones: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.NOTIFICACIONES, { params });
            return response;
        },
        markAsRead: async (id) => {
            const response = await api.patch(`${ENDPOINTS.NOTIFICACIONES}${id}/`, { leida: true });
            return response;
        },
        markAllAsRead: async () => {
            // Assuming backend supports this or iterate
            // For now just list
            return { message: "Not implemented yet in backend" };
        }
    },
    alertas: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.ALERTAS, { params });
            return response;
        }
    }
};
