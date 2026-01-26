/**
 * AdminLTE3 Configuration
 * This file contains the configuration for AdminLTE3 integration
 */

export const adminLTEConfig = {
  theme: 'light', // 'light' | 'dark' | 'auto'
  sidebar: {
    collapsed: false,
    fixed: true,
    mini: false
  },
  navbar: {
    fixed: true,
    search: true,
    notifications: true
  },
  layout: {
    boxed: false,
    topNav: false,
    sidebarMini: true
  },
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    info: '#17a2b8',
    warning: '#ffc107',
    danger: '#dc3545',
    light: '#f8f9fa',
    dark: '#343a40'
  },
  charts: {
    defaultOptions: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      }
    }
  }
}

export const dashboardWidgetTypes = {
  CHART: 'chart',
  METRIC: 'metric',
  TABLE: 'table',
  CUSTOM: 'custom'
}

export const notificationTypes = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
}

export default adminLTEConfig