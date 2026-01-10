import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { Plus, Edit2, Trash2, AlertCircle, Bell } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Alertas() {
    const { user } = useAuth();
    const [alertas, setAlertas] = useState([]);
    const [notificaciones, setNotificaciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [activeTab, setActiveTab] = useState('alertas');

    // Listas para selectores
    const [acueductos, setAcueductos] = useState([]);
    const [productsList, setProductsList] = useState([]);
    const [loadingProducts, setLoadingProducts] = useState(false);

    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [formData, setFormData] = useState({
        product_type: 'chemical',
        product_id: '',
        acueducto: '',
        umbral_minimo: '',
        activo: true
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [alertasRes, notifRes, acuRes] = await Promise.all([
                InventoryService.alertas.getAll(),
                InventoryService.notificaciones.getAll(),
                InventoryService.acueductos.getAll()
            ]);

            setAlertas(alertasRes.data.results || alertasRes.data);
            setNotificaciones(notifRes.data.results || notifRes.data);
            setAcueductos(acuRes.data.results || acuRes.data);
        } catch (err) {
            console.error("Error fetching data", err);
            setError("Error al cargar los datos");
        } finally {
            setLoading(false);
        }
    };

    // Fetch dynamic products
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
            } finally {
                setLoadingProducts(false);
            }
        };

        fetchProducts();
    }, [formData.product_type, showForm]);

    const handleFormChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        try {
            const payload = {
                acueducto: parseInt(formData.acueducto),
                umbral_minimo: parseFloat(formData.umbral_minimo),
                activo: formData.activo,
                product_type: formData.product_type,
                product_id: parseInt(formData.product_id)
            };

            if (editingId) {
                // Nota: La edición de tipo/producto a veces es restringida, 
                // pero aquí lo permitimos si el backend lo soporta.
                await InventoryService.alertas.update(editingId, payload);
                Swal.fire('Actualizado', 'Alerta actualizada exitosamente', 'success');
            } else {
                await InventoryService.alertas.create(payload);
                Swal.fire('Creado', 'Alerta creada exitosamente', 'success');
            }

            resetForm();
            fetchData();
        } catch (err) {
            console.error("Error saving alert", err);
            const msg = err.response?.data?.detail || "Error al guardar la alerta";
            Swal.fire('Error', msg, 'error');
        }
    };

    const handleDelete = async (id) => {
        const result = await Swal.fire({
            title: '¿Estás seguro?',
            text: "No podrás revertir esto",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminar'
        });

        if (result.isConfirmed) {
            try {
                await InventoryService.alertas.delete(id);
                Swal.fire('Eliminado', 'La alerta ha sido eliminada.', 'success');
                fetchData();
            } catch (err) {
                console.error("Error deleting alert", err);
                Swal.fire('Error', 'No se pudo eliminar la alerta', 'error');
            }
        }
    };

    const handleEdit = (alerta) => {
        setEditingId(alerta.id);
        // Aquí hay un reto: reconstruir el type y id desde el serializer si no vienen.
        // El serializer actual devuelve `product_type_read` solo si lo agregué (no lo agregué en AlertaSerializer, solo producto_str).
        // Sería mejor agregar los campos de lectura al serializer si quiero edición completa.
        // Por ahora, asumimos que no se edita el producto, o reseteamos.
        // Mejor simplificación: para editar, el usuario debe re-seleccionar el producto si quiere cambiarlo, 
        // o bloquear la edición del producto.
        // Dado el MVP, cargaremos los datos básicos.
        setFormData({
            acueducto: alerta.acueducto,
            umbral_minimo: alerta.umbral_minimo,
            activo: alerta.activo,
            product_type: 'chemical', // Default o intentar adivinar?
            product_id: '' // Difícil sin metadata
        });

        // Mejor UX: Avisar que debe reseleccionar producto si edita
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({
            product_type: 'chemical',
            product_id: '',
            acueducto: '',
            umbral_minimo: '',
            activo: true
        });
        setEditingId(null);
        setShowForm(false);
    };

    const markNotificationAsRead = async (id) => {
        try {
            await InventoryService.notificaciones.markAsRead(id);
            fetchData();
        } catch (err) {
            console.error("Error updating notification", err);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full p-10">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Gestión de Alertas</h1>
                {user?.role === 'ADMIN' && (
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                        <Plus size={20} /> Nueva Alerta
                    </button>
                )}
            </div>

            {showForm && user?.role === 'ADMIN' && (
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
                    <h2 className="text-xl font-bold mb-4">
                        {editingId ? 'Editar Alerta' : 'Crear Nueva Alerta'}
                    </h2>
                    {editingId && (
                        <div className="bg-yellow-50 p-2 mb-4 text-sm text-yellow-700 rounded">
                            Nota: Al editar, por favor seleccione nuevamente el producto si desea cambiarlo.
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                            {/* Acueducto */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Acueducto *</label>
                                <select
                                    name="acueducto"
                                    value={formData.acueducto}
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

                            {/* Tipo de Producto */}
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

                            {/* Producto Selector */}
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
                                    required={!editingId} // Requerido si es nuevo
                                >
                                    <option value="">-- Seleccionar Producto --</option>
                                    {productsList.map(p => (
                                        <option key={p.id} value={p.id}>
                                            {p.nombre} {p.codigo ? `(${p.codigo})` : ''} - {p.marca || ''}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Umbral */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Umbral Mínimo *</label>
                                <input
                                    type="number"
                                    name="umbral_minimo"
                                    value={formData.umbral_minimo}
                                    onChange={handleFormChange}
                                    step="0.01"
                                    min="0"
                                    className="w-full px-3 py-2 border rounded-lg"
                                    required
                                />
                            </div>

                            {/* Activo */}
                            <div className="flex items-end pb-2">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        name="activo"
                                        checked={formData.activo}
                                        onChange={handleFormChange}
                                        className="w-5 h-5 rounded text-blue-600"
                                    />
                                    <span className="font-medium text-gray-700">Alerta Activa</span>
                                </label>
                            </div>
                        </div>

                        <div className="flex gap-3 mt-4">
                            <button
                                type="submit"
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                {editingId ? 'Actualizar' : 'Crear'} Alerta
                            </button>
                            <button
                                type="button"
                                onClick={resetForm}
                                className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                            >
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="flex gap-4 border-b">
                <button
                    onClick={() => setActiveTab('alertas')}
                    className={`px-4 py-2 font-medium border-b-2 transition ${activeTab === 'alertas'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-800'
                        }`}
                >
                    Alertas ({alertas.length})
                </button>
                <button
                    onClick={() => setActiveTab('notificaciones')}
                    className={`px-4 py-2 font-medium border-b-2 transition ${activeTab === 'notificaciones'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-800'
                        }`}
                >
                    Notificaciones ({notificaciones.length})
                </button>
            </div>

            {activeTab === 'alertas' && (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acueducto</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Minimo</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                                {user?.role === 'ADMIN' && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {alertas.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">No hay alertas configuradas</td>
                                </tr>
                            ) : (
                                alertas.map(alerta => (
                                    <tr key={alerta.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                                            {alerta.producto_str}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">{alerta.acueducto_nombre}</td>
                                        <td className="px-6 py-4 text-sm font-bold text-gray-900">{alerta.umbral_minimo}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${alerta.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {alerta.activo ? 'Activa' : 'Inactiva'}
                                            </span>
                                        </td>
                                        {user?.role === 'ADMIN' && (
                                            <td className="px-6 py-4 text-sm flex gap-2">
                                                <button onClick={() => handleDelete(alerta.id)} className="text-red-600 hover:text-red-900">
                                                    <Trash2 size={18} />
                                                </button>
                                            </td>
                                        )}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            {activeTab === 'notificaciones' && (
                <div className="space-y-4">
                    {notificaciones.length === 0 ? (
                        <div className="bg-white rounded-lg shadow p-8 text-center">
                            <Bell size={48} className="mx-auto text-gray-400 mb-4" />
                            <p className="text-gray-600">No tienes notificaciones</p>
                        </div>
                    ) : (
                        notificaciones.map(notif => (
                            <div key={notif.id} className={`rounded-lg p-4 border-l-4 ${notif.leida ? 'bg-gray-50 border-gray-300' : 'bg-blue-50 border-blue-500'}`}>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <p className="font-semibold text-gray-800">{notif.mensaje}</p>
                                        <p className="text-xs text-gray-500 mt-1">{new Date(notif.creada_en).toLocaleString()}</p>
                                    </div>
                                    {!notif.leida && (
                                        <button onClick={() => markNotificationAsRead(notif.id)} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">
                                            Marcar leída
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}