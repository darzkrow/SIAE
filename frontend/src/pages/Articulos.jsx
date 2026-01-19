import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import ChemicalForm from '../components/forms/ChemicalForm';
import PipeForm from '../components/forms/PipeForm';
import PumpForm from '../components/forms/PumpForm';
import AccessoryForm from '../components/forms/AccessoryForm';
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

    // marcas para bombas
    const [marcas, setMarcas] = useState([]);

    useEffect(() => {
        fetchAuxData();
    }, []);

    useEffect(() => {
        fetchItems();
    }, [activeTab]);

    const fetchAuxData = async () => {
        try {
            const [catRes, unitRes, supRes, marRes] = await Promise.all([
                InventoryService.categories.getAll(),
                InventoryService.units.getAll(),
                InventoryService.suppliers.getAll(),
                InventoryService.marcas.getAll()
            ]);
            setCategorias(catRes.data.results || catRes.data);
            setUnits(unitRes.data.results || unitRes.data);
            setSuppliers(supRes.data.results || supRes.data);
            setMarcas(marRes.data.results || marRes.data);
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

    const handleSubmitByType = async (payload) => {
        try {
            let service;
            switch (activeTab) {
                case 'chemical': service = InventoryService.chemicals; break;
                case 'pipe': service = InventoryService.pipes; break;
                case 'pump': service = InventoryService.pumps; break;
                case 'accessory': service = InventoryService.accessories; break;
                default: return;
            }
            if (editingId) {
                await service.update(editingId, payload);
                Swal.fire('Actualizado', 'Artículo actualizado', 'success');
            } else {
                await service.create(payload);
                Swal.fire('Creado', 'Artículo creado', 'success');
            }
            setEditingId(null);
            setShowForm(false);
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
        setEditingId(null);
        setShowForm(false);
    };

    const handleEdit = (item) => {
        setEditingId(item.id);
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
                    {activeTab === 'chemical' && (
                      <ChemicalForm categorias={categorias} units={units} suppliers={suppliers} initialData={editingId ? items.find(i => i.id === editingId) : {}} onSubmit={handleSubmitByType} onCancel={resetForm} />
                    )}
                    {activeTab === 'pipe' && (
                      <PipeForm categorias={categorias} units={units} suppliers={suppliers} initialData={editingId ? items.find(i => i.id === editingId) : {}} onSubmit={handleSubmitByType} onCancel={resetForm} />
                    )}
                    {activeTab === 'pump' && (
                      <PumpForm categorias={categorias} units={units} suppliers={suppliers} marcas={marcas} initialData={editingId ? items.find(i => i.id === editingId) : {}} onSubmit={handleSubmitByType} onCancel={resetForm} />
                    )}
                    {activeTab === 'accessory' && (
                      <AccessoryForm categorias={categorias} units={units} suppliers={suppliers} initialData={editingId ? items.find(i => i.id === editingId) : {}} onSubmit={handleSubmitByType} onCancel={resetForm} />
                    )}
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