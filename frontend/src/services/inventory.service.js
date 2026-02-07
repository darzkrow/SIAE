import api from './api';

export const InventoryService = {
    // === PRODUCTOS (Inventario) ===
    chemicals: {
        getAll: (params) => api.get('chemicals/', { params }),
        getById: (id) => api.get(`chemicals/${id}/`),
        create: (data) => api.post('chemicals/', data),
        update: (id, data) => api.put(`chemicals/${id}/`, data),
        delete: (id) => api.delete(`chemicals/${id}/`),
        getStockBajo: () => api.get('chemicals/stock_bajo/'),
        getPeligrosos: () => api.get('chemicals/peligrosos/'),
    },
    pipes: {
        getAll: (params) => api.get('pipes/', { params }),
        getById: (id) => api.get(`pipes/${id}/`),
        create: (data) => api.post('pipes/', data),
        update: (id, data) => api.put(`pipes/${id}/`, data),
        delete: (id) => api.delete(`pipes/${id}/`),
        getByDiameter: (d) => api.get(`pipes/by_diameter/?diametro=${d}`),
    },
    pumps: {
        getAll: (params) => api.get('pumps/', { params }),
        getById: (id) => api.get(`pumps/${id}/`),
        create: (data) => api.post('pumps/', data),
        update: (id, data) => api.put(`pumps/${id}/`, data),
        delete: (id) => api.delete(`pumps/${id}/`),
    },
    accessories: {
        getAll: (params) => api.get('accessories/', { params }),
        getById: (id) => api.get(`accessories/${id}/`),
        create: (data) => api.post('accessories/', data),
        update: (id, data) => api.put(`accessories/${id}/`, data),
        delete: (id) => api.delete(`accessories/${id}/`),
    },

    // === AUXILIARES ===
    categories: {
        getAll: () => api.get('catalog/categorias/'),
        create: (data) => api.post('catalog/categorias/', data),
        update: (id, data) => api.put(`catalog/categorias/${id}/`, data),
        delete: (id) => api.delete(`catalog/categorias/${id}/`),
    },
    marcas: {
        getAll: () => api.get('catalog/marcas/'),
        create: (data) => api.post('catalog/marcas/', data),
        update: (id, data) => api.put(`catalog/marcas/${id}/`, data),
        delete: (id) => api.delete(`catalog/marcas/${id}/`),
    },
    tags: {
        getAll: () => api.get('catalog/tags/'),
    },
    units: {
        getAll: () => api.get('units/'),
        create: (data) => api.post('units/', data),
        update: (id, data) => api.put(`units/${id}/`, data),
        delete: (id) => api.delete(`units/${id}/`),
    },
    suppliers: {
        getAll: () => api.get('suppliers/'),
        create: (data) => api.post('suppliers/', data),
        update: (id, data) => api.put(`suppliers/${id}/`, data),
        delete: (id) => api.delete(`suppliers/${id}/`),
    },
    acueductos: {
        getAll: () => api.get('acueductos/'),
        getById: (id) => api.get(`acueductos/${id}/`),
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

    // === STOCK Y MOVIMIENTOS ===
    stock: {
        getAll: (params) => api.get('stock/', { params }),
        getResumen: () => api.get('stock/resumen/'),
        getAlertas: () => api.get('stock/alertas/'),
    },
    movimientos: {
        getAll: (params) => api.get('movimientos/', { params }),
        getById: (id) => api.get(`movimientos/${id}/`),
        create: (data) => api.post('movimientos/', data),
    },

    // === REPORTES ===
    reports: {
        dashboardStats: () => api.get('reportes-v2/dashboard_stats/'),
        getMovimientosRecientes: (dias = 7) => api.get(`reportes-v2/movimientos_recientes/?dias=${dias}`),
        getStockPorSucursal: () => api.get('reportes-v2/stock_por_sucursal/'),
        getResumenMovimientos: (dias = 30) => api.get(`reportes-v2/resumen_movimientos/?dias=${dias}`),
    },

    // === ALERTAS Y NOTIFICACIONES ===
    alertas: {
        getAll: () => api.get('notificaciones/alertas/'),
        create: (data) => api.post('notificaciones/alertas/', data),
        update: (id, data) => api.put(`notificaciones/alertas/${id}/`, data),
        delete: (id) => api.delete(`notificaciones/alertas/${id}/`),
    },
    notificaciones: {
        getAll: () => api.get('notificaciones/notificaciones/'),
        getUnread: () => api.get('notificaciones/notificaciones/?leida=false'),
        markAllRead: () => api.post('notificaciones/notificaciones/marcar_todas_leidas/'),
        markAsRead: (id) => api.patch(`notificaciones/notificaciones/${id}/`, { leida: true }),
    },

    // === GEOGRAFÍA (Rutas en Español) ===
    geography: {
        estados: (params) => api.get('geografia/estados/', { params }),
        municipios: (params) => api.get('geografia/municipios/', { params }),
        parroquias: (params) => api.get('geografia/parroquias/', { params }),
        ubicaciones: (params) => api.get('geografia/ubicaciones/', { params }),
    },

    // === COMPRAS ===
    compras: {
        ordenes: {
            getAll: (params) => api.get('compras/ordenes/', { params }),
            getById: (id) => api.get(`compras/ordenes/${id}/`),
            create: (data) => api.post('compras/ordenes/', data),
            update: (id, data) => api.put(`compras/ordenes/${id}/`, data),
            delete: (id) => api.delete(`compras/ordenes/${id}/`),
            aprobar: (id, step) => api.post(`compras/ordenes/${id}/aprobar/`, { step }),
        },
        items: {
            getAll: (params) => api.get('compras/items/', { params }),
            create: (data) => api.post('compras/items/', data),
            update: (id, data) => api.put(`compras/items/${id}/`, data),
            delete: (id) => api.delete(`compras/items/${id}/`),
        },
    },

    // === AUDITORÍA ===
    auditoria: {
        logs: (params) => api.get('auditoria/logs/', { params }),
        trashBin: (model) => api.get(`auditoria/trash_bin/?model=${model}`),
    },
};
