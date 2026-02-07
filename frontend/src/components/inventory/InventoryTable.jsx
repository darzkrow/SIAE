import React from 'react';
import { Package, Search, Edit2, Trash2, Activity } from 'lucide-react';

const InventoryTable = ({
    items,
    loading,
    searchTerm,
    onSearchChange,
    onRefresh,
    onEdit,
    onDelete,
    isAdmin
}) => {
    return (
        <div className="card-body">
            {/* Search */}
            <div className="row mb-3">
                <div className="col-md-6">
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Buscar por nombre, SKU o descripción..."
                            value={searchTerm}
                            onChange={(e) => onSearchChange(e.target.value)}
                            className="form-control"
                        />
                        <div className="input-group-append">
                            <span className="input-group-text">
                                <Search size={16} />
                            </span>
                        </div>
                    </div>
                </div>
                <div className="col-md-6 text-right">
                    <span className="text-muted mr-3">
                        {items.length} registros encontrados
                    </span>
                    <button onClick={onRefresh} className="btn btn-tool" title="Refrescar">
                        <Activity size={16} />
                    </button>
                </div>
            </div>

            <div className="table-responsive">
                <table className="table table-hover table-striped">
                    <thead>
                        <tr>
                            <th>SKU / Código</th>
                            <th>Nombre</th>
                            <th>Categoría</th>
                            <th>Stock Actual</th>
                            <th>Precio Est.</th>
                            {isAdmin && <th>Acciones</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={isAdmin ? "6" : "5"} className="text-center py-4">
                                    <div className="spinner-border text-primary" role="status">
                                        <span className="sr-only">Cargando...</span>
                                    </div>
                                </td>
                            </tr>
                        ) : items.length === 0 ? (
                            <tr>
                                <td colSpan={isAdmin ? "6" : "5"} className="text-center py-4 text-muted">
                                    <Package size={24} className="mb-2" />
                                    <p>No hay artículos en esta categoría que coincidan con la búsqueda.</p>
                                </td>
                            </tr>
                        ) : (
                            items.map(item => (
                                <tr key={item.id}>
                                    <td className="text-muted">
                                        <code>{item.sku || item.codigo || 'N/A'}</code>
                                    </td>
                                    <td>
                                        <div className="font-weight-bold">{item.nombre}</div>
                                        <small className="text-muted">
                                            {item.descripcion?.substring(0, 50)}
                                            {item.descripcion?.length > 50 ? '...' : ''}
                                        </small>
                                    </td>
                                    <td>
                                        <span className="badge badge-info">
                                            {item.categoria_nombre || item.categoria?.nombre || 'General'}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`badge ${(item.stock_actual || 0) > 10 ? 'badge-success' : (item.stock_actual || 0) > 0 ? 'badge-warning' : 'badge-danger'}`}>
                                            {item.stock_actual || 0} {item.unidad_medida_nombre || item.unidad_medida?.simbolo || ''}
                                        </span>
                                    </td>
                                    <td>
                                        ${item.precio_unitario || '0.00'}
                                    </td>
                                    {isAdmin && (
                                        <td>
                                            <div className="btn-group">
                                                <button
                                                    onClick={() => onEdit(item)}
                                                    className="btn btn-sm btn-default"
                                                    title="Editar"
                                                >
                                                    <Edit2 size={14} className="text-primary" />
                                                </button>
                                                <button
                                                    onClick={() => onDelete(item.id)}
                                                    className="btn btn-sm btn-default"
                                                    title="Eliminar"
                                                >
                                                    <Trash2 size={14} className="text-danger" />
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
        </div>
    );
};

export default InventoryTable;
