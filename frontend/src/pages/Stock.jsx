import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Search, Package, Droplets, Activity, Wrench, AlertTriangle, TrendingUp, PlusCircle, MinusCircle } from 'lucide-react';

export default function Stock() {
    const navigate = useNavigate();
    const { addNotification } = useNotifications();
    const [activeTab, setActiveTab] = useState('chemical');
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [stats, setStats] = useState({
        total: 0,
        sinStock: 0,
        stockBajo: 0,
        stockNormal: 0
    });

    const tabs = [
        { id: 'chemical', label: 'Químicos', icon: Package, color: 'primary' },
        { id: 'pipe', label: 'Tuberías', icon: Droplets, color: 'info' },
        { id: 'pump', label: 'Bombas/Equipos', icon: Activity, color: 'success' },
        { id: 'accessory', label: 'Accesorios', icon: Wrench, color: 'warning' },
    ];

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const fetchData = async () => {
        setLoading(true);
        setItems([]);
        try {
            let res;
            switch (activeTab) {
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

            const itemsData = res.data.results || res.data;
            setItems(itemsData);

            // Calcular estadísticas
            const stats = {
                total: itemsData.length,
                sinStock: itemsData.filter(item => (item.stock_actual || item.cantidad || 0) === 0).length,
                stockBajo: itemsData.filter(item => {
                    const stock = item.stock_actual || item.cantidad || 0;
                    return stock > 0 && stock <= 5;
                }).length,
                stockNormal: itemsData.filter(item => (item.stock_actual || item.cantidad || 0) > 5).length
            };
            setStats(stats);

        } catch (err) {
            console.error("Error fetching stock data", err);
            addNotification({
                type: 'error',
                title: 'Error de conexión',
                message: 'No se pudieron cargar los datos de stock',
                duration: 5000
            });
        } finally {
            setLoading(false);
        }
    };

    const filteredItems = items.filter(item => {
        const term = searchTerm.toLowerCase();
        return (
            (item.nombre && item.nombre.toLowerCase().includes(term)) ||
            (item.sku && item.sku.toLowerCase().includes(term)) ||
            (item.marca && item.marca.toLowerCase().includes(term))
        );
    });

    const getStockBadgeClass = (cantidad) => {
        if (cantidad === 0 || cantidad === undefined) return 'badge-danger';
        if (cantidad <= 5) return 'badge-warning';
        return 'badge-success';
    };

    const getStockLabel = (cantidad) => {
        if (cantidad === 0 || cantidad === undefined) return 'Sin stock';
        if (cantidad <= 5) return 'Stock bajo';
        return 'Normal';
    };

    const currentTab = tabs.find(t => t.id === activeTab);

    return (
        <div>
            {/* Header */}
            <div className="row mb-4">
                <div className="col-12">
                    <h1 className="h3 mb-0">
                        <Package className="mr-2" size={24} />
                        Inventario de Stock
                    </h1>
                    <p className="text-muted mb-0">
                        Gestión y control de stock por categorías
                    </p>
                </div>
            </div>

            {/* Stats */}
            <div className="row mb-4">
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Total Artículos"
                        value={stats.total}
                        icon={Package}
                        color="info"
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Sin Stock"
                        value={stats.sinStock}
                        icon={AlertTriangle}
                        color="danger"
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Stock Bajo"
                        value={stats.stockBajo}
                        icon={AlertTriangle}
                        color="warning"
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Stock Normal"
                        value={stats.stockNormal}
                        icon={TrendingUp}
                        color="success"
                    />
                </div>
            </div>

            {/* Tabs */}
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
                                                onClick={() => setActiveTab(tab.id)}
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

            {/* Search */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-body">
                            <div className="input-group">
                                <div className="input-group-prepend">
                                    <span className="input-group-text">
                                        <Search size={16} />
                                    </span>
                                </div>
                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="Buscar por nombre, código o marca..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stock Table */}
            <AdminLTEWidget
                type="table"
                title={`Stock de ${currentTab?.label}`}
                icon={currentTab?.icon}
                color={currentTab?.color}
                onRefresh={fetchData}
            >
                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Nombre</th>
                                <th>Marca/Modelo</th>
                                <th>Stock Actual</th>
                                <th>Unidad</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="text-center py-4">
                                        <div className="spinner-border text-primary" role="status">
                                            <span className="sr-only">Cargando...</span>
                                        </div>
                                        <p className="mt-2 text-muted">Cargando datos...</p>
                                    </td>
                                </tr>
                            ) : filteredItems.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="text-center py-4 text-muted">
                                        <Package size={24} className="mb-2" />
                                        <p>No se encontraron artículos</p>
                                    </td>
                                </tr>
                            ) : (
                                filteredItems.map(item => {
                                    const stock = item.stock_actual ?? item.cantidad ?? 0;
                                    return (
                                        <tr key={item.id}>
                                            <td><code>{item.sku || 'N/A'}</code></td>
                                            <td>{item.nombre}</td>
                                            <td>
                                                <small className="text-muted d-block">
                                                    {item.marca_nombre || item.marca || '-'}
                                                </small>
                                                {item.modelo && <span className="badge badge-light">{item.modelo}</span>}
                                            </td>
                                            <td className="font-weight-bold">
                                                {stock}
                                            </td>
                                            <td>{item.unidad_medida_simbolo || item.unidad_medida || 'UN'}</td>
                                            <td>
                                                <span className={`badge ${getStockBadgeClass(stock)}`}>
                                                    {getStockLabel(stock)}
                                                </span>
                                            </td>
                                            <td>
                                                <div className="btn-group btn-group-sm">
                                                    <button
                                                        className="btn btn-success"
                                                        title="Entrada rápida"
                                                        onClick={() => navigate('/movimientos', {
                                                            state: {
                                                                product_type: activeTab,
                                                                product_id: item.id,
                                                                type: 'ENTRADA'
                                                            }
                                                        })}
                                                    >
                                                        <PlusCircle size={14} />
                                                    </button>
                                                    <button
                                                        className="btn btn-danger"
                                                        title="Salida rápida"
                                                        onClick={() => navigate('/movimientos', {
                                                            state: {
                                                                product_type: activeTab,
                                                                product_id: item.id,
                                                                type: 'SALIDA'
                                                            }
                                                        })}
                                                    >
                                                        <MinusCircle size={14} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })
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