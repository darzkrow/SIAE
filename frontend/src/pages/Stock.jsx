import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, AlertCircle, Plus, Minus, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Stock() {
    const [stockData, setStockData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');
    const [alertas, setAlertas] = useState([]);
    const [showMovementModal, setShowMovementModal] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [movementType, setMovementType] = useState('ENTRADA');
    const [movementQuantity, setMovementQuantity] = useState('');
    const [sucursalDestino, setSucursalDestino] = useState('');
    const [acueductoDestino, setAcueductoDestino] = useState('');
    const [acueductos, setAcueductos] = useState([]);
    const [sucursales, setSucursales] = useState([]);
    const [acueductosFiltered, setAcueductosFiltered] = useState([]);
    const [submitting, setSubmitting] = useState(false);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [stockTubRes, stockEqRes, alertasRes, acueductosRes, sucursalesRes] = await Promise.all([
                    axios.get(`${API_URL}/api/stock-tuberias/`),
                    axios.get(`${API_URL}/api/stock-equipos/`),
                    axios.get(`${API_URL}/api/reportes/alertas_stock_bajo/`),
                    axios.get(`${API_URL}/api/acueductos/`),
                    axios.get(`${API_URL}/api/sucursales/`)
                ]);

                const tuberias = (stockTubRes.data.results || stockTubRes.data).map(s => ({
                    ...s,
                    tipo: 'tuberia',
                    nombre: s.tuberia_detalle?.nombre || 'Tubería desconocida'
                }));

                const equipos = (stockEqRes.data.results || stockEqRes.data).map(s => ({
                    ...s,
                    tipo: 'equipo',
                    nombre: s.equipo_detalle?.nombre || 'Equipo desconocido'
                }));

                setStockData([...tuberias, ...equipos]);
                setAlertas(alertasRes.data);
                setAcueductos(acueductosRes.data.results || acueductosRes.data);
                setSucursales(sucursalesRes.data.results || sucursalesRes.data);
            } catch (err) {
                console.error("Error fetching stock data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Filtrar acueductos cuando se selecciona una sucursal
    useEffect(() => {
        if (sucursalDestino) {
            const filtered = acueductos.filter(acueducto => 
                acueducto.sucursal === parseInt(sucursalDestino)
            );
            setAcueductosFiltered(filtered);
            setAcueductoDestino(''); // Limpiar selección anterior
        } else {
            setAcueductosFiltered([]);
            setAcueductoDestino('');
        }
    }, [sucursalDestino, acueductos]);

    const filteredStock = stockData.filter(item => {
        const matchesSearch = item.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            item.acueducto_nombre.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = filterType === 'all' || item.tipo === filterType;
        return matchesSearch && matchesType;
    });

    const getStockStatus = (cantidad, umbral) => {
        if (cantidad === 0) return { color: 'bg-red-100 text-red-800', label: 'Sin stock' };
        if (cantidad <= umbral) return { color: 'bg-yellow-100 text-yellow-800', label: 'Bajo' };
        return { color: 'bg-green-100 text-green-800', label: 'Normal' };
    };

    const handleCreateMovement = async () => {
        if (!movementQuantity || movementQuantity <= 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Cantidad Inválida',
                text: 'Ingresa una cantidad válida mayor a 0',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        if (movementType === 'TRANSFERENCIA' && !acueductoDestino) {
            Swal.fire({
                icon: 'warning',
                title: 'Acueducto Requerido',
                text: 'Selecciona un acueducto destino',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        if (movementType === 'TRANSFERENCIA' && parseInt(acueductoDestino) === selectedItem.acueducto) {
            Swal.fire({
                icon: 'warning',
                title: 'Acueducto Inválido',
                text: 'El acueducto destino no puede ser igual al acueducto origen',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        setSubmitting(true);
        try {
            const movementData = {
                [selectedItem.tipo === 'tuberia' ? 'tuberia' : 'equipo']: selectedItem[selectedItem.tipo === 'tuberia' ? 'tuberia' : 'equipo'],
                tipo_movimiento: movementType,
                cantidad: parseInt(movementQuantity),
                razon: `Movimiento desde Stock - ${movementType}`
            };

            if (movementType === 'ENTRADA') {
                movementData.acueducto_destino = selectedItem.acueducto;
            } else if (movementType === 'SALIDA') {
                movementData.acueducto_origen = selectedItem.acueducto;
            } else if (movementType === 'TRANSFERENCIA') {
                movementData.acueducto_origen = selectedItem.acueducto;
                movementData.acueducto_destino = parseInt(acueductoDestino);
            }

            await axios.post(`${API_URL}/api/movimientos/`, movementData);
            
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: 'Movimiento creado exitosamente',
                confirmButtonColor: '#10b981',
                timer: 2000,
                timerProgressBar: true
            });
            
            setShowMovementModal(false);
            
            // Recargar datos
            const [stockTubRes, stockEqRes] = await Promise.all([
                axios.get(`${API_URL}/api/stock-tuberias/`),
                axios.get(`${API_URL}/api/stock-equipos/`)
            ]);

            const tuberias = (stockTubRes.data.results || stockTubRes.data).map(s => ({
                ...s,
                tipo: 'tuberia',
                nombre: s.tuberia_detalle?.nombre || 'Tubería desconocida'
            }));

            const equipos = (stockEqRes.data.results || stockEqRes.data).map(s => ({
                ...s,
                tipo: 'equipo',
                nombre: s.equipo_detalle?.nombre || 'Equipo desconocido'
            }));

            setStockData([...tuberias, ...equipos]);
        } catch (err) {
            console.error("Error creating movement", err);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: err.response?.data?.detail || err.response?.data?.cantidad?.[0] || 'Error al crear el movimiento',
                confirmButtonColor: '#ef4444'
            });
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando stock...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Gestión de Stock</h1>
                <p className="text-gray-600 mt-2">Visualiza y gestiona el inventario de tuberías y equipos</p>
            </div>

            {/* Alertas Críticas */}
            {alertas.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                        <div>
                            <h3 className="font-bold text-red-800 mb-2">Alertas de Stock Bajo</h3>
                            <div className="space-y-1">
                                {alertas.slice(0, 3).map((alerta, idx) => (
                                    <p key={idx} className="text-sm text-red-700">
                                        {alerta.articulo} en {alerta.acueducto}: {alerta.cantidad_actual}/{alerta.umbral_minimo}
                                    </p>
                                ))}
                                {alertas.length > 3 && (
                                    <p className="text-sm text-red-700 font-semibold">
                                        +{alertas.length - 3} alertas más
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Búsqueda y Filtros */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                        <input
                            type="text"
                            placeholder="Buscar por artículo o acueducto..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <select
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Todos los tipos</option>
                        <option value="tuberia">Solo Tuberías</option>
                        <option value="equipo">Solo Equipos</option>
                    </select>
                </div>
            </div>

            {/* Tabla de Stock */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Tipo</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Artículo</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acueducto</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Cantidad</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Estado</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Última Actualización</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {filteredStock.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                        No hay registros de stock
                                    </td>
                                </tr>
                            ) : (
                                filteredStock.map((item) => {
                                    const status = getStockStatus(item.cantidad, 10); // Umbral por defecto de 10
                                    return (
                                        <tr key={`${item.tipo}-${item.id}`} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 text-sm">
                                                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                                    {item.tipo === 'tuberia' ? 'Tubería' : 'Equipo'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm font-medium">{item.nombre}</td>
                                            <td className="px-6 py-4 text-sm">{item.acueducto_nombre}</td>
                                            <td className="px-6 py-4 text-sm font-bold text-lg">{item.cantidad}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${status.color}`}>
                                                    {status.label}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-600">
                                                {new Date(item.fecha_ultima_actualizacion).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 text-sm">
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => {
                                                            setSelectedItem(item);
                                                            setMovementType('ENTRADA');
                                                            setMovementQuantity('');
                                                            setShowMovementModal(true);
                                                        }}
                                                        className="p-1 text-green-600 hover:bg-green-100 rounded"
                                                        title="Entrada"
                                                    >
                                                        <Plus size={18} />
                                                    </button>
                                                    <button
                                                        onClick={() => {
                                                            setSelectedItem(item);
                                                            setMovementType('SALIDA');
                                                            setMovementQuantity('');
                                                            setShowMovementModal(true);
                                                        }}
                                                        className="p-1 text-red-600 hover:bg-red-100 rounded"
                                                        title="Salida"
                                                    >
                                                        <Minus size={18} />
                                                    </button>
                                                    <button
                                                        onClick={() => {
                                                            setSelectedItem(item);
                                                            setMovementType('TRANSFERENCIA');
                                                            setMovementQuantity('');
                                                            setSucursalDestino('');
                                                            setAcueductoDestino('');
                                                            setShowMovementModal(true);
                                                        }}
                                                        className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                                                        title="Transferencia"
                                                    >
                                                        <ArrowRight size={18} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Resumen */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600 mb-2">Total de Tuberías</h3>
                    <p className="text-3xl font-bold text-blue-600">
                        {stockData.filter(s => s.tipo === 'tuberia').reduce((sum, s) => sum + s.cantidad, 0)}
                    </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600 mb-2">Total de Equipos</h3>
                    <p className="text-3xl font-bold text-green-600">
                        {stockData.filter(s => s.tipo === 'equipo').reduce((sum, s) => sum + s.cantidad, 0)}
                    </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-600 mb-2">Stock Bajo</h3>
                    <p className="text-3xl font-bold text-red-600">{alertas.length}</p>
                </div>
            </div>

            {/* Modal de Movimiento */}
            {showMovementModal && selectedItem && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
                        <h2 className="text-xl font-bold mb-4">
                            {movementType === 'ENTRADA' && '➕ Entrada de Stock'}
                            {movementType === 'SALIDA' && '➖ Salida de Stock'}
                            {movementType === 'TRANSFERENCIA' && '↔️ Transferencia'}
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Artículo</label>
                                <input
                                    type="text"
                                    value={selectedItem.nombre}
                                    disabled
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Acueducto Origen</label>
                                <input
                                    type="text"
                                    value={selectedItem.acueducto_nombre}
                                    disabled
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                />
                            </div>

                            {movementType === 'TRANSFERENCIA' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Sucursal Destino</label>
                                        <select
                                            value={sucursalDestino}
                                            onChange={(e) => setSucursalDestino(e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="">Selecciona una sucursal</option>
                                            {sucursales.map(sucursal => (
                                                <option key={sucursal.id} value={sucursal.id}>
                                                    {sucursal.nombre}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Acueducto Destino</label>
                                        <select
                                            value={acueductoDestino}
                                            onChange={(e) => setAcueductoDestino(e.target.value)}
                                            disabled={!sucursalDestino}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                                        >
                                            <option value="">
                                                {sucursalDestino ? 'Selecciona un acueducto' : 'Primero selecciona una sucursal'}
                                            </option>
                                            {acueductosFiltered.map(acueducto => (
                                                <option key={acueducto.id} value={acueducto.id}>
                                                    {acueducto.nombre}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad</label>
                                <input
                                    type="number"
                                    min="1"
                                    value={movementQuantity}
                                    onChange={(e) => setMovementQuantity(e.target.value)}
                                    placeholder="Ingresa la cantidad"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <p className="text-xs text-gray-500 mt-1">Stock disponible: {selectedItem.cantidad}</p>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setShowMovementModal(false)}
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={handleCreateMovement}
                                    disabled={submitting}
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                                >
                                    {submitting ? 'Guardando...' : 'Guardar'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}