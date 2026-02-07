import { useState, useEffect } from 'react';
import { ProductService } from '../services/productService';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Package, Droplet, Cylinder, Zap, Settings, Plus, Edit2, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Products() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('unidades');

    const tabs = [
        { id: 'unidades', label: 'Unidades', icon: Settings },
        { id: 'quimicos', label: 'Químicos', icon: Droplet },
        { id: 'tuberias', label: 'Tuberías', icon: Cylinder },
        { id: 'equipos', label: 'Equipos', icon: Zap },
        { id: 'accesorios', label: 'Accesorios', icon: Package },
    ];

    return (
        <div>
            <div className="row mb-4">
                <div className="col-12">
                    <h1 className="h3 mb-0">Gestión de Productos</h1>
                    <p className="text-muted">Administración de inventario por tipo</p>
                </div>
            </div>

            <div className="card card-primary card-outline card-tabs">
                <div className="card-header p-0 pt-1 border-bottom-0">
                    <ul className="nav nav-tabs" role="tablist">
                        {tabs.map(tab => (
                            <li key={tab.id} className="nav-item">
                                <a
                                    className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                                    onClick={() => setActiveTab(tab.id)}
                                    role="button"
                                >
                                    <tab.icon size={16} className="mr-2" />
                                    {tab.label}
                                </a>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="card-body">
                    <div className="tab-content">
                        {activeTab === 'unidades' && <UnitsTab />}
                        {activeTab === 'quimicos' && <GenericProductTab type="quimicos" title="Productos Químicos" />}
                        {activeTab === 'tuberias' && <GenericProductTab type="tuberias" title="Tuberías" />}
                        {activeTab === 'equipos' && <GenericProductTab type="equipos" title="Bombas y Motores" />}
                        {activeTab === 'accesorios' && <GenericProductTab type="accesorios" title="Accesorios" />}
                    </div>
                </div>
            </div>
        </div>
    );
}

function UnitsTab() {
    const { addNotification } = useNotifications();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await ProductService.unidades.getAll();
            setItems(res.data.results || res.data);
        } catch (e) {
            addNotification({ type: 'error', message: 'Error cargando unidades' });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-4">Cargando...</div>;

    return (
        <div>
            <div className="mb-3">
                <button className="btn btn-primary btn-sm"><Plus size={16} /> Nueva Unidad</button>
            </div>
            <table className="table table-striped">
                <thead><tr><th>Código</th><th>Nombre</th><th>Acciones</th></tr></thead>
                <tbody>
                    {items.map(i => (
                        <tr key={i.id}>
                            <td>{i.codigo}</td>
                            <td>{i.nombre}</td>
                            <td>...</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

function GenericProductTab({ type, title }) {
    const { addNotification } = useNotifications();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, [type]);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await ProductService[type].getAll();
            setItems(res.data.results || res.data);
        } catch (e) {
            console.error(e);
            addNotification({ type: 'error', message: `Error cargando ${title}` });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-4">Cargando...</div>;

    return (
        <div>
            <div className="d-flex justify-content-between mb-3">
                <h5>{title}</h5>
                <button className="btn btn-primary btn-sm"><Plus size={16} /> Nuevo</button>
            </div>

            <div className="table-responsive">
                <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Descripción</th>
                            <th>Stock</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.length === 0 ? (
                            <tr><td colSpan="4" className="text-center">No hay registros</td></tr>
                        ) : (
                            items.map(i => (
                                <tr key={i.id}>
                                    <td>{i.nombre}</td>
                                    <td>{i.descripcion || '-'}</td>
                                    <td>{i.stock_actual || 0}</td>
                                    <td>
                                        <button className="btn btn-sm btn-outline-primary mr-1"><Edit2 size={12} /></button>
                                        <button className="btn btn-sm btn-outline-danger"><Trash2 size={12} /></button>
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
