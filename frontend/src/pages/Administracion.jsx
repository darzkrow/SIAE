import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Building2, Droplets, Zap, Users, Package } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { InventoryService } from '../services/inventory.service';

export default function Administracion() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('sucursales');
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Data states
    const [sucursales, setSucursales] = useState([]);
    const [acueductos, setAcueductos] = useState([]);
    const [pipes, setPipes] = useState([]);
    const [pumps, setPumps] = useState([]);
    const [categories, setCategories] = useState([]);
    const [organizaciones, setOrganizaciones] = useState([]);
    const [usuarios, setUsuarios] = useState([]);

    // Form data
    const [formData, setFormData] = useState({});

    useEffect(() => {
        if (!user?.is_admin) {
            setError('No tienes permiso para acceder a esta sección');
            return;
        }
        fetchAllData();
    }, [user]);

    const fetchAllData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [
                sucRes, acuRes, pipeRes, pumpRes,
                catRes, orgRes, usersRes
            ] = await Promise.all([
                InventoryService.sucursales.getAll(),
                InventoryService.acueductos.getAll(),
                InventoryService.pipes.getAll(),
                InventoryService.pumps.getAll(),
                InventoryService.categories.getAll(),
                InventoryService.organizaciones.getAll(),
                InventoryService.users.getAll()
            ]);

            setSucursales(sucRes.data.results || sucRes.data);
            setAcueductos(acuRes.data.results || acuRes.data);
            setPipes(pipeRes.data.results || pipeRes.data);
            setPumps(pumpRes.data.results || pumpRes.data);
            setCategories(catRes.data.results || catRes.data);
            setOrganizaciones(orgRes.data.results || orgRes.data);
            setUsuarios(usersRes.data.results || usersRes.data);
        } catch (err) {
            console.error("Error fetching data", err);
            setError("Error al cargar los datos de administración");
        } finally {
            setLoading(false);
        }
    };

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
            let service;
            switch (activeTab) {
                case 'sucursales': service = InventoryService.sucursales; break;
                case 'acueductos': service = InventoryService.acueductos; break;
                case 'pipes': service = InventoryService.pipes; break;
                case 'pumps': service = InventoryService.pumps; break;
                case 'organizaciones': service = InventoryService.organizaciones; break;
                case 'usuarios': service = InventoryService.users; break;
                default: throw new Error("Servicio no definido");
            }

            if (editingId) {
                await service.update(editingId, formData);
                setSuccess(`Actualizado exitosamente`);
            } else {
                await service.create(formData);
                setSuccess(`Creado exitosamente`);
            }

            resetForm();
            fetchAllData();
        } catch (err) {
            console.error("Error saving data", err);
            setError(err.response?.data?.detail || "Error al guardar los cambios");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm(`¿Estás seguro de que deseas eliminar este elemento?`)) return;

        try {
            let service;
            switch (activeTab) {
                case 'sucursales': service = InventoryService.sucursales; break;
                case 'organizaciones': service = InventoryService.organizaciones; break;
                case 'usuarios': service = InventoryService.users; break;
                case 'pipes': service = InventoryService.pipes; break;
                case 'pumps': service = InventoryService.pumps; break;
                case 'acueductos': service = InventoryService.acueductos; break;
                default: throw new Error("Servicio no definido");
            }

            await service.delete(id);
            setSuccess(`Eliminado exitosamente`);
            fetchAllData();
        } catch (err) {
            console.error("Error deleting data", err);
            setError("Error al eliminar el elemento");
        }
    };

    const handleEdit = (item) => {
        setEditingId(item.id);
        const editData = { ...item };
        if (item.organizacion_central?.id) editData.organizacion_central = item.organizacion_central.id;
        if (item.sucursal?.id) editData.sucursal = item.sucursal.id;
        if (item.categoria?.id) editData.categoria = item.categoria.id;
        if (item.unidad_medida?.id) editData.unidad_medida = item.unidad_medida.id;
        if (item.proveedor?.id) editData.proveedor = item.proveedor.id;
        if (item.producto?.id) editData.producto = item.producto.id;
        if (item.acueducto?.id) editData.acueducto = item.acueducto.id;

        setFormData(editData);
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({});
        setEditingId(null);
        setShowForm(false);
    };

    const renderForm = () => {
        const inputClass = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition";
        const labelClass = "block text-sm font-medium text-gray-700 mb-1";

        switch (activeTab) {
            case 'sucursales':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className={labelClass}>Nombre *</label>
                                <input type="text" name="nombre" value={formData.nombre || ''} onChange={handleFormChange} className={inputClass} required />
                            </div>
                            <div>
                                <label className={labelClass}>Organización Central *</label>
                                <select name="organizacion_central" value={formData.organizacion_central || ''} onChange={handleFormChange} className={inputClass} required>
                                    <option value="">Seleccionar...</option>
                                    {organizaciones.map(o => <option key={o.id} value={o.id}>{o.nombre}</option>)}
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-2 pt-4">
                            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 shadow-sm transition active:scale-95">{editingId ? 'Actualizar' : 'Crear'}</button>
                            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition active:scale-95">Cancelar</button>
                        </div>
                    </form>
                );

            case 'organizaciones':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className={labelClass}>Nombre *</label>
                                <input type="text" name="nombre" value={formData.nombre || ''} onChange={handleFormChange} className={inputClass} required />
                            </div>
                            <div>
                                <label className={labelClass}>RIF</label>
                                <input type="text" name="rif" value={formData.rif || ''} onChange={handleFormChange} className={inputClass} />
                            </div>
                        </div>
                        <div className="flex gap-2 pt-4">
                            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 shadow-sm transition active:scale-95">{editingId ? 'Actualizar' : 'Crear'}</button>
                            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition active:scale-95">Cancelar</button>
                        </div>
                    </form>
                );

            case 'acueductos':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className={labelClass}>Nombre *</label>
                                <input type="text" name="nombre" value={formData.nombre || ''} onChange={handleFormChange} className={inputClass} required />
                            </div>
                            <div>
                                <label className={labelClass}>Sucursal *</label>
                                <select name="sucursal" value={formData.sucursal || ''} onChange={handleFormChange} className={inputClass} required>
                                    <option value="">Seleccionar...</option>
                                    {sucursales.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className={labelClass}>Ubicación</label>
                                <input type="text" name="ubicacion" value={formData.ubicacion || ''} onChange={handleFormChange} className={inputClass} />
                            </div>
                        </div>
                        <div className="flex gap-2 pt-4">
                            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 shadow-sm transition active:scale-95">{editingId ? 'Actualizar' : 'Crear'}</button>
                            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition active:scale-95">Cancelar</button>
                        </div>
                    </form>
                );

            case 'usuarios':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className={labelClass}>Usuario *</label>
                                <input type="text" name="username" value={formData.username || ''} onChange={handleFormChange} disabled={editingId} className={`${inputClass} disabled:bg-gray-100`} required />
                            </div>
                            <div>
                                <label className={labelClass}>Email *</label>
                                <input type="email" name="email" value={formData.email || ''} onChange={handleFormChange} className={inputClass} required />
                            </div>
                            <div>
                                <label className={labelClass}>Nombre</label>
                                <input type="text" name="first_name" value={formData.first_name || ''} onChange={handleFormChange} className={inputClass} />
                            </div>
                            <div>
                                <label className={labelClass}>Apellido</label>
                                <input type="text" name="last_name" value={formData.last_name || ''} onChange={handleFormChange} className={inputClass} />
                            </div>
                            <div>
                                <label className={labelClass}>Rol *</label>
                                <select name="role" value={formData.role || 'OPERADOR'} onChange={handleFormChange} className={inputClass}>
                                    <option value="ADMIN">Administrador</option>
                                    <option value="OPERADOR">Operador</option>
                                </select>
                            </div>
                            <div>
                                <label className={labelClass}>Sucursal</label>
                                <select name="sucursal" value={formData.sucursal || ''} onChange={handleFormChange} className={inputClass}>
                                    <option value="">Seleccionar...</option>
                                    {sucursales.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className={labelClass}>Contraseña {editingId ? '(opcional)' : '*'}</label>
                                <input type="password" name="password" value={formData.password || ''} onChange={handleFormChange} className={inputClass} required={!editingId} />
                            </div>
                            <div className="flex items-center gap-2 pt-6">
                                <input type="checkbox" name="is_active" checked={formData.is_active !== false} onChange={handleFormChange} className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                <span className="text-sm font-medium text-gray-700">Activo</span>
                            </div>
                        </div>
                        <div className="flex gap-2 pt-4">
                            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 shadow-sm transition active:scale-95">{editingId ? 'Actualizar' : 'Crear'}</button>
                            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition active:scale-95">Cancelar</button>
                        </div>
                    </form>
                );

            case 'pipes':
            case 'pumps':
                return (
                    <p className="text-sm text-gray-500 italic">
                        La gestión detallada de productos se realiza en la sección de Catálogo.
                    </p>
                );

            default:
                return null;
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Administración</h1>
                <p className="text-gray-500">Configuración general del sistema y gestión de accesos</p>
            </header>

            {error && <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-r-lg">{error}</div>}
            {success && <div className="mb-4 p-4 bg-green-50 border-l-4 border-green-500 text-green-700 rounded-r-lg">{success}</div>}

            <div className="flex flex-col lg:flex-row gap-8">
                <aside className="w-full lg:w-64 space-y-1">
                    <nav className="space-y-1">
                        {[
                            { id: 'organizaciones', icon: Building2, label: 'Organizaciones' },
                            { id: 'sucursales', icon: Building2, label: 'Sucursales' },
                            { id: 'acueductos', icon: Droplets, label: 'Acueductos' },
                            { id: 'usuarios', icon: Users, label: 'Usuarios' },
                            { id: 'pipes', icon: Package, label: 'Tuberías (Catálogo)' },
                            { id: 'pumps', icon: Zap, label: 'Bombas (Catálogo)' }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => { setActiveTab(tab.id); resetForm(); }}
                                className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition ${activeTab === tab.id ? 'bg-blue-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <tab.icon size={20} />
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </aside>

                <main className="flex-1">
                    <div className="mb-6 flex justify-between items-center">
                        <h2 className="text-xl font-semibold capitalize">{activeTab.replace('-', ' ')}</h2>
                        {['organizaciones', 'sucursales', 'acueductos', 'usuarios'].includes(activeTab) && !showForm && (
                            <button
                                onClick={() => setShowForm(true)}
                                className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                <Plus size={20} />
                                Nuevo {activeTab.slice(0, -1)}
                            </button>
                        )}
                    </div>

                    {showForm ? (
                        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-8">
                            <h3 className="text-lg font-medium mb-6">{editingId ? 'Editar' : 'Crear'} {activeTab.slice(0, -1)}</h3>
                            {renderForm()}
                        </div>
                    ) : (
                        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-gray-50 border-b border-gray-200">
                                        <tr>
                                            {activeTab === 'sucursales' && (
                                                <>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Nombre</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Organización</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Código</th>
                                                </>
                                            )}
                                            {activeTab === 'organizaciones' && (
                                                <>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Nombre</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">RIF</th>
                                                </>
                                            )}
                                            {activeTab === 'acueductos' && (
                                                <>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Nombre</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Sucursal</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Ubicación</th>
                                                </>
                                            )}
                                            {activeTab === 'usuarios' && (
                                                <>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Usuario</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Rol</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Sucursal</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Estado</th>
                                                </>
                                            )}
                                            {activeTab === 'pipes' && (
                                                <>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">SKU</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Nombre</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Material</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Diámetro</th>
                                                </>
                                            )}
                                            {activeTab === 'pumps' && (
                                                <>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">SKU</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Marca/Modelo</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Potencia</th>
                                                    <th className="px-6 py-4 font-semibold text-gray-700">Serie</th>
                                                </>
                                            )}
                                            <th className="px-6 py-4 font-semibold text-gray-700 text-right">Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200">
                                        {loading ? (
                                            <tr><td colSpan="5" className="px-6 py-8 text-center text-gray-500">Cargando datos...</td></tr>
                                        ) : (
                                            (() => {
                                                let items = [];
                                                if (activeTab === 'sucursales') items = sucursales;
                                                else if (activeTab === 'organizaciones') items = organizaciones;
                                                else if (activeTab === 'acueductos') items = acueductos;
                                                else if (activeTab === 'usuarios') items = usuarios;
                                                else if (activeTab === 'pipes') items = pipes;
                                                else if (activeTab === 'pumps') items = pumps;

                                                if (items.length === 0) {
                                                    return <tr><td colSpan="5" className="px-6 py-8 text-center text-gray-500">No se encontraron registros</td></tr>;
                                                }

                                                return items.map(item => (
                                                    <tr key={item.id} className="hover:bg-gray-50 transition">
                                                        {activeTab === 'sucursales' && (
                                                            <>
                                                                <td className="px-6 py-4 font-medium text-gray-900">{item.nombre}</td>
                                                                <td className="px-6 py-4 text-gray-600">{item.organizacion_central_nombre || '-'}</td>
                                                                <td className="px-6 py-4 text-gray-600">{item.codigo}</td>
                                                            </>
                                                        )}
                                                        {activeTab === 'organizaciones' && (
                                                            <>
                                                                <td className="px-6 py-4 font-medium text-gray-900">{item.nombre}</td>
                                                                <td className="px-6 py-4 text-gray-600">{item.rif}</td>
                                                            </>
                                                        )}
                                                        {activeTab === 'acueductos' && (
                                                            <>
                                                                <td className="px-6 py-4 font-medium text-gray-900">{item.nombre}</td>
                                                                <td className="px-6 py-4 text-gray-600">{item.sucursal_nombre || '-'}</td>
                                                                <td className="px-6 py-4 text-gray-600">{item.ubicacion}</td>
                                                            </>
                                                        )}
                                                        {activeTab === 'usuarios' && (
                                                            <>
                                                                <td className="px-6 py-4">
                                                                    <div className="font-medium text-gray-900">{item.username}</div>
                                                                    <div className="text-gray-500">{item.email}</div>
                                                                </td>
                                                                <td className="px-6 py-4">
                                                                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${item.role === 'ADMIN' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                                                                        }`}>
                                                                        {item.role}
                                                                    </span>
                                                                </td>
                                                                <td className="px-6 py-4 text-gray-600">{item.sucursal_nombre || 'N/A'}</td>
                                                                <td className="px-6 py-4">
                                                                    <span className={`h-2.5 w-2.5 rounded-full inline-block mr-2 ${item.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                                                    {item.is_active ? 'Activo' : 'Inactivo'}
                                                                </td>
                                                            </>
                                                        )}
                                                        {activeTab === 'pipes' && (
                                                            <>
                                                                <td className="px-6 py-4 font-mono text-xs">{item.sku}</td>
                                                                <td className="px-6 py-4 font-medium">{item.nombre}</td>
                                                                <td className="px-6 py-4">{item.material_display || item.material}</td>
                                                                <td className="px-6 py-4">{item.diametro_display}</td>
                                                            </>
                                                        )}
                                                        {activeTab === 'pumps' && (
                                                            <>
                                                                <td className="px-6 py-4 font-mono text-xs">{item.sku}</td>
                                                                <td className="px-6 py-4 font-medium">{item.marca} - {item.modelo}</td>
                                                                <td className="px-6 py-4">{item.potencia_display}</td>
                                                                <td className="px-6 py-4">{item.numero_serie}</td>
                                                            </>
                                                        )}
                                                        <td className="px-6 py-4 text-right">
                                                            <div className="flex justify-end gap-2">
                                                                {['organizaciones', 'sucursales', 'acueductos', 'usuarios'].includes(activeTab) && (
                                                                    <>
                                                                        <button onClick={() => handleEdit(item)} className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition" title="Editar">
                                                                            <Edit2 size={18} />
                                                                        </button>
                                                                        <button onClick={() => handleDelete(item.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition" title="Eliminar">
                                                                            <Trash2 size={18} />
                                                                        </button>
                                                                    </>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                ));
                                            })()
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}
