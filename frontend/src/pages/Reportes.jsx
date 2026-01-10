import { useState, useEffect } from 'react';
import { BarChart3, Download, Filter, Calendar } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { InventoryService } from '../services/inventory.service';

export default function Reportes() {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [reportType, setReportType] = useState('movimientos');
    const [dateRange, setDateRange] = useState(30);
    const [movimientos, setMovimientos] = useState([]);
    const [stockData, setStockData] = useState([]);
    const [resumen, setResumen] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchReportData();
    }, [reportType, dateRange]);

    const fetchReportData = async () => {
        setLoading(true);
        setError(null);
        try {
            if (reportType === 'movimientos') {
                const response = await InventoryService.reports.getMovimientosRecientes(dateRange);
                setMovimientos(response.data);
            } else if (reportType === 'stock') {
                const response = await InventoryService.reports.getStockPorSucursal();
                setStockData(response.data);
            } else if (reportType === 'resumen') {
                const response = await InventoryService.reports.getResumenMovimientos(dateRange);
                setResumen(response.data);
            }
        } catch (err) {
            console.error("Error fetching report data", err);
            setError("Error al cargar el reporte");
        } finally {
            setLoading(false);
        }
    };

    const exportToCSV = () => {
        let csvContent = "data:text/csv;charset=utf-8,";
        let data = [];
        let headers = [];

        if (reportType === 'movimientos') {
            headers = ['Tipo', 'Artículo', 'Cantidad', 'Origen', 'Destino', 'Fecha'];
            data = movimientos.map(m => [
                m.tipo_movimiento,
                m.articulo_nombre,
                m.cantidad,
                m.acueducto_origen_nombre || '-',
                m.acueducto_destino_nombre || '-',
                new Date(m.fecha_movimiento).toLocaleDateString()
            ]);
        } else if (reportType === 'stock') {
            headers = ['Sucursal', 'Acueductos', 'Stock Tuberías', 'Stock Equipos', 'Total'];
            data = stockData.map(s => [
                s.nombre,
                s.total_acueductos,
                s.stock_tuberias,
                s.stock_equipos,
                s.stock_total
            ]);
        } else if (reportType === 'resumen') {
            headers = ['Tipo Movimiento', 'Total', 'Cantidad Total'];
            data = resumen.map(r => [
                r.tipo_movimiento,
                r.total,
                r.cantidad_total
            ]);
        }

        csvContent += headers.join(',') + '\n';
        data.forEach(row => {
            csvContent += row.join(',') + '\n';
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `reporte_${reportType}_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const getTipoMovimientoColor = (tipo) => {
        switch (tipo) {
            case 'ENTRADA': return 'bg-green-100 text-green-800';
            case 'SALIDA': return 'bg-red-100 text-red-800';
            case 'TRANSFERENCIA': return 'bg-blue-100 text-blue-800';
            case 'AJUSTE': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando reporte...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Reportes</h1>
                <button
                    onClick={exportToCSV}
                    className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                >
                    <Download size={20} /> Exportar CSV
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                    {error}
                </div>
            )}

            {/* Filtros */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Tipo de Reporte */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tipo de Reporte
                        </label>
                        <select
                            value={reportType}
                            onChange={(e) => setReportType(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="movimientos">Movimientos</option>
                            <option value="stock">Stock por Sucursal</option>
                            <option value="resumen">Resumen de Movimientos</option>
                        </select>
                    </div>

                    {/* Rango de Fechas */}
                    {reportType !== 'stock' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Período (días)
                            </label>
                            <select
                                value={dateRange}
                                onChange={(e) => setDateRange(parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value={7}>Últimos 7 días</option>
                                <option value={30}>Últimos 30 días</option>
                                <option value={90}>Últimos 90 días</option>
                                <option value={365}>Último año</option>
                            </select>
                        </div>
                    )}
                </div>
            </div>

            {/* Reporte de Movimientos */}
            {reportType === 'movimientos' && (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="p-6 border-b">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <BarChart3 size={24} />
                            Reporte de Movimientos
                        </h2>
                        <p className="text-gray-600 text-sm mt-1">
                            Últimos {dateRange} días - Total: {movimientos.length} movimientos
                        </p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Tipo</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Artículo</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Cantidad</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Origen</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Destino</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Fecha</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {movimientos.length === 0 ? (
                                    <tr>
                                        <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                            No hay movimientos en este período
                                        </td>
                                    </tr>
                                ) : (
                                    movimientos.map(mov => (
                                        <tr key={mov.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTipoMovimientoColor(mov.tipo_movimiento)}`}>
                                                    {mov.tipo_movimiento}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm">{mov.articulo_nombre}</td>
                                            <td className="px-6 py-4 text-sm font-semibold">{mov.cantidad}</td>
                                            <td className="px-6 py-4 text-sm">{mov.acueducto_origen_nombre || '-'}</td>
                                            <td className="px-6 py-4 text-sm">{mov.acueducto_destino_nombre || '-'}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">
                                                {new Date(mov.fecha_movimiento).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Reporte de Stock por Sucursal */}
            {reportType === 'stock' && (
                <div className="grid grid-cols-1 gap-6">
                    {stockData.map(sucursal => (
                        <div key={sucursal.id} className="bg-white rounded-lg shadow p-6">
                            <h3 className="text-lg font-bold mb-4">{sucursal.nombre}</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-blue-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Acueductos</p>
                                    <p className="text-2xl font-bold text-blue-600">{sucursal.total_acueductos}</p>
                                </div>
                                <div className="bg-green-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Stock Tuberías</p>
                                    <p className="text-2xl font-bold text-green-600">{sucursal.stock_tuberias}</p>
                                </div>
                                <div className="bg-purple-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Stock Equipos</p>
                                    <p className="text-2xl font-bold text-purple-600">{sucursal.stock_equipos}</p>
                                </div>
                                <div className="bg-orange-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Stock Total</p>
                                    <p className="text-2xl font-bold text-orange-600">{sucursal.stock_total}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Reporte de Resumen */}
            {reportType === 'resumen' && (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="p-6 border-b">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <BarChart3 size={24} />
                            Resumen de Movimientos
                        </h2>
                        <p className="text-gray-600 text-sm mt-1">
                            Últimos {dateRange} días
                        </p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Tipo de Movimiento</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Total de Movimientos</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Cantidad Total</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {resumen.length === 0 ? (
                                    <tr>
                                        <td colSpan="3" className="px-6 py-8 text-center text-gray-500">
                                            No hay datos en este período
                                        </td>
                                    </tr>
                                ) : (
                                    resumen.map((item, idx) => (
                                        <tr key={idx} className="hover:bg-gray-50">
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTipoMovimientoColor(item.tipo_movimiento)}`}>
                                                    {item.tipo_movimiento}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm font-semibold">{item.total}</td>
                                            <td className="px-6 py-4 text-sm font-semibold">{item.cantidad_total}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}