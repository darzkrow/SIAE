import api from './api';

export const InventoryService = {
    // === PRODUCTOS ===
    chemicals: {
        getAll: () => api.get('/api/chemicals/'),
        getById: (id) => api.get(`/api/chemicals/${id}/`),
        create: (data) => api.post('/api/chemicals/', data),
        update: (id, data) => api.put(`/api/chemicals/${id}/`, data),
        delete: (id) => api.delete(`/api/chemicals/${id}/`),
        getStockBajo: () => api.get('/api/chemicals/stock_bajo/'),
        getPeligrosos: () => api.get('/api/chemicals/peligrosos/'),
    },
    pipes: {
        getAll: () => api.get('/api/pipes/'),
        getById: (id) => api.get(`/api/pipes/${id}/`),
        create: (data) => api.post('/api/pipes/', data),
        update: (id, data) => api.put(`/api/pipes/${id}/`, data),
        delete: (id) => api.delete(`/api/pipes/${id}/`),
        getByDiameter: (d) => api.get(`/api/pipes/by_diameter/?diametro=${d}`),
    },
    pumps: {
        getAll: () => api.get('/api/pumps/'),
        getById: (id) => api.get(`/api/pumps/${id}/`),
        create: (data) => api.post('/api/pumps/', data),
        update: (id, data) => api.put(`/api/pumps/${id}/`, data),
        delete: (id) => api.delete(`/api/pumps/${id}/`),
    },
    accessories: {
        getAll: () => api.get('/api/accessories/'),
        getById: (id) => api.get(`/api/accessories/${id}/`),
        create: (data) => api.post('/api/accessories/', data),
        update: (id, data) => api.put(`/api/accessories/${id}/`, data),
        delete: (id) => api.delete(`/api/accessories/${id}/`),
    },

    // === AUXILIARES ===
    categories: {
        getAll: () => api.get('/api/categories/'),
    },
    units: {
        getAll: () => api.get('/api/units/'),
    },
    suppliers: {
        getAll: () => api.get('/api/suppliers/'),
    },
    acueductos: {
        getAll: () => api.get('/api/acueductos/'),
    },
    sucursales: {
        getAll: () => api.get('/api/sucursales/'),
    },

    // === MOVIMIENTOS ===
    movimientos: {
        getAll: (params) => api.get('/api/movimientos/', { params }),
        create: (data) => api.post('/api/movimientos/', data),
    },

    // === REPORTES ===
    reports: {
        dashboardStats: () => api.get('/api/reportes-v2/dashboard_stats/'),
    },
    // Alertas
    alertas: {
        getAll: () => api.get('/api/alertas/'),
        create: (data) => api.post('/api/alertas/', data),
        update: (id, data) => api.put(`/api/alertas/${id}/`, data),
        delete: (id) => api.delete(`/api/alertas/${id}/`),
    },

    // Notificaciones
    notificaciones: {
        getAll: () => api.get('/api/notificaciones/'),
        markAsRead: (id) => api.patch(`/api/notificaciones/${id}/`, { leida: true }),
    }
};
