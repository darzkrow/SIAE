import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Box, Monitor, Plus, Edit2, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Assets() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('materiales');

    const tabs = [
        { id: 'materiales', label: 'Materiales Estratégicos', icon: Box },
        { id: 'activos', label: 'Activos Fijos', icon: Monitor },
    ];

    return (
        <div>
            <div className="row mb-4">
                <div className="col-12">
                    <h1 className="h3 mb-0">Gestión de Activos</h1>
                    <p className="text-muted">Materiales estratégicos y activos fijos</p>
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
                        {activeTab === 'materiales' && <GenericAssetTab type="materiales" title="Materiales Estratégicos" />}
                        {activeTab === 'activos' && <GenericAssetTab type="activosFijos" title="Activos Fijos" />}
                    </div>
                </div>
            </div>
        </div>
    );
}

function GenericAssetTab({ type, title }) {
    const { addNotification } = useNotifications();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, [type]);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await InventoryService.assets[type].getAll();
            setItems(res.data.results || res.data);
        } catch (e) {
            addNotification({ type: 'error', message: `Error cargando ${title}` });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-4">Cargando...</div>;

    return (
        <div>
            <div className="mb-3">
                <button className="btn btn-primary btn-sm"><Plus size={16} /> Nuevo Registro</button>
            </div>

            <div className="table-responsive">
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Nombre/Descripción</th>
                            {type === 'activosFijos' && <th>Serial</th>}
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.length === 0 ? (
                            <tr><td colSpan="5" className="text-center">No hay registros</td></tr>
                        ) : (
                            items.map(i => (
                                <tr key={i.id}>
                                    <td>{i.codigo || i.id}</td>
                                    <td>{i.nombre || i.descripcion}</td>
                                    {type === 'activosFijos' && <td>{i.serial}</td>}
                                    <td>{i.estado || '-'}</td>
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
