import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Bell, CheckCircle, AlertCircle, Info, AlertTriangle, Trash2 } from 'lucide-react';

export default function NotificacionesList() {
    // Keep useNotifications for local toasts if needed, or remove if not used for actions
    const { addNotification } = useNotifications();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, unread, read

    useEffect(() => {
        fetchNotifications();
    }, []);

    const fetchNotifications = async () => {
        try {
            const res = await InventoryService.notificaciones.getAll();
            setNotifications(res.data.results || res.data);
        } catch (error) {
            console.error(error);
            // addNotification({ type: 'error', message: 'Error cargando notificaciones' });
        } finally {
            setLoading(false);
        }
    };

    const handleMarkAsRead = async (id) => {
        try {
            await InventoryService.notificaciones.markAsRead(id);
            fetchNotifications(); // Reload
        } catch (error) {
            console.error(error);
        }
    }

    const filteredNotifications = notifications.filter(notification => {
        if (filter === 'unread') return !notification.leida; // Backend field usually 'leida' or 'read'
        if (filter === 'read') return notification.leida;
        return true;
    });

    const getIcon = (type) => {
        switch (type) {
            case 'success':
            case 'EXITO':
                return <CheckCircle size={20} className="text-success" />;
            case 'error':
            case 'ERROR':
                return <AlertCircle size={20} className="text-danger" />;
            case 'warning':
            case 'ADVERTENCIA':
                return <AlertTriangle size={20} className="text-warning" />;
            case 'info':
            default:
                return <Info size={20} className="text-info" />;
        }
    };

    const getTimeAgo = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleString();
    };

    return (
        <div>
            {/* Header */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 className="h3 mb-0">
                                <Bell className="mr-2" size={24} />
                                Centro de Notificaciones
                            </h1>
                            <p className="text-muted mb-0">
                                Gestiona todas tus notificaciones del sistema
                            </p>
                        </div>
                        <div>
                            <button
                                className="btn btn-outline-secondary"
                                onClick={() => { }}
                                disabled={true}
                            >
                                <CheckCircle size={16} className="mr-2" />
                                Marcar todas como leídas
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats */}
            <div className="row mb-4">
                <div className="col-lg-4 col-md-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Total Notificaciones"
                        value={notifications.length}
                        icon={Bell}
                        color="info"
                    />
                </div>
                <div className="col-lg-4 col-md-6">
                    <AdminLTEWidget
                        type="metric"
                        title="No Leídas"
                        value={notifications.filter(n => !n.leida).length}
                        icon={AlertCircle}
                        color="warning"
                    />
                </div>
                <div className="col-lg-4 col-md-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Leídas"
                        value={notifications.filter(n => n.leida).length}
                        icon={CheckCircle}
                        color="success"
                    />
                </div>
            </div>

            {/* Filters */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="btn-group" role="group">
                        <button
                            type="button"
                            className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
                            onClick={() => setFilter('all')}
                        >
                            Todas ({notifications.length})
                        </button>
                        <button
                            type="button"
                            className={`btn ${filter === 'unread' ? 'btn-primary' : 'btn-outline-primary'}`}
                            onClick={() => setFilter('unread')}
                        >
                            No Leídas ({notifications.filter(n => !n.leida).length})
                        </button>
                        <button
                            type="button"
                            className={`btn ${filter === 'read' ? 'btn-primary' : 'btn-outline-primary'}`}
                            onClick={() => setFilter('read')}
                        >
                            Leídas ({notifications.filter(n => n.leida).length})
                        </button>
                    </div>
                </div>
            </div>

            {/* Notifications List */}
            <AdminLTEWidget
                type="card"
                title="Notificaciones"
                color="primary"
            >
                {filteredNotifications.length === 0 ? (
                    <div className="text-center py-5">
                        <Bell size={48} className="text-muted mb-3" />
                        <h5 className="text-muted">No hay notificaciones</h5>
                        <p className="text-muted">
                            {filter === 'all'
                                ? 'No tienes notificaciones en este momento.'
                                : filter === 'unread'
                                    ? 'No tienes notificaciones sin leer.'
                                    : 'No tienes notificaciones leídas.'
                            }
                        </p>
                    </div>
                ) : (
                    <div className="list-group list-group-flush">
                        {filteredNotifications.map((notification) => (
                            <div
                                key={notification.id}
                                className={`list-group-item list-group-item-action ${!notification.read ? 'bg-light' : ''}`}
                            >
                                <div className="d-flex align-items-start">
                                    <div className="mr-3 mt-1">
                                        {getIcon(notification.type)}
                                    </div>
                                    <div className="flex-grow-1">
                                        <div className="d-flex justify-content-between align-items-start">
                                            <h6 className="mb-1 font-weight-bold">
                                                {notification.titulo || notification.title}
                                                {!notification.leida && (
                                                    <span className="badge badge-primary badge-sm ml-2">Nuevo</span>
                                                )}
                                            </h6>
                                            <small className="text-muted">
                                                {getTimeAgo(notification.created_at || notification.fecha_creacion)}
                                            </small>
                                        </div>
                                        <p className="mb-1 text-muted">
                                            {notification.mensaje || notification.message}
                                        </p>
                                        {!notification.leida && (
                                            <button
                                                className="btn btn-sm btn-link pl-0"
                                                onClick={() => handleMarkAsRead(notification.id)}
                                            >
                                                Marcar como leída
                                            </button>
                                        )}
                                        {notification.actions && (
                                            <div className="mt-2">
                                                {notification.actions.map((action, index) => (
                                                    <button
                                                        key={index}
                                                        type="button"
                                                        className={`btn btn-sm ${action.variant || 'btn-outline-secondary'} mr-2`}
                                                        onClick={action.onClick}
                                                    >
                                                        {action.label}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </AdminLTEWidget>
        </div>
    );
}
