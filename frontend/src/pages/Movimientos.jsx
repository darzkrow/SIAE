import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Plus, Filter, Package, TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import Swal from 'sweetalert2';

export default function Movimientos() {
    const { addNotification } = useNotifications();
    const [movimientos, setMovimientos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [stats, setStats] = useState({
        total: 0,
        entradas: 0,
        salidas: 0,
        transferencias: 0
    });

    // Filtros
    const [filtros, setFiltros] = useState({
        tipo_movimiento: '',
        fecha_desde: '',
        fecha_hasta: ''
    });

    // Formulario
    const [formData, setFormData] = useState({
        tipo_movimiento: 'ENTRADA',
        product_type: 'chemical',
        product_id: '',
        acueducto_origen: '',
        acueducto_destino: '',
        cantidad: '',
        razon: ''
    });

    // Data lists
    const [productsList, setProductsList] = useState([]);
    const [acueductos, setAcueductos] = useState([]);
    const [loadingProducts, setLoadingProducts] = useState(false);

    // Cargar datos iniciales
    useEffect(() => {
        fetchInitialData();
    }, []);

    const fetchInitialData = async () => {
        try {
            const [movRes, acuRes] = await Promise.all([
                InventoryService.movimientos.getAll(),
                InventoryService.acueductos.getAll()
            ]);
            
            const movimientos = movRes.data.results || movRes.data;
            setMovimientos(movimientos);
            setAcueductos(acuRes.data.results || acuRes.data);
            
            // Calcular estadísticas
            const stats = {
                total: movimientos.length,
                entradas: movimientos.filter(m => m.tipo_movimiento === 'ENTRADA').length,
                salidas: movimientos.filter(m => m.tipo_movimiento === 'SALIDA').length,
                transferencias: movimientos.filter(m => m.tipo_movimiento === 'TRANSFERENCIA').length
            };
            setStats(stats);
            
        } catch (err) {
            console.error("Error fetching initial data", err);
            addNotification({
                type: 'error',
                title: 'Error de conexión',
                message: 'No se pudieron cargar los movimientos. Verifique la conexión con el servidor.',
                duration: 5000
            });
        } finally {
            setLoading(false);
        }
    };

    // Cargar productos cuando cambia el tipo
    useEffect(() => {
        if (!showForm) return;
        fetchProducts();
    }, [formData.product_type, showForm]);

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

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validaciones
        if (formData.tipo_movimiento === 'TRANSFERENCIA' &&
            formData.acueducto_origen === formData.acueducto_destino) {
            Swal.fire({
                icon: 'warning',
                title: 'Acueducto Inválido',
                text: 'El acueducto destino no puede ser igual al origen'
            });
            return;
        }

        if (!formData.product_id) {
            Swal.fire({
                icon: 'warning',
                title: 'Faltan datos',
                text: 'Seleccione un producto'
            });
            return;
        }

        try {
            const payload = {
                tipo_movimiento: formData.tipo_movimiento,
                cantidad: parseInt(formData.cantidad),
                razon: formData.razon,
                product_type: formData.product_type,
                product_id: parseInt(formData.product_id),
                acueducto_origen: formData.acueducto_origen || null,
                acueducto_destino: formData.acueducto_destino || null
            };

            await InventoryService.movimientos.create(payload);

            addNotification({
                type: 'success',
                title: '¡Éxito!',
                message: 'Movimiento registrado exitosamente',
                duration: 3000
            });

            // Reset form
            setFormData(prev => ({
                ...prev,
                cantidad: '',
                razon: '',
                product_id: ''
            }));
            setShowForm(false);

            // Recargar datos
            fetchInitialData();

        } catch (err) {
            console.error("Error creating movement", err);
            const msg = err.response?.data?.detail || 'Error al crear el movimiento';
            addNotification({
                type: 'error',
                title: 'Error',
                message: msg,
                duration: 5000
            });
        }
    };

    const getTipoBadgeClass = (tipo) => {
        switch (tipo) {
            case 'ENTRADA': return 'badge-success';
            case 'SALIDA': return 'badge-danger';
            case 'TRANSFERENCIA': return 'badge-info';
            case 'AJUSTE': return 'badge-warning';
            default: return 'badge-secondary';
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
                <div className="text-center">
                    <div className="spinner-border text-primary" role="status">
                        <span className="sr-only">Cargando...</span>
                    </div>
                    <p className="mt-3 text-muted">Cargando movimientos...</p>
                </div>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="d-flex justify-content-between align-items-center">
                        <div>
                            <h1 className="h3 mb-0">
                                <Package className="mr-2" size={24} />
                                Movimientos de Inventario
                            </h1>
                            <p className="text-muted mb-0">
                                Gestión y seguimiento de movimientos de stock
                            </p>
                        </div>
                        <button
                            onClick={() => setShowForm(!showForm)}
                            className="btn btn-primary"
                        >
                            <Plus size={16} className="mr-2" />
                            Nuevo Movimiento
                        </button>
                    </div>
                </div>
            </div>

            {/* Stats */}
            <div className="row mb-4">
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Total Movimientos"
                        value={stats.total}
                        icon={Package}
                        color="info"
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Entradas"
                        value={stats.entradas}
                        icon={TrendingUp}
                        color="success"
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Salidas"
                        value={stats.salidas}
                        icon={TrendingUp}
                        color="danger"
                    />
                </div>
                <div className="col-lg-3 col-6">
                    <AdminLTEWidget
                        type="metric"
                        title="Transferencias"
                        value={stats.transferencias}
                        icon={TrendingUp}
                        color="warning"
                    />
                </div>
            </div>

            {/* Form */}
            {showForm && (
                <AdminLTEWidget
                    type="card"
                    title="Registrar Nuevo Movimiento"
                    color="primary"
                >
                    <form onSubmit={handleSubmit}>
                        <div className="row">
                            <div className="col-md-6">
                                <div className="form-group">
                                    <label>Tipo de Movimiento *</label>
                                    <select
                                        name="tipo_movimiento"
                                        value={formData.tipo_movimiento}
                                        onChange={handleFormChange}
                                        className="form-control"
                                        required
                                    >
                                        <option value="ENTRADA">Entrada</option>
                                        <option value="SALIDA">Salida</option>
                                        <option value="TRANSFERENCIA">Transferencia</option>
                                        <option value="AJUSTE">Ajuste</option>
                                    </select>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="form-group">
                                    <label>Tipo de Producto *</label>
                                    <select
                                        name="product_type"
                                        value={formData.product_type}
                                        onChange={(e) => {
                                            setFormData(prev => ({ 
                                                ...prev, 
                                                product_type: e.target.value, 
                                                product_id: '' 
                                            }));
                                        }}
                                        className="form-control"
                                    >
                                        <option value="chemical">Químico</option>
                                        <option value="pipe">Tubería</option>
                                        <option value="pump">Bomba/Motor</option>
                                        <option value="accessory">Accesorio</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="row">
                            <div className="col-12">
                                <div className="form-group">
                                    <label>
                                        Producto ({formData.product_type}) *
                                        {loadingProducts && <small className="text-info ml-2">Cargando...</small>}
                                    </label>
                                    <select
                                        name="product_id"
                                        value={formData.product_id}
                                        onChange={handleFormChange}
                                        className="form-control"
                                        disabled={loadingProducts}
                                        required
                                    >
                                        <option value="">-- Seleccionar Producto --</option>
                                        {productsList.map(p => (
                                            <option key={p.id} value={p.id}>
                                                {p.nombre} {p.sku ? `(${p.sku})` : ''} - {p.marca || ''}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="row">
                            <div className="col-md-6">
                                <div className="form-group">
                                    <label>Cantidad *</label>
                                    <input
                                        type="number"
                                        name="cantidad"
                                        value={formData.cantidad}
                                        onChange={handleFormChange}
                                        className="form-control"
                                        min="1"
                                        required
                                    />
                                </div>
                            </div>
                            <div className="col-md-6">
                                {(formData.tipo_movimiento === 'SALIDA' || 
                                  formData.tipo_movimiento === 'TRANSFERENCIA' || 
                                  formData.tipo_movimiento === 'AJUSTE') && (
                                    <div className="form-group">
                                        <label>Acueducto Origen *</label>
                                        <select
                                            name="acueducto_origen"
                                            value={formData.acueducto_origen}
                                            onChange={handleFormChange}
                                            className="form-control"
                                            required
                                        >
                                            <option value="">Seleccionar...</option>
                                            {acueductos.map(a => (
                                                <option key={a.id} value={a.id}>{a.nombre}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}
                                {(formData.tipo_movimiento === 'ENTRADA' || 
                                  formData.tipo_movimiento === 'TRANSFERENCIA') && (
                                    <div className="form-group">
                                        <label>Acueducto Destino *</label>
                                        <select
                                            name="acueducto_destino"
                                            value={formData.acueducto_destino}
                                            onChange={handleFormChange}
                                            className="form-control"
                                            required
                                        >
                                            <option value="">Seleccionar...</option>
                                            {acueductos.map(a => (
                                                <option key={a.id} value={a.id}>{a.nombre}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Razón / Comentarios</label>
                            <textarea
                                name="razon"
                                value={formData.razon}
                                onChange={handleFormChange}
                                className="form-control"
                                rows="3"
                            />
                        </div>

                        <div className="d-flex justify-content-end">
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className="btn btn-secondary mr-2"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="btn btn-primary"
                            >
                                Guardar Movimiento
                            </button>
                        </div>
                    </form>
                </AdminLTEWidget>
            )}

            {/* Movimientos Table */}
            <AdminLTEWidget
                type="table"
                title="Historial de Movimientos"
                icon={Calendar}
                onRefresh={fetchInitialData}
            >
                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Tipo</th>
                                <th>Producto</th>
                                <th>Cantidad</th>
                                <th>Origen</th>
                                <th>Destino</th>
                                <th>Fecha</th>
                                <th>Usuario</th>
                            </tr>
                        </thead>
                        <tbody>
                            {movimientos.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="text-center text-muted py-4">
                                        <AlertCircle size={24} className="mb-2" />
                                        <p>No hay movimientos registrados</p>
                                    </td>
                                </tr>
                            ) : (
                                movimientos.map(mov => (
                                    <tr key={mov.id}>
                                        <td>
                                            <span className={`badge ${getTipoBadgeClass(mov.tipo_movimiento)}`}>
                                                {mov.tipo_movimiento}
                                            </span>
                                        </td>
                                        <td className="font-weight-bold">
                                            {mov.producto_str || 'Producto desconocido'}
                                        </td>
                                        <td className="font-weight-bold">
                                            {mov.cantidad}
                                        </td>
                                        <td className="text-muted">
                                            {mov.acueducto_origen_nombre || '-'}
                                        </td>
                                        <td className="text-muted">
                                            {mov.acueducto_destino_nombre || '-'}
                                        </td>
                                        <td className="text-muted">
                                            {new Date(mov.fecha_movimiento).toLocaleDateString('es-ES')}
                                        </td>
                                        <td className="text-muted">
                                            {mov.usuario_nombre || '-'}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </AdminLTEWidget>
        </div>
    );
}