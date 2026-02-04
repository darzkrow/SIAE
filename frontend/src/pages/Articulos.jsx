import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import ChemicalForm from '../components/forms/ChemicalForm';
import PipeForm from '../components/forms/PipeForm';
import PumpForm from '../components/forms/PumpForm';
import AccessoryForm from '../components/forms/AccessoryForm';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Plus, Search, Edit2, Trash2, Package, Droplets, Activity, Wrench } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Articulos() {
    const { user } = useAuth();
    const { addNotification } = useNotifications();
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
    const [marcas, setMarcas] = useState([]);

    const tabs = [
        { id: 'chemical', label: 'Químicos', icon: Package, color: 'primary' },
        { id: 'pipe', label: 'Tuberías', icon: Droplets, color: 'info' },
        { id: 'pump', label: 'Bombas', icon: Activity, color: 'success' },
        { id: 'accessory', label: 'Accesorios', icon: Wrench, color: 'warning' },
    ];

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
            addNotification({
                type: 'error',
                title: 'Error de carga',
                message: 'No se pudieron cargar los datos auxiliares',
                duration: 5000
            });
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
            addNotification({
                type: 'error',
                title: 'Error de conexión',
                message: 'No se pudieron cargar los artículos',
                duration: 5000
            });
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
                addNotification({
                    type: 'success',
                    title: 'Artículo actualizado',
                    message: 'El artículo se actualizó correctamente',
                    duration: 3000
                });
            } else {
                await service.create(payload);
                addNotification({
                    type: 'success',
                    title: 'Artículo creado',
                    message: 'El artículo se creó correctamente',
                    duration: 3000
                });
            }
            setEditingId(null);
            setShowForm(false);
            fetchItems();
        } catch (err) {
            console.error("Error saving item", err);
            const msg = err.response?.data?.detail || JSON.stringify(err.response?.data) || "Error al guardar";
            addNotification({
                type: 'error',
                title: 'Error',
                message: msg,
                duration: 5000
            });
        }
    };

    const handleDelete = async (id) => {
        const result = await Swal.fire({
            title: '¿Eliminar artículo?',
            text: '¿Está seguro de eliminar este artículo?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });

        if (result.isConfirmed) {
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
                addNotification({
                    type: 'success',
                    title: 'Artículo eliminado',
                    message: 'El artículo se eliminó correctamente',
                    duration: 3000
                });
            } catch (err) {
                console.error("Error deleting", err);
                addNotification({
                    type: 'error',
                    title: 'Error',
                    message: 'No se pudo eliminar el artículo',
                    duration: 5000
                });
            }
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
        (item.nombre && item.nombre.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (item.sku && item.sku.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const currentTab = tabs.find(t => t.id === activeTab);

    return (
        <div>
            {/* Header */}
            <div className="row mb-4">
                <div className="col-sm-6">
                    <h1 className="h3 mb-0">
                        <Package className="mr-2" size={24} />
                        Catálogo de Artículos
                    </h1>
                    <p className="text-muted mb-0">
                        Gestión de productos del inventario
                    </p>
                </div>
                <div className="col-sm-6">
                    <div className="float-sm-right">
                        {user?.is_admin && (
                            <button
                                onClick={() => setShowForm(!showForm)}
                                className="btn btn-primary"
                            >
                                <Plus size={16} className="mr-2" /> 
                                Nuevo {currentTab?.label.slice(0, -1)}
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Tabs Navigation */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header p-2">
                            <ul className="nav nav-pills">
                                {tabs.map(tab => {
                                    const Icon = tab.icon;
                                    return (
                                        <li key={tab.id} className="nav-item">
                                            <button
                                                onClick={() => { 
                                                    setActiveTab(tab.id); 
                                                    setShowForm(false); 
                                                    setEditingId(null);
                                                }}
                                                className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                                            >
                                                <Icon size={16} className="mr-2" />
                                                {tab.label}
                                            </button>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            {/* Form */}
            {showForm && (
                <div className="row mb-4">
                    <div className="col-12">
                        <AdminLTEWidget 
                            type="card" 
                            title={`${editingId ? 'Editar' : 'Crear'} ${currentTab?.label.slice(0, -1)}`}
                            color="primary"
                        >
                            {activeTab === 'chemical' && (
                              <ChemicalForm 
                                categorias={categorias} 
                                units={units} 
                                suppliers={suppliers} 
                                initialData={editingId ? items.find(i => i.id === editingId) : {}} 
                                onSubmit={handleSubmitByType} 
                                onCancel={resetForm} 
                              />
                            )}
                            {activeTab === 'pipe' && (
                              <PipeForm 
                                categorias={categorias} 
                                units={units} 
                                suppliers={suppliers} 
                                initialData={editingId ? items.find(i => i.id === editingId) : {}} 
                                onSubmit={handleSubmitByType} 
                                onCancel={resetForm} 
                              />
                            )}
                            {activeTab === 'pump' && (
                              <PumpForm 
                                categorias={categorias} 
                                units={units} 
                                suppliers={suppliers} 
                                marcas={marcas} 
                                initialData={editingId ? items.find(i => i.id === editingId) : {}} 
                                onSubmit={handleSubmitByType} 
                                onCancel={resetForm} 
                              />
                            )}
                            {activeTab === 'accessory' && (
                              <AccessoryForm 
                                categorias={categorias} 
                                units={units} 
                                suppliers={suppliers} 
                                initialData={editingId ? items.find(i => i.id === editingId) : {}} 
                                onSubmit={handleSubmitByType} 
                                onCancel={resetForm} 
                              />
                            )}
                        </AdminLTEWidget>
                    </div>
                </div>
            )}

            {/* Search and List */}
            <AdminLTEWidget 
                type="table" 
                title={`Lista de ${currentTab?.label}`}
                icon={currentTab?.icon}
                color={currentTab?.color}
                onRefresh={fetchItems}
            >
                <div className="row mb-3">
                    <div className="col-md-6">
                        <div className="input-group">
                            <div className="input-group-prepend">
                                <span className="input-group-text">
                                    <Search size={16} />
                                </span>
                            </div>
                            <input
                                type="text"
                                placeholder="Buscar artículos..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="form-control"
                            />
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="float-right">
                            <span className="badge badge-info">
                                {filteredItems.length} artículos encontrados
                            </span>
                        </div>
                    </div>
                </div>
                
                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>SKU</th>
                                <th>Nombre</th>
                                <th>Categoría</th>
                                <th>Stock</th>
                                {user?.is_admin && <th>Acciones</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={user?.is_admin ? "5" : "4"} className="text-center py-4">
                                        <div className="spinner-border text-primary" role="status">
                                            <span className="sr-only">Cargando...</span>
                                        </div>
                                        <p className="mt-2 text-muted">Cargando artículos...</p>
                                    </td>
                                </tr>
                            ) : filteredItems.length === 0 ? (
                                <tr>
                                    <td colSpan={user?.is_admin ? "5" : "4"} className="text-center py-4 text-muted">
                                        <Package size={24} className="mb-2" />
                                        <p>No se encontraron artículos</p>
                                    </td>
                                </tr>
                            ) : (
                                filteredItems.map(item => (
                                    <tr key={item.id}>
                                        <td>
                                            <code className="text-sm">{item.sku || '-'}</code>
                                        </td>
                                        <td className="font-weight-bold">{item.nombre}</td>
                                        <td>
                                            <span className="badge badge-secondary">
                                                {item.categoria_nombre || item.categoria?.nombre || '-'}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge ${(item.stock_actual || 0) > 10 ? 'badge-success' : (item.stock_actual || 0) > 0 ? 'badge-warning' : 'badge-danger'}`}>
                                                {item.stock_actual || 0} {item.unidad_medida_nombre || ''}
                                            </span>
                                        </td>
                                        {user?.is_admin && (
                                            <td>
                                                <div className="btn-group btn-group-sm">
                                                    <button 
                                                        onClick={() => handleEdit(item)} 
                                                        className="btn btn-outline-info"
                                                        title="Editar"
                                                    >
                                                        <Edit2 size={14} />
                                                    </button>
                                                    <button 
                                                        onClick={() => handleDelete(item.id)} 
                                                        className="btn btn-outline-danger"
                                                        title="Eliminar"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                </div>
                                            </td>
                                        )}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                
                {filteredItems.length > 0 && (
                    <div className="card-footer">
                        <small className="text-muted">
                            Mostrando {filteredItems.length} de {items.length} artículos
                        </small>
                    </div>
                )}
            </AdminLTEWidget>
        </div>
    );
}