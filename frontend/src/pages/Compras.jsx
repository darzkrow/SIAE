import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { useAuth } from '../context/AuthContext';
import { ShoppingCart, Plus, Eye, FileText, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function Compras() {
  const { user } = useAuth();
  const { addNotification } = useNotifications();
  const [ordenes, setOrdenes] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    pendientes: 0,
    aprobadas: 0,
    rechazadas: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [oRes, iRes] = await Promise.all([
        InventoryService.compras.ordenes.getAll(),
        InventoryService.compras.items.getAll(),
      ]);
      
      const ordenesData = oRes.data.results || oRes.data;
      const itemsData = iRes.data.results || iRes.data;
      
      setOrdenes(ordenesData);
      setItems(itemsData);
      
      // Calcular estadísticas
      const stats = {
        total: ordenesData.length,
        pendientes: ordenesData.filter(o => o.estado === 'PENDIENTE').length,
        aprobadas: ordenesData.filter(o => o.estado === 'APROBADA').length,
        rechazadas: ordenesData.filter(o => o.estado === 'RECHAZADA').length
      };
      setStats(stats);
      
    } catch (e) {
      console.error(e);
      addNotification({
        type: 'error',
        title: 'Error de conexión',
        message: 'No se pudieron cargar las órdenes de compra',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const getEstadoBadgeClass = (estado) => {
    switch (estado) {
      case 'PENDIENTE': return 'badge-warning';
      case 'APROBADA': return 'badge-success';
      case 'RECHAZADA': return 'badge-danger';
      case 'COMPLETADA': return 'badge-info';
      default: return 'badge-secondary';
    }
  };

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case 'PENDIENTE': return <Clock size={16} />;
      case 'APROBADA': return <CheckCircle size={16} />;
      case 'RECHAZADA': return <XCircle size={16} />;
      case 'COMPLETADA': return <CheckCircle size={16} />;
      default: return <AlertCircle size={16} />;
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="sr-only">Cargando...</span>
          </div>
          <p className="mt-3 text-muted">Cargando órdenes de compra...</p>
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
                <ShoppingCart className="mr-2" size={24} />
                Órdenes de Compra
              </h1>
              <p className="text-muted mb-0">
                Gestión y seguimiento de órdenes de compra
              </p>
            </div>
            {user?.is_admin && (
              <button className="btn btn-primary">
                <Plus size={16} className="mr-2" />
                Nueva Orden
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="row mb-4">
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Total Órdenes"
            value={stats.total}
            icon={ShoppingCart}
            color="info"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Pendientes"
            value={stats.pendientes}
            icon={Clock}
            color="warning"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Aprobadas"
            value={stats.aprobadas}
            icon={CheckCircle}
            color="success"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Rechazadas"
            value={stats.rechazadas}
            icon={XCircle}
            color="danger"
          />
        </div>
      </div>

      {/* Órdenes de Compra */}
      <AdminLTEWidget
        type="table"
        title="Órdenes de Compra"
        icon={FileText}
        color="primary"
        onRefresh={loadData}
      >
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>Estado</th>
                <th>Solicitante</th>
                <th>Aprobador</th>
                <th>Fecha Creación</th>
                <th>Total Items</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {ordenes.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center text-muted py-4">
                    <ShoppingCart size={24} className="mb-2" />
                    <p>No hay órdenes de compra registradas</p>
                  </td>
                </tr>
              ) : (
                ordenes.map(orden => (
                  <tr key={orden.id}>
                    <td className="font-weight-bold">
                      #{orden.id}
                    </td>
                    <td>
                      <span className={`badge ${getEstadoBadgeClass(orden.estado)} d-flex align-items-center`} style={{ width: 'fit-content' }}>
                        {getEstadoIcon(orden.estado)}
                        <span className="ml-1">{orden.estado}</span>
                      </span>
                    </td>
                    <td className="text-muted">
                      {orden.solicitante_nombre || orden.solicitante || '-'}
                    </td>
                    <td className="text-muted">
                      {orden.aprobador_nombre || orden.aprobador || '-'}
                    </td>
                    <td className="text-muted">
                      {orden.creado_en ? new Date(orden.creado_en).toLocaleDateString('es-ES') : '-'}
                    </td>
                    <td className="font-weight-bold">
                      {items.filter(item => item.orden === orden.id || item.orden_id === orden.id).length}
                    </td>
                    <td>
                      <Link 
                        to={`/compras/orden/${orden.id}`} 
                        className="btn btn-sm btn-outline-primary"
                      >
                        <Eye size={14} className="mr-1" />
                        Ver Detalle
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </AdminLTEWidget>

      {/* Items de Órdenes */}
      <AdminLTEWidget
        type="table"
        title="Items de Órdenes Recientes"
        icon={FileText}
        color="secondary"
      >
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>Orden</th>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Tipo</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center text-muted py-4">
                    <FileText size={24} className="mb-2" />
                    <p>No hay items de órdenes registrados</p>
                  </td>
                </tr>
              ) : (
                items.slice(0, 10).map(item => (
                  <tr key={item.id}>
                    <td className="font-weight-bold">
                      #{item.id}
                    </td>
                    <td>
                      <Link 
                        to={`/compras/orden/${item.orden || item.orden_id}`}
                        className="text-primary"
                      >
                        #{item.orden || item.orden_id}
                      </Link>
                    </td>
                    <td className="font-weight-bold">
                      {item.producto_str || `${item.product_type_read || item.product_type}:${item.product_id_read || item.product_id}`}
                    </td>
                    <td className="font-weight-bold">
                      {item.cantidad}
                    </td>
                    <td>
                      <span className="badge badge-info">
                        {item.product_type_read || item.product_type || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {items.length > 10 && (
          <div className="card-footer">
            <small className="text-muted">
              Mostrando 10 de {items.length} items totales
            </small>
          </div>
        )}
      </AdminLTEWidget>
    </div>
  );
}
