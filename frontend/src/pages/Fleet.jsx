import { useState, useEffect } from 'react';
import { FleetService } from '../services/fleetService';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Truck, Wrench, UserCheck, Plus, Edit2, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Fleet() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('vehiculos');

    const tabs = [
        { id: 'vehiculos', label: 'Vehículos', icon: Truck },
        { id: 'mantenimiento', label: 'Mantenimiento', icon: Wrench },
        { id: 'asignaciones', label: 'Asignaciones', icon: UserCheck },
    ];

    return (
        <div>
            <div className="row mb-4">
                <div className="col-12">
                    <h1 className="h3 mb-0">Gestión de Flota</h1>
                    <p className="text-muted">Vehículos, mantenimientos y conductores</p>
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
                        {activeTab === 'vehiculos' && <VehiclesTab />}
                        {activeTab === 'mantenimiento' && <MaintenanceTab />}
                        {activeTab === 'asignaciones' && <AssignmentsTab />}
                    </div>
                </div>
            </div>
        </div>
    );
}

function VehiclesTab() {
    const { addNotification } = useNotifications();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await FleetService.vehiculos.getAll();
            setItems(res.data.results || res.data);
        } catch (e) {
            addNotification({ type: 'error', message: 'Error cargando vehículos' });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-4">Cargando...</div>;

    return (
        <div>
            <div className="mb-3">
                <button className="btn btn-primary btn-sm"><Plus size={16} /> Nuevo Vehículo</button>
            </div>
            <div className="table-responsive">
                <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Placa</th>
                            <th>Modelo</th>
                            <th>Tipo</th>
                            <th>Estado</th>
                            <th>Kilometraje</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.length === 0 ? (
                            <tr><td colSpan="6" className="text-center">No hay vehículos registrados</td></tr>
                        ) : (
                            items.map(i => (
                                <tr key={i.id}>
                                    <td className="font-weight-bold">{i.placa}</td>
                                    <td>{i.marca} {i.modelo}</td>
                                    <td>{i.tipo_vehiculo_nombre || i.tipo_vehiculo}</td>
                                    <td>
                                        <span className={`badge badge-${i.estado === 'DISPONIBLE' ? 'success' : 'warning'}`}>
                                            {i.estado}
                                        </span>
                                    </td>
                                    <td>{i.kilometraje_actual} km</td>
                                    <td>
                                        <button className="btn btn-sm btn-outline-primary mr-1"><Edit2 size={12} /></button>
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

function MaintenanceTab() {
    const { addNotification } = useNotifications();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await FleetService.mantenimiento.getAll();
            setItems(res.data.results || res.data);
        } catch (e) {
            addNotification({ type: 'error', message: 'Error cargando mantenimientos' });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-4">Cargando...</div>;

    return (
        <div>
            <div className="mb-3">
                <button className="btn btn-warning btn-sm"><Plus size={16} /> Registrar Mantenimiento</button>
            </div>
            <table className="table table-striped">
                <thead><tr><th>Vehículo</th><th>Tipo</th><th>Fecha</th><th>Costo</th><th>Estado</th></tr></thead>
                <tbody>
                    {items.length === 0 ? (
                        <tr><td colSpan="5" className="text-center">No hay registros de mantenimiento</td></tr>
                    ) : items.map(i => (
                        <tr key={i.id}>
                            <td>{i.vehiculo_placa}</td>
                            <td>{i.tipo_mantenimiento}</td>
                            <td>{new Date(i.fecha_inicio).toLocaleDateString()}</td>
                            <td>${i.costo_total}</td>
                            <td>{i.estado}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

function AssignmentsTab() {
    const { addNotification } = useNotifications();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await FleetService.asignaciones.getAll();
            setItems(res.data.results || res.data);
        } catch (e) {
            addNotification({ type: 'error', message: 'Error cargando asignaciones' });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-4">Cargando...</div>;

    return (
        <div>
            <div className="mb-3">
                <button className="btn btn-success btn-sm"><Plus size={16} /> Asignar Vehículo</button>
            </div>
            <table className="table table-striped">
                <thead><tr><th>Vehículo</th><th>Conductor</th><th>Asignado Por</th><th>Fecha Inicio</th><th>Estado</th></tr></thead>
                <tbody>
                    {items.length === 0 ? (
                        <tr><td colSpan="5" className="text-center">No hay asignaciones activas</td></tr>
                    ) : items.map(i => (
                        <tr key={i.id}>
                            <td>{i.vehiculo_placa}</td>
                            <td>{i.conductor_nombre}</td>
                            <td>{i.asignado_por_nombre}</td>
                            <td>{new Date(i.fecha_asignacion).toLocaleDateString()}</td>
                            <td><span className={`badge badge-${i.activo ? 'success' : 'secondary'}`}>{i.activo ? 'ACTIVO' : 'FINALIZADO'}</span></td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
