import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';
import { 
  Package, 
  Droplets, 
  Activity, 
  AlertCircle, 
  TrendingUp, 
  Plus, 
  Minus, 
  ArrowRight, 
  Calendar, 
  Users, 
  BarChart2, 
  PieChart, 
  ListChecks,
  DollarSign,
  Building
} from 'lucide-react';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import Swal from 'sweetalert2';

export default function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const { addNotification } = useNotifications();
    const [stats, setStats] = useState(null);
    const [movimientos, setMovimientos] = useState([]);
    const [alertas, setAlertas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const hasShownWelcome = useRef(false);

    // Clear welcome notification when component unmounts
    useEffect(() => {
        return () => {
            // Reset welcome flag when component unmounts
            hasShownWelcome.current = false;
        };
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, movRes, alertasRes] = await Promise.all([
                    InventoryService.reports.dashboardStats(),
                    InventoryService.movimientos.getAll({ limit: 5, ordering: '-fecha_movimiento' }),
                    InventoryService.alertas.getAll({ limit: 5 })
                ]);

                setStats(statsRes.data);
                setMovimientos(movRes.data.results || movRes.data);
                setAlertas(alertasRes.data.results || alertasRes.data);
                
                // Show welcome notification only once per session
                const welcomeKey = `dashboard-welcome-${user?.id || 'unknown'}`;
                if (!sessionStorage.getItem(welcomeKey) && !hasShownWelcome.current) {
                    hasShownWelcome.current = true;
                    addNotification({
                        type: 'success',
                        title: '¡Bienvenido!',
                        message: `Dashboard cargado correctamente para ${user?.username}`,
                        duration: 3000
                    });
                    sessionStorage.setItem(welcomeKey, 'true');
                }
            } catch (err) {
                console.error("Error fetching dashboard data", err);
                const errorMessage = "No se pudieron cargar los datos del dashboard. Verifique la conexión con el servidor.";
                setError(errorMessage);
                
                addNotification({
                    type: 'error',
                    title: 'Error de conexión',
                    message: errorMessage,
                    duration: 5000
                });
            } finally {
                setLoading(false);
            }
        };
        
        // Only fetch data if user is available
        if (user) {
            fetchData();
        }
    }, [user?.id]); // Only depend on user ID to prevent unnecessary re-renders

    const handleQuickAction = (action) => {
        if (action === 'entrada') {
            navigate('/movimientos', { state: { openModal: true, type: 'ENTRADA' } });
        } else if (action === 'salida') {
            navigate('/movimientos', { state: { openModal: true, type: 'SALIDA' } });
        } else if (action === 'ajuste') {
            navigate('/movimientos', { state: { openModal: true, type: 'AJUSTE' } });
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
                <div className="text-center">
                    <div className="spinner-border text-primary" role="status">
                        <span className="sr-only">Cargando...</span>
                    </div>
                    <p className="mt-3 text-muted">Cargando dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-danger" role="alert">
                <h4 className="alert-heading">Error</h4>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div>
            {/* Welcome Section */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card bg-gradient-primary">
                        <div className="card-body">
                            <h1 className="text-white">¡Bienvenido de nuevo, {user?.username}!</h1>
                            <p className="text-white-50 mb-1">
                                Resumen de la actividad reciente en el inventario.
                            </p>
                            <small className="text-white-75">
                                {new Date().toLocaleDateString('es-ES', { 
                                    weekday: 'long', 
                                    year: 'numeric', 
                                    month: 'long', 
                                    day: 'numeric' 
                                })}
                            </small>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="row mb-4">
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Artículos Totales"
                        value={stats?.total_articulos || 0}
                        icon={Package}
                        color="primary"
                        trend={{
                            direction: 'up',
                            value: '12%',
                            period: 'vs mes anterior'
                        }}
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Valor Inventario"
                        value={`$${(stats?.valor_total_inventario || 0).toLocaleString('es-CL')}`}
                        icon={DollarSign}
                        color="success"
                        trend={{
                            direction: 'up',
                            value: '8%',
                            period: 'vs mes anterior'
                        }}
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Sucursales Activas"
                        value={stats?.total_sucursales || 0}
                        icon={Building}
                        color="warning"
                        trend={{
                            direction: 'neutral',
                            value: '0%',
                            period: 'sin cambios'
                        }}
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Alertas de Stock"
                        value={stats?.alertas_stock_bajo || 0}
                        icon={AlertCircle}
                        color="danger"
                        trend={{
                            direction: 'down',
                            value: '5%',
                            period: 'vs semana anterior'
                        }}
                    />
                </div>
            </div>

            {/* Quick Actions & Recent Activity */}
            <div className="row">
                <div className="col-lg-4">
                    {/* Quick Actions */}
                    <AdminLTEWidget
                        type="card"
                        title="Acciones Rápidas"
                        icon={TrendingUp}
                        color="info"
                    >
                        <div className="d-grid gap-2">
                            <button
                                onClick={() => handleQuickAction('entrada')}
                                className="btn btn-success btn-block"
                            >
                                <Plus size={16} className="mr-2" />
                                Nueva Entrada
                            </button>
                            <button
                                onClick={() => handleQuickAction('salida')}
                                className="btn btn-danger btn-block"
                            >
                                <Minus size={16} className="mr-2" />
                                Registrar Salida
                            </button>
                            <button
                                onClick={() => handleQuickAction('ajuste')}
                                className="btn btn-warning btn-block"
                            >
                                <ListChecks size={16} className="mr-2" />
                                Realizar Ajuste
                            </button>
                        </div>
                    </AdminLTEWidget>

                    {/* Admin Panel */}
                    {(user?.is_admin || user?.role === 'ADMIN') && (
                        <AdminLTEWidget
                            type="card"
                            title="Panel de Administración"
                            icon={PieChart}
                            color="secondary"
                        >
                            <div className="d-grid gap-2">
                                <button
                                    onClick={() => navigate('/administracion')}
                                    className="btn btn-outline-secondary btn-block"
                                >
                                    Gestionar Sucursales
                                </button>
                                <button
                                    onClick={() => navigate('/usuarios')}
                                    className="btn btn-outline-secondary btn-block"
                                >
                                    Gestionar Usuarios
                                </button>
                                <button
                                    onClick={() => navigate('/reportes')}
                                    className="btn btn-outline-secondary btn-block"
                                >
                                    Ver Reportes
                                </button>
                            </div>
                        </AdminLTEWidget>
                    )}
                </div>

                <div className="col-lg-8">
                    {/* Recent Movements */}
                    <AdminLTEWidget
                        type="table"
                        title="Movimientos Recientes"
                        icon={Calendar}
                        onRefresh={() => window.location.reload()}
                    >
                        {movimientos.length === 0 ? (
                            <div className="text-center py-4">
                                <p className="text-muted">No hay movimientos recientes.</p>
                            </div>
                        ) : (
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Tipo</th>
                                        <th>Artículo</th>
                                        <th>Cantidad</th>
                                        <th>Fecha</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {movimientos.map((mov) => (
                                        <tr key={mov.id}>
                                            <td>
                                                <span className={`badge ${getTipoBadgeClass(mov.tipo_movimiento)}`}>
                                                    {mov.tipo_movimiento}
                                                </span>
                                            </td>
                                            <td className="font-weight-bold">{mov.articulo_nombre}</td>
                                            <td className="font-weight-bold">{mov.cantidad}</td>
                                            <td className="text-muted">
                                                {new Date(mov.fecha_movimiento).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                        <div className="card-footer">
                            <button
                                onClick={() => navigate('/movimientos')}
                                className="btn btn-primary btn-sm"
                            >
                                Ver todos los movimientos
                                <ArrowRight size={14} className="ml-1" />
                            </button>
                        </div>
                    </AdminLTEWidget>
                </div>
            </div>

            {/* Alerts Section */}
            {alertas.length > 0 && (
                <div className="row mt-4">
                    <div className="col-12">
                        <AdminLTEWidget
                            type="card"
                            title={`Alertas de Stock Bajo (${alertas.length})`}
                            icon={AlertCircle}
                            color="danger"
                        >
                            <div className="row">
                                {alertas.map((alerta) => (
                                    <div key={alerta.id} className="col-md-6 col-lg-4 mb-3">
                                        <div className="card bg-light">
                                            <div className="card-body">
                                                <h6 className="card-title">{alerta.articulo_nombre}</h6>
                                                <p className="card-text text-muted small">{alerta.sucursal_nombre}</p>
                                                <div className="d-flex justify-content-between align-items-center">
                                                    <span className="badge badge-danger badge-lg">
                                                        {alerta.cantidad_actual}
                                                    </span>
                                                    <small className="text-muted">
                                                        Umbral: {alerta.articulo_umbral_minimo}
                                                    </small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            {stats?.alertas_stock_bajo > 5 && (
                                <div className="card-footer">
                                    <button
                                        onClick={() => navigate('/alertas')}
                                        className="btn btn-danger btn-sm"
                                    >
                                        Ver todas las alertas ({stats.alertas_stock_bajo})
                                        <ArrowRight size={14} className="ml-1" />
                                    </button>
                                </div>
                            )}
                        </AdminLTEWidget>
                    </div>
                </div>
            )}
        </div>
    );
}

function getTipoBadgeClass(tipo) {
    switch (tipo) {
        case 'ENTRADA': return 'badge-success';
        case 'SALIDA': return 'badge-danger';
        case 'TRANSFERENCIA': return 'badge-info';
        case 'AJUSTE': return 'badge-warning';
        default: return 'badge-secondary';
    }
}