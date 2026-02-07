import api from './api';

const ENDPOINTS = {
    LOGS: 'auditoria/logs/',
};

export const AuditService = {
    logs: {
        getAll: async (params = {}) => {
            const response = await api.get(ENDPOINTS.LOGS, { params });
            return response;
        }
    }
};
