import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { Plus, Filter } from 'lucide-react';
import Swal from 'sweetalert2';

export default function Movimientos() {
    const [movimientos, setMovimientos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);

    // Filtros
    const [filtros, setFiltros] = useState({
        tipo_movimiento: '',
    });

    // Formulario
    const [formData, setFormData] = useState({
        tipo_movimiento: 'ENTRADA',
        product_type: 'chemical', // Default
        product_id: '',
        acueducto_origen: '',
        acueducto_destino: '',
        cantidad: '',
        razon: ''
    });

    // Data lists
    const [productsList, setProductsList] = useState([]);
    const [acueductos, setAcueductos] = useState([]);
    const [loadingProducts, setLoadingProducts] = useState(false);

    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Cargar Movimientos y Acueductos al inicio
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [movRes, acuRes] = await Promise.all([
                    InventoryService.movimientos.getAll(),
                    InventoryService.acueductos.getAll()
                ]);
                setMovimientos(movRes.data.results || movRes.data);
                setAcueductos(acuRes.data.results || acuRes.data);
            } catch (err) {
                console.error("Error fetching initial data", err);
                setError("Error al cargar datos iniciales. Asegúrese que el servidor backend esté corriendo.");
            } finally {
                setLoading(false);
            }
        };
        fetchInitialData();
    }, []);

    // Cargar productos cuando cambia el tipo de producto seleccionado
    useEffect(() => {
        if (!showForm) return;

        const fetchProducts = async () => {
            setLoadingProducts(true);
            setProductsList([]);
            try {
                let res;
                switch (formData.product_type) {
                    case 'chemical':
                        res = await InventoryService.chemicals.getAll();
                        break;
                    case 'pipe':
                        res = await InventoryService.pipes.getAll();
                        break;
                    case 'pump':
                        res = await InventoryService.pumps.getAll();
                        break;
                    case 'accessory':
                        res = await InventoryService.accessories.getAll();
                        break;
                    default:
                        res = { data: [] };
                }
                setProductsList(res.data.results || res.data);
            } catch (err) {
                console.error("Error fetching products", err);
                // No mostrar error global, solo log
            } finally {
                setLoadingProducts(false);
            }
        };

        fetchProducts();
    }, [formData.product_type, showForm]);

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        // Validaciones básicas
        if (formData.tipo_movimiento === 'TRANSFERENCIA' &&
            formData.acueducto_origen === formData.acueducto_destino) {
            Swal.fire({
                icon: 'warning',
                title: 'Acueducto Inválido',
                text: 'El acueducto destino no puede ser igual al origen',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        if (!formData.product_id) {
            Swal.fire({
                icon: 'warning',
                title: 'Faltan datos',
                text: 'Seleccione un producto',
            });
            return;
        }

        try {
            const payload = {
                tipo_movimiento: formData.tipo_movimiento,
                cantidad: parseInt(formData.cantidad),
                razon: formData.razon,
                product_type: formData.product_type,
                product_id: parseInt(formData.product_id),
                acueducto_origen: formData.acueducto_origen || null,
                acueducto_destino: formData.acueducto_destino || null
            };

            await InventoryService.movimientos.create(payload);

            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: 'Movimiento registrado exitosamente',
                timer: 2000,
                showConfirmButton: false
            });

            // Reset parcial
            setFormData(prev => ({
                ...prev,
                cantidad: '',
                razon: '',
                product_id: '' // Limpiar selección de producto pero mantener tipo
            }));
            setShowForm(false);

            // Recargar movimientos
            const movRes = await InventoryService.movimientos.getAll();
            setMovimientos(movRes.data.results || movRes.data);

        } catch (err) {
            console.error("Error creating movement", err);
            const msg = err.response?.data?.detail
                || JSON.stringify(err.response?.data)
                || 'Error al crear el movimiento';
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: msg,
                confirmButtonColor: '#ef4444'
            });
        }
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
            <div className="flex items-center justify-center h-full p-10">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando movimientos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Movimientos de Inventario</h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                    <Plus size={20} /> Nuevo Movimiento
                </button>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                    {error}
                </div>
            )}

            {showForm && (
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
                    <h2 className="text-xl font-bold mb-4">Registrar Nuevo Movimiento</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Fila 1 */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Movimiento *</label>
                                <select
                                    name="tipo_movimiento"
                                    value={formData.tipo_movimiento}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border rounded-lg"
                                >
                                    <option value="ENTRADA">Entrada</option>
                                    <option value="SALIDA">Salida</option>
                                    <option value="TRANSFERENCIA">Transferencia</option>
                                    <option value="AJUSTE">Ajuste</option>
                                </select>
                            </div>

                            {/* Selector de Tipo de Producto */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Producto *</label>
                                <select
                                    name="product_type"
                                    value={formData.product_type}
                                    onChange={(e) => {
                                        setFormData(prev => ({ ...prev, product_type: e.target.value, product_id: '' }));
                                    }}
                                    className="w-full px-3 py-2 border rounded-lg bg-gray-50"
                                >
                                    <option value="chemical">Químico</option>
                                    <option value="pipe">Tubería</option>
                                    <option value="pump">Bomba/Motor</option>
                                    <option value="accessory">Accesorio</option>
                                </select>
                            </div>

                            {/* Selector de Producto Específico */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Producto ({formData.product_type}) *
                                    {loadingProducts && <span className="text-xs text-blue-500 ml-2">Cargando lista...</span>}
                                </label>
                                <select
                                    name="product_id"
                                    value={formData.product_id}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border rounded-lg"
                                    disabled={loadingProducts}
                                >
                                    <option value="">-- Seleccionar Producto --</option>
                                    {productsList.map(p => (
                                        <option key={p.id} value={p.id}>
                                            {p.nombre} {p.codigo ? `(${p.codigo})` : ''} - {p.marca || ''}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Cantidad */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad *</label>
                                <input
                                    type="number"
                                    name="cantidad"
                                    value={formData.cantidad}
                                    onChange={handleFormChange}
                                    min="1"
                                    className="w-full px-3 py-2 border rounded-lg"
                                    required
                                />
                            </div>

                            {/* Logica condicional de Acueductos */}
                            {(formData.tipo_movimiento === 'SALIDA' || formData.tipo_movimiento === 'TRANSFERENCIA' || formData.tipo_movimiento === 'AJUSTE') && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Acueducto Origen *</label>
                                    <select
                                        name="acueducto_origen"
                                        value={formData.acueducto_origen}
                                        onChange={handleFormChange}
                                        className="w-full px-3 py-2 border rounded-lg"
                                        required
                                    >
                                        <option value="">Seleccionar...</option>
                                        {acueductos.map(a => (
                                            <option key={a.id} value={a.id}>{a.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {(formData.tipo_movimiento === 'ENTRADA' || formData.tipo_movimiento === 'TRANSFERENCIA') && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Acueducto Destino *</label>
                                    <select
                                        name="acueducto_destino"
                                        value={formData.acueducto_destino}
                                        onChange={handleFormChange}
                                        className="w-full px-3 py-2 border rounded-lg"
                                        required
                                    >
                                        <option value="">Seleccionar...</option>
                                        {acueductos.map(a => (
                                            <option key={a.id} value={a.id}>{a.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">Razón / Comentarios</label>
                                <textarea
                                    name="razon"
                                    value={formData.razon}
                                    onChange={handleFormChange}
                                    rows="2"
                                    className="w-full px-3 py-2 border rounded-lg"
                                />
                            </div>
                        </div>

                        <div className="flex gap-3 justify-end mt-4">
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                            >
                                Guardar Movimiento
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cant.</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Origen</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Destino</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {movimientos.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                                    No hay movimientos recientes
                                </td>
                            </tr>
                        ) : (
                            movimientos.map(mov => (
                                <tr key={mov.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getTipoMovimientoColor(mov.tipo_movimiento)}`}>
                                            {mov.tipo_movimiento}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {mov.producto_str || 'Producto desconocido'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                                        {mov.cantidad}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {mov.acueducto_origen_nombre || '-'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {mov.acueducto_destino_nombre || '-'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(mov.fecha_movimiento).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}