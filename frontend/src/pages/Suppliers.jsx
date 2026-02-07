import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { Truck, Plus, Edit2, Trash2, Search, Phone, Mail, MapPin } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Suppliers() {
    const { user } = useAuth();
    const { addNotification } = useNotifications();
    const [suppliers, setSuppliers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingSupplier, setEditingSupplier] = useState(null);
    const [formData, setFormData] = useState({
        nombre_empresa: '',
        contacto_nombre: '',
        contacto_email: '',
        contacto_telefono: '',
        direccion: '',
        rif: ''
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await InventoryService.suppliers.getAll();
            setSuppliers(res.data.results || res.data);
        } catch (e) {
            addNotification({ type: 'error', message: 'Error cargando proveedores' });
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingSupplier) {
                await InventoryService.suppliers.update(editingSupplier.id, formData);
                addNotification({ type: 'success', message: 'Proveedor actualizado' });
            } else {
                await InventoryService.suppliers.create(formData);
                addNotification({ type: 'success', message: 'Proveedor creado' });
            }
            setShowForm(false);
            setEditingSupplier(null);
            setFormData({ nombre_empresa: '', contacto_nombre: '', contacto_email: '', contacto_telefono: '', direccion: '', rif: '' });
            loadData();
        } catch (e) {
            addNotification({ type: 'error', message: 'Error guardando proveedor' });
        }
    };

    const handleEdit = (supplier) => {
        setEditingSupplier(supplier);
        setFormData({
            nombre_empresa: supplier.nombre_empresa || '',
            contacto_nombre: supplier.contacto_nombre || '',
            contacto_email: supplier.contacto_email || '',
            contacto_telefono: supplier.contacto_telefono || '',
            direccion: supplier.direccion || '',
            rif: supplier.rif || ''
        });
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        const result = await Swal.fire({
            title: '¿Eliminar proveedor?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true
        });

        if (result.isConfirmed) {
            try {
                await InventoryService.suppliers.delete(id);
                loadData();
                addNotification({ type: 'success', message: 'Proveedor eliminado' });
            } catch (e) {
                addNotification({ type: 'error', message: 'Error eliminando proveedor' });
            }
        }
    };

    return (
        <div>
            <div className="row mb-4">
                <div className="col-12 d-flex justify-content-between align-items-center">
                    <div>
                        <h1 className="h3 mb-0">Proveedores</h1>
                        <p className="text-muted">Gestión de proveedores y contactos</p>
                    </div>
                    <button className="btn btn-primary" onClick={() => { setEditingSupplier(null); setShowForm(true); }}>
                        <Plus size={18} className="mr-2" /> Nuevo Proveedor
                    </button>
                </div>
            </div>

            {showForm && (
                <div className="card card-primary mb-4">
                    <div className="card-header">
                        <h3 className="card-title">{editingSupplier ? 'Editar' : 'Nuevo'} Proveedor</h3>
                    </div>
                    <form onSubmit={handleSubmit}>
                        <div className="card-body">
                            <div className="row">
                                <div className="col-md-6 form-group">
                                    <label>Nombre Empresa *</label>
                                    <input type="text" className="form-control" required
                                        value={formData.nombre_empresa}
                                        onChange={e => setFormData({ ...formData, nombre_empresa: e.target.value })}
                                    />
                                </div>
                                <div className="col-md-6 form-group">
                                    <label>RIF</label>
                                    <input type="text" className="form-control"
                                        value={formData.rif}
                                        onChange={e => setFormData({ ...formData, rif: e.target.value })}
                                    />
                                </div>
                                <div className="col-md-4 form-group">
                                    <label>Contacto</label>
                                    <input type="text" className="form-control"
                                        value={formData.contacto_nombre}
                                        onChange={e => setFormData({ ...formData, contacto_nombre: e.target.value })}
                                    />
                                </div>
                                <div className="col-md-4 form-group">
                                    <label>Email</label>
                                    <input type="email" className="form-control"
                                        value={formData.contacto_email}
                                        onChange={e => setFormData({ ...formData, contacto_email: e.target.value })}
                                    />
                                </div>
                                <div className="col-md-4 form-group">
                                    <label>Teléfono</label>
                                    <input type="text" className="form-control"
                                        value={formData.contacto_telefono}
                                        onChange={e => setFormData({ ...formData, contacto_telefono: e.target.value })}
                                    />
                                </div>
                                <div className="col-12 form-group">
                                    <label>Dirección</label>
                                    <textarea className="form-control" rows="2"
                                        value={formData.direccion}
                                        onChange={e => setFormData({ ...formData, direccion: e.target.value })}
                                    ></textarea>
                                </div>
                            </div>
                        </div>
                        <div className="card-footer text-right">
                            <button type="button" className="btn btn-secondary mr-2" onClick={() => setShowForm(false)}>Cancelar</button>
                            <button type="submit" className="btn btn-primary">Guardar</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="row">
                {suppliers.map(supplier => (
                    <div key={supplier.id} className="col-md-4">
                        <div className="card card-widget widget-user-2 shadow-sm">
                            <div className="widget-user-header bg-info">
                                <div className="widget-user-image">
                                    <div className="img-circle elevation-2 bg-white d-flex align-items-center justify-content-center" style={{ width: 65, height: 65 }}>
                                        <Truck size={30} className="text-info" />
                                    </div>
                                </div>
                                <h3 className="widget-user-username ml-3">{supplier.nombre_empresa}</h3>
                                <h5 className="widget-user-desc ml-3">{supplier.rif}</h5>
                            </div>
                            <div className="card-footer p-0">
                                <ul className="nav flex-column">
                                    <li className="nav-item">
                                        <span className="nav-link text-muted">
                                            <Phone size={14} className="mr-2" /> {supplier.contacto_telefono || 'N/A'}
                                        </span>
                                    </li>
                                    <li className="nav-item">
                                        <span className="nav-link text-muted">
                                            <Mail size={14} className="mr-2" /> {supplier.contacto_email || 'N/A'}
                                        </span>
                                    </li>
                                    <li className="nav-item">
                                        <span className="nav-link text-muted">
                                            <MapPin size={14} className="mr-2" /> {supplier.direccion || 'N/A'}
                                        </span>
                                    </li>
                                    <li className="nav-item p-2 text-right">
                                        <button className="btn btn-sm btn-outline-primary mr-1" onClick={() => handleEdit(supplier)}>Editar</button>
                                        <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(supplier.id)}>Eliminar</button>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            {suppliers.length === 0 && !loading && (
                <div className="text-center text-muted p-5">No hay proveedores registrados.</div>
            )}
        </div>
    );
}
