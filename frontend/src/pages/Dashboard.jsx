import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';
import { Package, Droplets, Activity, AlertCircle, TrendingUp, Plus, Minus, ArrowRight, Calendar, Users, BarChart2, PieChart, ListChecks } from 'lucide-react';
import Swal from 'sweetalert2';
import StatCard from '../components/StatCard'; // Importar el nuevo componente

export default function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [movimientos, setMovimientos] = useState([]);
    const [alertas, setAlertas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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
            } catch (err) {
                console.error("Error fetching dashboard data", err);
                setError("No se pudieron cargar los datos del dashboard. Verifique la conexión con el servidor.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

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
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md" role="alert">
                <p className="font-bold">Error</p>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Welcome Section */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-xl p-8 shadow-lg">
                <h1 className="text-4xl font-bold">¡Bienvenido de nuevo, {user?.username}!</h1>
                <p className="text-blue-100 mt-2 text-lg">
                    Resumen de la actividad reciente en el inventario.
                </p>
                <p className="text-blue-200 text-sm mt-1">
                    {new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Artículos Totales"
                    value={stats?.total_articulos || 0}
                    icon={Package}
                    color="bg-blue-500"
                    trendLabel="En todas las sucursales"
                />
                <StatCard
                    title="Valor del Inventario"
                    value={`$${(stats?.valor_total_inventario || 0).toLocaleString('es-CL')}`}
                    icon={BarChart2}
                    color="bg-green-500"
                    trendLabel="Valor monetario total"
                />
                <StatCard
                    title="Sucursales Activas"
                    value={stats?.total_sucursales || 0}
                    icon={Users}
                    color="bg-amber-500"
                    trendLabel="Gestionando inventario"
                />
                <StatCard
                    title="Alertas de Stock"
                    value={stats?.alertas_stock_bajo || 0}
                    icon={AlertCircle}
                    color="bg-red-500"
                    trendLabel="Requieren atención"
                />
            </div>

            {/* Quick Actions & Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1 space-y-6">
                    {/* Quick Actions */}
                    <div className="bg-white rounded-xl shadow-md p-6">
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
                            <TrendingUp className="text-purple-500" />
                            Acciones Rápidas
                        </h3>
                        <div className="space-y-3">
                            <button
                                onClick={() => handleQuickAction('entrada')}
                                className="w-full p-4 bg-green-500 text-white rounded-lg hover:bg-green-600 transition font-semibold flex items-center justify-center gap-2"
                            >
                                <Plus size={20} />
                                Nueva Entrada
                            </button>
                            <button
                                onClick={() => handleQuickAction('salida')}
                                className="w-full p-4 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-semibold flex items-center justify-center gap-2"
                            >
                                <Minus size={20} />
                                Registrar Salida
                            </button>
                            <button
                                onClick={() => handleQuickAction('ajuste')}
                                className="w-full p-4 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition font-semibold flex items-center justify-center gap-2"
                            >
                                <ListChecks size={20} />
                                Realizar Ajuste
                            </button>
                        </div>
                    </div>
                     {/* Admin Panel */}
                    {user?.is_admin && (
                        <div className="bg-white rounded-xl shadow-md p-6">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
                                <PieChart className="text-indigo-500" />
                                Panel de Administración
                            </h3>
                            <div className="space-y-3">
                                <button
                                    onClick={() => navigate('/administracion')}
                                    className="w-full p-3 bg-indigo-100 text-indigo-800 rounded-lg hover:bg-indigo-200 transition font-medium"
                                >
                                    Gestionar Sucursales
                                </button>
                                <button
                                    onClick={() => navigate('/usuarios')}
                                    className="w-full p-3 bg-indigo-100 text-indigo-800 rounded-lg hover:bg-indigo-200 transition font-medium"
                                >
                                    Gestionar Usuarios
                                </button>
                                <button
                                    onClick={() => navigate('/reportes')}
                                    className="w-full p-3 bg-indigo-100 text-indigo-800 rounded-lg hover:bg-indigo-200 transition font-medium"
                                >
                                    Ver Reportes
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                <div className="lg:col-span-2 bg-white rounded-xl shadow-md p-6">
                     {/* Recent Movements */}
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
                        <Calendar className="text-blue-500" />
                        Movimientos Recientes
                    </h3>
                    {movimientos.length === 0 ? (
                        <div className="text-center py-12">
                            <p className="text-gray-500">No hay movimientos recientes.</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="border-b-2 border-gray-100">
                                    <tr>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-600">Tipo</th>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-600">Artículo</th>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-600">Cantidad</th>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-600">Fecha</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {movimientos.map((mov) => (
                                        <tr key={mov.id} className="hover:bg-gray-50">
                                            <td className="px-4 py-3">
                                                <span className={`px-2 py-1 rounded-full text-xs font-bold ${getTipoColor(mov.tipo_movimiento)}`}>
                                                    {mov.tipo_movimiento}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 font-medium text-gray-800">{mov.articulo_nombre}</td>
                                            <td className="px-4 py-3 font-bold text-gray-800">{mov.cantidad}</td>
                                            <td className="px-4 py-3 text-gray-500">
                                                {new Date(mov.fecha_movimiento).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                    <button
                        onClick={() => navigate('/movimientos')}
                        className="w-full mt-4 p-2 text-blue-600 hover:bg-blue-50 rounded-lg font-semibold text-sm transition"
                    >
                        Ver todos los movimientos →
                    </button>
                </div>
            </div>

            {/* Alerts Section */}
            {alertas.length > 0 && (
                <div className="bg-white rounded-xl shadow-md p-6">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-red-600">
                        <AlertCircle />
                        Alertas de Stock Bajo ({alertas.length})
                    </h3>
                    <div className="space-y-3">
                        {alertas.map((alerta) => (
                            <div key={alerta.id} className="flex justify-between items-center p-4 bg-red-50 rounded-lg border border-red-200">
                                <div>
                                    <p className="font-bold text-gray-800">{alerta.articulo_nombre}</p>
                                    <p className="text-sm text-gray-600">{alerta.sucursal_nombre}</p>
                                </div>
                                <div className="text-right">
                                    <p className="font-extrabold text-2xl text-red-600">{alerta.cantidad_actual}</p>
                                    <p className="text-xs text-gray-500">Umbral: {alerta.articulo_umbral_minimo}</p>
                                </div>
                            </div>
                        ))}
                        {stats?.alertas_stock_bajo > 5 && (
                            <button
                                onClick={() => navigate('/alertas')}
                                className="w-full mt-3 p-2 text-red-600 hover:bg-red-100 rounded-lg font-semibold text-sm transition"
                            >
                                Ver todas las alertas ({stats.alertas_stock_bajo})
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

function getTipoColor(tipo) {
    switch (tipo) {
        case 'ENTRADA': return 'bg-green-100 text-green-800';
        case 'SALIDA': return 'bg-red-100 text-red-800';
        case 'TRANSFERENCIA': return 'bg-blue-100 text-blue-800';
        case 'AJUSTE': return 'bg-yellow-100 text-yellow-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}
