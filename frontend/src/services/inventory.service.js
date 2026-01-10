import api from './api';

export const InventoryService = {
    // === PRODUCTOS ===
    chemicals: {
        getAll: () => api.get('chemicals/'),
        getById: (id) => api.get(`chemicals/${id}/`),
        create: (data) => api.post('chemicals/', data),
        update: (id, data) => api.put(`chemicals/${id}/`, data),
        delete: (id) => api.delete(`chemicals/${id}/`),
        getStockBajo: () => api.get('chemicals/stock_bajo/'),
        getPeligrosos: () => api.get('chemicals/peligrosos/'),
    },
    pipes: {
        getAll: () => api.get('pipes/'),
        getById: (id) => api.get(`pipes/${id}/`),
        create: (data) => api.post('pipes/', data),
        update: (id, data) => api.put(`pipes/${id}/`, data),
        delete: (id) => api.delete(`pipes/${id}/`),
        getByDiameter: (d) => api.get(`pipes/by_diameter/?diametro=${d}`),
    },
    pumps: {
        getAll: () => api.get('pumps/'),
        getById: (id) => api.get(`pumps/${id}/`),
        create: (data) => api.post('pumps/', data),
        update: (id, data) => api.put(`pumps/${id}/`, data),
        delete: (id) => api.delete(`pumps/${id}/`),
    },
    accessories: {
        getAll: () => api.get('accessories/'),
        getById: (id) => api.get(`accessories/${id}/`),
        create: (data) => api.post('accessories/', data),
        update: (id, data) => api.put(`accessories/${id}/`, data),
        delete: (id) => api.delete(`accessories/${id}/`),
    },

    // === AUXILIARES ===
    categories: {
        getAll: () => api.get('categories/'),
    },
    units: {
        getAll: () => api.get('units/'),
    },
    suppliers: {
        getAll: () => api.get('suppliers/'),
    },
    acueductos: {
        getAll: () => api.get('acueductos/'),
    },
    sucursales: {
        getAll: () => api.get('sucursales/'),
        create: (data) => api.post('sucursales/', data),
        update: (id, data) => api.put(`sucursales/${id}/`, data),
        delete: (id) => api.delete(`sucursales/${id}/`),
    },
    organizaciones: {
        getAll: () => api.get('organizaciones/'),
        create: (data) => api.post('organizaciones/', data),
        update: (id, data) => api.put(`organizaciones/${id}/`, data),
        delete: (id) => api.delete(`organizaciones/${id}/`),
    },
    users: {
        getAll: () => api.get('users/'),
        create: (data) => api.post('users/', data),
        update: (id, data) => api.put(`users/${id}/`, data),
        delete: (id) => api.delete(`users/${id}/`),
    },
    stockPipes: {
        getAll: () => api.get('stock-pipes/'),
        create: (data) => api.post('stock-pipes/', data),
        update: (id, data) => api.put(`stock-pipes/${id}/`, data),
        delete: (id) => api.delete(`stock-pipes/${id}/`),
    },
    stockPumps: {
        getAll: () => api.get('stock-pumps/'),
        create: (data) => api.post('stock-pumps/', data),
        update: (id, data) => api.put(`stock-pumps/${id}/`, data),
        delete: (id) => api.delete(`stock-pumps/${id}/`),
    },
    stockAccessories: {
        getAll: () => api.get('stock-accessories/'),
    },

    // === MOVIMIENTOS ===
    movimientos: {
        getAll: (params) => api.get('movimientos/', { params }),
        create: (data) => api.post('movimientos/', data),
    },

    // === REPORTES ===
    reports: {
        dashboardStats: () => api.get('reportes-v2/dashboard_stats/'),
        getMovimientosRecientes: (dias) => api.get(`reportes-v2/movimientos_recientes/?dias=${dias}`),
        getStockPorSucursal: () => api.get('reportes-v2/stock_por_sucursal/'),
        getResumenMovimientos: (dias) => api.get(`reportes-v2/resumen_movimientos/?dias=${dias}`),
    },
    // Alertas
    alertas: {
        getAll: () => api.get('alertas/'),
        create: (data) => api.post('alertas/', data),
        update: (id, data) => api.put(`alertas/${id}/`, data),
        delete: (id) => api.delete(`alertas/${id}/`),
    },

    // Notificaciones
    notificaciones: {
        getAll: () => api.get('notificaciones/'),
        markAsRead: (id) => api.patch(`notificaciones/${id}/`, { leida: true }),
    }
};
