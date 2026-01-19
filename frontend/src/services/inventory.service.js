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
        // Catalogo app
        getAll: () => api.get('catalog/categorias/'),
    },
    marcas: {
        getAll: () => api.get('catalog/marcas/'),
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
        // Notificaciones app
        getAll: () => api.get('notificaciones/alertas/'),
        create: (data) => api.post('notificaciones/alertas/', data),
        update: (id, data) => api.put(`notificaciones/alertas/${id}/`, data),
        delete: (id) => api.delete(`notificaciones/alertas/${id}/`),
    },

    // Notificaciones
    notificaciones: {
        getAll: () => api.get('notificaciones/notificaciones/'),
        markAsRead: (id) => api.patch(`notificaciones/notificaciones/${id}/`, { leida: true }),
    },

    // === GEOGRAFÍA ===
    geography: {
        states: () => api.get('geography/states/'),
        municipalities: () => api.get('geography/municipalities/'),
        parishes: () => api.get('geography/parishes/'),
        ubicaciones: () => api.get('geography/ubicaciones/'),
    },

    // === COMPRAS ===
    compras: {
        ordenes: {
            getAll: () => api.get('compras/ordenes/'),
            getById: (id) => api.get(`compras/ordenes/${id}/`),
            create: (data) => api.post('compras/ordenes/', data),
            update: (id, data) => api.put(`compras/ordenes/${id}/`, data),
            delete: (id) => api.delete(`compras/ordenes/${id}/`),
        },
        items: {
            getAll: () => api.get('compras/items/'),
            getById: (id) => api.get(`compras/items/${id}/`),
            create: (data) => api.post('compras/items/', data),
            update: (id, data) => api.put(`compras/items/${id}/`, data),
            delete: (id) => api.delete(`compras/items/${id}/`),
        },
    },

    // === AUDITORÍA ===
    auditoria: {
        logs: () => api.get('auditoria/logs/'),
    },
};
