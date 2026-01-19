import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { Plus, Search, Edit2, Trash2, Package, Droplets, Activity, Wrench } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Articulos() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('chemical');
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Aux Data
    const [categorias, setCategorias] = useState([]);
    const [units, setUnits] = useState([]);
    const [suppliers, setSuppliers] = useState([]);

    const tabs = [
        { id: 'chemical', label: 'Químicos', icon: <Package size={18} /> },
        { id: 'pipe', label: 'Tuberías', icon: <Droplets size={18} /> },
        { id: 'pump', label: 'Bombas', icon: <Activity size={18} /> },
        { id: 'accessory', label: 'Accesorios', icon: <Wrench size={18} /> },
    ];

    const [formData, setFormData] = useState({
        nombre: '',
        descripcion: '',
        categoria: '',
        unidad_medida: '',
        proveedor: '',
        stock_minimo: 0,
        precio_unitario: 0,
        // Pipe
        material: 'PVC',
        diametro_nominal: 0,
        // Pump
        tipo_equipo: 'BOMBA_CENTRIFUGA',
        marca: '',
        modelo: '',
        numero_serie: '',
        potencia_hp: 0,
        voltaje: 110,
        fases: 'MONOFASICO',
        // Chemical
        tipo_presentacion: 'SACO',
        es_peligroso: false
    });

    useEffect(() => {
        fetchAuxData();
    }, []);

    useEffect(() => {
        fetchItems();
    }, [activeTab]);

    const fetchAuxData = async () => {
        try {
            const [catRes, unitRes, supRes] = await Promise.all([
                InventoryService.categories.getAll(),
                InventoryService.units.getAll(),
                InventoryService.suppliers.getAll()
            ]);
            setCategorias(catRes.data.results || catRes.data);
            setUnits(unitRes.data.results || unitRes.data);
            setSuppliers(supRes.data.results || supRes.data);
        } catch (err) {
            console.error("Error loading auxiliary data", err);
        }
    };

    const fetchItems = async () => {
        setLoading(true);
        try {
            let res;
            switch (activeTab) {
                case 'chemical': res = await InventoryService.chemicals.getAll(); break;
                case 'pipe': res = await InventoryService.pipes.getAll(); break;
                case 'pump': res = await InventoryService.pumps.getAll(); break;
                case 'accessory': res = await InventoryService.accessories.getAll(); break;
                default: res = { data: [] };
            }
            setItems(res.data.results || res.data);
        } catch (err) {
            console.error("Error fetching items", err);
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

    const validateForm = () => {
        if (!formData.nombre || !formData.categoria || !formData.unidad_medida || !formData.proveedor) {
            Swal.fire('Error', 'Complete los campos obligatorios', 'error');
            return false;
        }
        if (activeTab === 'pump') {
            const requiredPump = ['tipo_equipo', 'marca', 'modelo', 'numero_serie', 'potencia_hp', 'voltaje', 'fases'];
            const missing = requiredPump.filter(k => !formData[k] && formData[k] !== 0);
            if (missing.length) {
                Swal.fire('Error', 'Complete los datos de la bomba: tipo, marca, modelo, serial, potencia, voltaje y fases', 'error');
                return false;
            }
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        try {
            const payload = { ...formData };
            // Limpieza de datos según tab (opcional pero recomendable)

            let service;
            switch (activeTab) {
                case 'chemical': service = InventoryService.chemicals; break;
                case 'pipe': service = InventoryService.pipes; break;
                case 'pump': service = InventoryService.pumps; break;
                case 'accessory': service = InventoryService.accessories; break;
            }

            if (editingId) {
                await service.update(editingId, payload);
                Swal.fire('Actualizado', 'Artículo actualizado', 'success');
            } else {
                await service.create(payload);
                Swal.fire('Creado', 'Artículo creado', 'success');
            }

            resetForm();
            fetchItems();
        } catch (err) {
            console.error("Error saving item", err);
            const msg = err.response?.data?.detail || JSON.stringify(err.response?.data) || "Error al guardar";
            Swal.fire('Error', msg, 'error');
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Eliminar este artículo?')) return;
        try {
            let service;
            switch (activeTab) {
                case 'chemical': service = InventoryService.chemicals; break;
                case 'pipe': service = InventoryService.pipes; break;
                case 'pump': service = InventoryService.pumps; break;
                case 'accessory': service = InventoryService.accessories; break;
            }
            await service.delete(id);
            fetchItems();
            Swal.fire('Eliminado', 'Artículo eliminado', 'success');
        } catch (err) {
            console.error("Error deleting", err);
            Swal.fire('Error', 'No se pudo eliminar', 'error');
        }
    };

    const resetForm = () => {
        setFormData({
            nombre: '', descripcion: '', categoria: '', unidad_medida: '', proveedor: '',
            stock_minimo: 0, precio_unitario: 0,
            // Pipe
            material: 'PVC', diametro_nominal: 0,
            // Pump
            tipo_equipo: 'BOMBA_CENTRIFUGA', marca: '', modelo: '', numero_serie: '', potencia_hp: 0, voltaje: 110, fases: 'MONOFASICO',
            // Chemical
            tipo_presentacion: 'SACO', es_peligroso: false
        });
        setEditingId(null);
        setShowForm(false);
    };

    const handleEdit = (item) => {
        setEditingId(item.id);
        setFormData({
            ...item,
            categoria: item.categoria?.id || item.categoria, // Ajustar según lo que devuelva el serializer
            unidad_medida: item.unidad_medida?.id || item.unidad_medida,
            proveedor: item.proveedor?.id || item.proveedor
        });
        setShowForm(true);
    };

    const filteredItems = items.filter(item =>
        item.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.sku && item.sku.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Catálogo de Artículos</h1>
                {user?.is_admin && (
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                        <Plus size={20} /> Nuevo {tabs.find(t => t.id === activeTab)?.label.slice(0, -1)}
                    </button>
                )}
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow p-2 flex overflow-x-auto gap-2">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => { setActiveTab(tab.id); setShowForm(false); }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition whitespace-nowrap ${activeTab === tab.id
                                ? 'bg-blue-600 text-white font-medium'
                                : 'text-gray-600 hover:bg-gray-100'
                            }`}
                    >
                        {tab.icon} {tab.label}
                    </button>
                ))}
            </div>

            {/* Form */}
            {showForm && (
                <div className="bg-white rounded-lg shadow p-6 border-blue-500 border-l-4">
                    <h2 className="text-xl font-bold mb-4">{editingId ? 'Editar' : 'Crear'} Artículo</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Common Fields */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium mb-1">Nombre *</label>
                                <input name="nombre" value={formData.nombre} onChange={handleFormChange} className="w-full border p-2 rounded" required />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Categoría *</label>
                                <select name="categoria" value={formData.categoria} onChange={handleFormChange} className="w-full border p-2 rounded" required>
                                    <option value="">Seleccionar...</option>
                                    {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Unidad *</label>
                                <select name="unidad_medida" value={formData.unidad_medida} onChange={handleFormChange} className="w-full border p-2 rounded" required>
                                    <option value="">Seleccionar...</option>
                                    {units.map(u => <option key={u.id} value={u.id}>{u.nombre} ({u.simbolo})</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Proveedor *</label>
                                <select name="proveedor" value={formData.proveedor} onChange={handleFormChange} className="w-full border p-2 rounded" required>
                                    <option value="">Seleccionar...</option>
                                    {suppliers.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Minimo Stock</label>
                                <input type="number" name="stock_minimo" value={formData.stock_minimo} onChange={handleFormChange} className="w-full border p-2 rounded" />
                            </div>

                            {/* Specific Fields */}
                            {activeTab === 'pipe' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Material</label>
                                        <select name="material" value={formData.material} onChange={handleFormChange} className="w-full border p-2 rounded">
                                            <option value="PVC">PVC</option>
                                            <option value="PEAD">PEAD</option>
                                            <option value="ACERO">Acero</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Diámetro (mm)</label>
                                        <input type="number" name="diametro_nominal" value={formData.diametro_nominal} onChange={handleFormChange} className="w-full border p-2 rounded" />
                                    </div>
                                </>
                            )}
                            {activeTab === 'pump' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Tipo de equipo</label>
                                        <select name="tipo_equipo" value={formData.tipo_equipo} onChange={handleFormChange} className="w-full border p-2 rounded">
                                            <option value="BOMBA_CENTRIFUGA">Bomba Centrífuga</option>
                                            <option value="BOMBA_SUMERGIBLE">Bomba Sumergible</option>
                                            <option value="BOMBA_PERIFERICA">Bomba Periférica</option>
                                            <option value="BOMBA_TURBINA">Bomba de Turbina</option>
                                            <option value="MOTOR_ELECTRICO">Motor Eléctrico</option>
                                            <option value="VARIADOR">Variador de Frecuencia</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Marca</label>
                                        <select name="marca" value={formData.marca} onChange={handleFormChange} className="w-full border p-2 rounded">
                                            <option value="">Seleccionar...</option>
                                            {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Modelo</label>
                                        <input name="modelo" value={formData.modelo} onChange={handleFormChange} className="w-full border p-2 rounded" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Número de serie</label>
                                        <input name="numero_serie" value={formData.numero_serie} onChange={handleFormChange} className="w-full border p-2 rounded" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Potencia (HP)</label>
                                        <input type="number" step="0.01" name="potencia_hp" value={formData.potencia_hp} onChange={handleFormChange} className="w-full border p-2 rounded" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Voltaje</label>
                                        <input type="number" name="voltaje" value={formData.voltaje} onChange={handleFormChange} className="w-full border p-2 rounded" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Fases</label>
                                        <select name="fases" value={formData.fases} onChange={handleFormChange} className="w-full border p-2 rounded">
                                            <option value="MONOFASICO">Monofásico</option>
                                            <option value="TRIFASICO">Trifásico</option>
                                        </select>
                                    </div>
                                </>
                            )}
                            {activeTab === 'chemical' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Presentación</label>
                                        <select name="tipo_presentacion" value={formData.tipo_presentacion} onChange={handleFormChange} className="w-full border p-2 rounded">
                                            <option value="SACO">Saco</option>
                                            <option value="TAMBOR">Tambor</option>
                                            <option value="GRANEL">Granel</option>
                                        </select>
                                    </div>
                                    <div className="flex items-end pb-2">
                                        <label className="flex items-center gap-2"><input type="checkbox" name="es_peligroso" checked={formData.es_peligroso} onChange={handleFormChange} /> Es Peligroso</label>
                                    </div>
                                </>
                            )}

                        </div>
                        <div className="flex gap-2 justify-end">
                            <button type="button" onClick={resetForm} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Cancelar</button>
                            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Guardar</button>
                        </div>
                    </form>
                </div>
            )}

            {/* List */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="relative mb-4">
                    <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Buscar..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border rounded-lg"
                    />
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-4 py-2 text-left">SKU</th>
                                <th className="px-4 py-2 text-left">Nombre</th>
                                <th className="px-4 py-2 text-left">Categoría</th>
                                <th className="px-4 py-2 text-left">Stock</th>
                                {user?.is_admin && <th className="px-4 py-2 text-left">Acciones</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? <tr><td colSpan="5" className="p-4 text-center">Cargando...</td></tr> :
                                filteredItems.map(item => (
                                    <tr key={item.id} className="border-b hover:bg-gray-50">
                                        <td className="px-4 py-2 text-sm text-gray-500">{item.sku}</td>
                                        <td className="px-4 py-2 font-medium">{item.nombre}</td>
                                        <td className="px-4 py-2 text-sm">{item.categoria_nombre || item.categoria?.nombre}</td>
                                        <td className="px-4 py-2 text-sm">{item.stock_actual} {item.unidad_medida_nombre || ''}</td>
                                        {user?.is_admin && (
                                            <td className="px-4 py-2 flex gap-2">
                                                <button onClick={() => handleEdit(item)} className="text-blue-600"><Edit2 size={16} /></button>
                                                <button onClick={() => handleDelete(item.id)} className="text-red-600"><Trash2 size={16} /></button>
                                            </td>
                                        )}
                                    </tr>
                                ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}