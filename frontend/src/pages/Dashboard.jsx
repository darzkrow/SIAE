import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';
import { Package, Droplets, Activity, AlertCircle, TrendingUp, Plus, Minus, ArrowRight, Calendar, Users } from 'lucide-react';
import Swal from 'sweetalert2';

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
                    InventoryService.movimientos.getAll({ limit: 5 }),
                    // Para alertas de stock bajo, idealmente deberíamos tener un endpoint unificado
                    // Por ahora usamos el de químicos como ejemplo o el reporte general si existe
                    // Asumiremos que alertas_stock_bajo sigue existiendo en el nuevo reporte
                    InventoryService.chemicals.getStockBajo()
                    // Nota: El endpoint original /api/reportes/alertas_stock_bajo/ podría necesitar 
                    // ser re-mapeado en el servicio si es un endpoint custom global.
                ]);

                setStats(statsRes.data);
                setMovimientos(movRes.data.results || movRes.data);
                setAlertas(alertasRes.data);
            } catch (err) {
                console.error("Error fetching stats", err);
                setError("No se pudieron cargar las estadísticas");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleQuickAction = (action) => {
        if (action === 'entrada') {
            navigate('/movimientos');
            Swal.fire({
                icon: 'info',
                title: 'Crear Entrada',
                text: 'Selecciona "Nuevo Movimiento" y elige tipo ENTRADA',
                confirmButtonColor: '#3085d6'
            });
        } else if (action === 'salida') {
            navigate('/movimientos');
            Swal.fire({
                icon: 'info',
                title: 'Registrar Salida',
                text: 'Selecciona "Nuevo Movimiento" y elige tipo SALIDA',
                confirmButtonColor: '#3085d6'
            });
        } else if (action === 'transferencia') {
            navigate('/stock');
            Swal.fire({
                icon: 'info',
                title: 'Crear Transferencia',
                text: 'Busca el artículo y haz clic en el botón ↔️',
                confirmButtonColor: '#3085d6'
            });
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando estadísticas...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Welcome Section */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg p-6">
                <h1 className="text-3xl font-bold">Bienvenido, {user?.username}!</h1>
                <p className="text-blue-100 mt-2">
                    {user?.role === 'ADMIN' ? 'Panel de Administrador' : 'Panel de Operador'}
                </p>
                <p className="text-blue-100 text-sm mt-1">
                    {new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Tuberías"
                    value={stats?.total_tuberias || 0}
                    icon={<Droplets className="text-blue-500" size={24} />}
                    color="bg-blue-50"
                />
                <StatCard
                    title="Equipos"
                    value={stats?.total_equipos || 0}
                    icon={<Activity className="text-green-500" size={24} />}
                    color="bg-green-50"
                />
                <StatCard
                    title="Sucursales"
                    value={stats?.total_sucursales || 0}
                    icon={<Package className="text-amber-500" size={24} />}
                    color="bg-amber-50"
                />
                <StatCard
                    title="Alertas Activas"
                    value={alertas.length}
                    icon={<AlertCircle className="text-red-500" size={24} />}
                    color="bg-red-50"
                />
            </div>

            {/* Stock Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Droplets className="text-blue-500" size={20} />
                        Stock de Tuberías
                    </h3>
                    <div className="text-3xl font-bold text-blue-600">
                        {stats?.total_stock_tuberias || 0}
                    </div>
                    <p className="text-gray-600 text-sm mt-2">Unidades en inventario</p>
                    <button
                        onClick={() => navigate('/stock')}
                        className="mt-4 text-blue-600 hover:text-blue-800 font-medium text-sm"
                    >
                        Ver detalles →
                    </button>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Activity className="text-green-500" size={20} />
                        Stock de Equipos
                    </h3>
                    <div className="text-3xl font-bold text-green-600">
                        {stats?.total_stock_equipos || 0}
                    </div>
                    <p className="text-gray-600 text-sm mt-2">Unidades en inventario</p>
                    <button
                        onClick={() => navigate('/stock')}
                        className="mt-4 text-green-600 hover:text-green-800 font-medium text-sm"
                    >
                        Ver detalles →
                    </button>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <TrendingUp className="text-purple-500" size={20} />
                    Acciones Rápidas
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button
                        onClick={() => handleQuickAction('entrada')}
                        className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition text-left font-medium flex items-center gap-2"
                    >
                        <Plus size={20} className="text-green-600" />
                        Nueva Entrada
                    </button>
                    <button
                        onClick={() => handleQuickAction('salida')}
                        className="p-4 border-2 border-red-200 rounded-lg hover:bg-red-50 transition text-left font-medium flex items-center gap-2"
                    >
                        <Minus size={20} className="text-red-600" />
                        Registrar Salida
                    </button>
                    <button
                        onClick={() => handleQuickAction('transferencia')}
                        className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition text-left font-medium flex items-center gap-2"
                    >
                        <ArrowRight size={20} className="text-blue-600" />
                        Transferencia
                    </button>
                </div>
            </div>

            {/* Alerts Section */}
            {alertas.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-800">
                        <AlertCircle size={20} />
                        Alertas de Stock Bajo ({alertas.length})
                    </h3>
                    <div className="space-y-2">
                        {alertas.slice(0, 5).map((alerta, idx) => (
                            <div key={idx} className="flex justify-between items-center p-3 bg-white rounded border border-red-100">
                                <div>
                                    <p className="font-medium text-gray-800">{alerta.articulo}</p>
                                    <p className="text-sm text-gray-600">{alerta.acueducto}</p>
                                </div>
                                <div className="text-right">
                                    <p className="font-bold text-red-600">{alerta.cantidad_actual}/{alerta.umbral_minimo}</p>
                                    <p className="text-xs text-gray-600">Stock/Umbral</p>
                                </div>
                            </div>
                        ))}
                        {alertas.length > 5 && (
                            <button
                                onClick={() => navigate('/alertas')}
                                className="w-full mt-3 p-2 text-red-600 hover:bg-red-100 rounded font-medium text-sm"
                            >
                                Ver todas las alertas ({alertas.length})
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Recent Movements */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Calendar className="text-purple-500" size={20} />
                    Movimientos Recientes
                </h3>
                {movimientos.length === 0 ? (
                    <div className="text-center py-8">
                        <p className="text-gray-600">No hay movimientos recientes</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-4 py-2 text-left font-semibold text-gray-700">Tipo</th>
                                    <th className="px-4 py-2 text-left font-semibold text-gray-700">Artículo</th>
                                    <th className="px-4 py-2 text-left font-semibold text-gray-700">Cantidad</th>
                                    <th className="px-4 py-2 text-left font-semibold text-gray-700">Fecha</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {movimientos.map((mov) => (
                                    <tr key={mov.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-2">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${getTipoColor(mov.tipo_movimiento)}`}>
                                                {mov.tipo_movimiento}
                                            </span>
                                        </td>
                                        <td className="px-4 py-2 font-medium">{mov.articulo_nombre}</td>
                                        <td className="px-4 py-2 font-bold">{mov.cantidad}</td>
                                        <td className="px-4 py-2 text-gray-600">
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
                    className="w-full mt-4 p-2 text-blue-600 hover:bg-blue-50 rounded font-medium text-sm"
                >
                    Ver todos los movimientos →
                </button>
            </div>

            {/* Admin Section */}
            {user?.role === 'ADMIN' && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Users className="text-indigo-500" size={20} />
                        Panel de Administración
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button
                            onClick={() => navigate('/administracion')}
                            className="p-4 border-2 border-indigo-200 rounded-lg hover:bg-indigo-50 transition text-left font-medium"
                        >
                            Gestionar Sucursales
                        </button>
                        <button
                            onClick={() => navigate('/usuarios')}
                            className="p-4 border-2 border-indigo-200 rounded-lg hover:bg-indigo-50 transition text-left font-medium"
                        >
                            Gestionar Usuarios
                        </button>
                        <button
                            onClick={() => navigate('/reportes')}
                            className="p-4 border-2 border-indigo-200 rounded-lg hover:bg-indigo-50 transition text-left font-medium"
                        >
                            Ver Reportes
                        </button>
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

function StatCard({ title, value, icon, color }) {
    return (
        <div className={`${color} rounded-lg p-6 border border-gray-200`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-600 text-sm font-medium">{title}</p>
                    <p className="text-3xl font-bold text-gray-800 mt-2">{value}</p>
                </div>
                <div className="p-3 bg-white rounded-lg">
                    {icon}
                </div>
            </div>
        </div>
    );
}
