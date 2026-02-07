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

// Modular Components
import InventoryHeader from '../components/inventory/InventoryHeader';
import InventoryTabs from '../components/inventory/InventoryTabs';
import InventoryTable from '../components/inventory/InventoryTable';

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
            console.error("Error loading aux data", err);
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
                    message: 'El artículo se guardó correctamente',
                    duration: 3000
                });
            } else {
                await service.create(payload);
                addNotification({
                    type: 'success',
                    title: 'Artículo creado',
                    message: 'El artículo se registró correctamente',
                    duration: 3000
                });
            }
            resetForm();
            fetchItems();
        } catch (err) {
            console.error("Error saving product", err);
            const msg = err.response?.data?.detail || JSON.stringify(err.response?.data) || "Error al guardar";
            addNotification({
                type: 'error',
                title: 'Error',
                message: 'No se pudo guardar el artículo',
                duration: 5000
            });
        }
    };

    const handleDelete = async (id) => {
        const result = await Swal.fire({
            title: '¿Estás seguro?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
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
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const filteredItems = items.filter(item => {
        const term = searchTerm.toLowerCase();
        return (
            (item.nombre && item.nombre.toLowerCase().includes(term)) ||
            (item.sku && item.sku.toLowerCase().includes(term)) ||
            (item.descripcion && item.descripcion.toLowerCase().includes(term))
        );
    });

    const currentTab = tabs.find(t => t.id === activeTab);

    return (
        <div>
            <InventoryHeader
                showForm={showForm}
                editingId={editingId}
                onToggleForm={() => {
                    if (showForm && !editingId) setShowForm(false);
                    else { setEditingId(null); setShowForm(true); }
                }}
                currentTabLabel={currentTab?.label}
                isAdmin={user?.is_admin}
            />

            <section className="content">
                <div className="container-fluid">
                    {/* Form area remain in the main page for now for easier prop management */}
                    {showForm && (
                        <div className="row mb-4">
                            <div className="col-12">
                                <AdminLTEWidget
                                    type="card"
                                    title={`${editingId ? 'Editar' : 'Crear'} ${currentTab?.label.slice(0, -1)}`}
                                    color={editingId ? 'info' : 'success'}
                                    collapsible={false}
                                    removable={true}
                                    onRemove={resetForm}
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

                    <div className="row">
                        <div className="col-12">
                            <div className="card card-primary card-outline card-tabs">
                                <InventoryTabs
                                    tabs={tabs}
                                    activeTab={activeTab}
                                    onTabChange={(id) => {
                                        setActiveTab(id);
                                        setShowForm(false);
                                        setEditingId(null);
                                    }}
                                />
                                <InventoryTable
                                    items={filteredItems}
                                    loading={loading}
                                    searchTerm={searchTerm}
                                    onSearchChange={setSearchTerm}
                                    onRefresh={fetchItems}
                                    onEdit={handleEdit}
                                    onDelete={handleDelete}
                                    isAdmin={user?.is_admin}
                                />
                                <div className="card-footer clearfix">
                                    <ul className="pagination pagination-sm m-0 float-right">
                                        <li className="page-item"><a className="page-link" href="#">&laquo;</a></li>
                                        <li className="page-item active"><a className="page-link" href="#">1</a></li>
                                        <li className="page-item"><a className="page-link" href="#">&raquo;</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}