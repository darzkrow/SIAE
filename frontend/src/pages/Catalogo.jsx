import { useEffect, useState } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { BookOpen, Tag, Package, Plus, Edit2, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Catalogo() {
  const { user } = useAuth();
  const { addNotification } = useNotifications();
  const [categorias, setCategorias] = useState([]);
  const [marcas, setMarcas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCategoriaForm, setShowCategoriaForm] = useState(false);
  const [showMarcaForm, setShowMarcaForm] = useState(false);
  const [editingCategoria, setEditingCategoria] = useState(null);
  const [editingMarca, setEditingMarca] = useState(null);
  
  // Form data
  const [categoriaForm, setCategoriaForm] = useState({ nombre: '', descripcion: '' });
  const [marcaForm, setMarcaForm] = useState({ nombre: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [catRes, marRes] = await Promise.all([
        InventoryService.categories.getAll(),
        InventoryService.marcas.getAll(),
      ]);
      setCategorias(Array.isArray(catRes.data) ? catRes.data : (catRes.data?.results || []));
      setMarcas(Array.isArray(marRes.data) ? marRes.data : (marRes.data?.results || []));
    } catch (e) {
      console.error(e);
      addNotification({
        type: 'error',
        title: 'Error de conexión',
        message: 'No se pudo cargar el catálogo',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCategoriaSubmit = async (e) => {
    e.preventDefault();
    try {
      // Trim whitespace from form data
      const cleanedData = {
        nombre: categoriaForm.nombre.trim(),
        descripcion: categoriaForm.descripcion.trim()
      };
      
      if (editingCategoria) {
        await InventoryService.categories.update(editingCategoria.id, cleanedData);
        addNotification({
          type: 'success',
          title: 'Categoría actualizada',
          message: 'La categoría se actualizó correctamente',
          duration: 3000
        });
      } else {
        await InventoryService.categories.create(cleanedData);
        addNotification({
          type: 'success',
          title: 'Categoría creada',
          message: 'La categoría se creó correctamente',
          duration: 3000
        });
      }
      setCategoriaForm({ nombre: '', descripcion: '' });
      setEditingCategoria(null);
      setShowCategoriaForm(false);
      loadData();
    } catch (err) {
      console.error(err);
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'No se pudo guardar la categoría',
        duration: 5000
      });
    }
  };

  const handleMarcaSubmit = async (e) => {
    e.preventDefault();
    try {
      // Trim whitespace from form data
      const cleanedData = {
        nombre: marcaForm.nombre.trim()
      };
      
      if (editingMarca) {
        await InventoryService.marcas.update(editingMarca.id, cleanedData);
        addNotification({
          type: 'success',
          title: 'Marca actualizada',
          message: 'La marca se actualizó correctamente',
          duration: 3000
        });
      } else {
        await InventoryService.marcas.create(cleanedData);
        addNotification({
          type: 'success',
          title: 'Marca creada',
          message: 'La marca se creó correctamente',
          duration: 3000
        });
      }
      setMarcaForm({ nombre: '' });
      setEditingMarca(null);
      setShowMarcaForm(false);
      loadData();
    } catch (err) {
      console.error(err);
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'No se pudo guardar la marca',
        duration: 5000
      });
    }
  };

  const handleDeleteCategoria = async (categoria) => {
    const result = await Swal.fire({
      title: '¿Eliminar categoría?',
      text: `¿Está seguro de eliminar la categoría "${categoria.nombre || categoria.name}"?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        await InventoryService.categories.delete(categoria.id);
        addNotification({
          type: 'success',
          title: 'Categoría eliminada',
          message: 'La categoría se eliminó correctamente',
          duration: 3000
        });
        loadData();
      } catch (err) {
        console.error(err);
        addNotification({
          type: 'error',
          title: 'Error',
          message: 'No se pudo eliminar la categoría',
          duration: 5000
        });
      }
    }
  };

  const handleDeleteMarca = async (marca) => {
    const result = await Swal.fire({
      title: '¿Eliminar marca?',
      text: `¿Está seguro de eliminar la marca "${marca.nombre || marca.name}"?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        await InventoryService.marcas.delete(marca.id);
        addNotification({
          type: 'success',
          title: 'Marca eliminada',
          message: 'La marca se eliminó correctamente',
          duration: 3000
        });
        loadData();
      } catch (err) {
        console.error(err);
        addNotification({
          type: 'error',
          title: 'Error',
          message: 'No se pudo eliminar la marca',
          duration: 5000
        });
      }
    }
  };

  const startEditCategoria = (categoria) => {
    setEditingCategoria(categoria);
    setCategoriaForm({
      nombre: (categoria.nombre || categoria.name || '').trim(),
      descripcion: (categoria.descripcion || categoria.description || '').trim()
    });
    setShowCategoriaForm(true);
  };

  const startEditMarca = (marca) => {
    setEditingMarca(marca);
    setMarcaForm({
      nombre: (marca.nombre || marca.name || '').trim()
    });
    setShowMarcaForm(true);
  };

  const resetCategoriaForm = () => {
    setCategoriaForm({ nombre: '', descripcion: '' });
    setEditingCategoria(null);
    setShowCategoriaForm(false);
  };

  const resetMarcaForm = () => {
    setMarcaForm({ nombre: '' });
    setEditingMarca(null);
    setShowMarcaForm(false);
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="sr-only">Cargando...</span>
          </div>
          <p className="mt-3 text-muted">Cargando catálogo...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="h3 mb-0">
            <BookOpen className="mr-2" size={24} />
            Catálogo de Productos
          </h1>
          <p className="text-muted mb-0">
            Gestión de categorías y marcas del sistema
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="row mb-4">
        <div className="col-lg-6 col-12">
          <AdminLTEWidget
            type="metric"
            title="Total Categorías"
            value={categorias.length}
            icon={Package}
            color="primary"
          />
        </div>
        <div className="col-lg-6 col-12">
          <AdminLTEWidget
            type="metric"
            title="Total Marcas"
            value={marcas.length}
            icon={Tag}
            color="info"
          />
        </div>
      </div>

      <div className="row">
        {/* Categorías */}
        <div className="col-lg-6">
          <AdminLTEWidget
            type="card"
            title="Categorías"
            icon={Package}
            color="primary"
          >
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="mb-0">Lista de Categorías</h5>
              {user?.is_admin && (
                <button
                  onClick={() => setShowCategoriaForm(true)}
                  className="btn btn-primary btn-sm"
                >
                  <Plus size={14} className="mr-1" />
                  Nueva Categoría
                </button>
              )}
            </div>

            {showCategoriaForm && (
              <div className="card mb-3">
                <div className="card-body">
                  <h6>{editingCategoria ? 'Editar' : 'Nueva'} Categoría</h6>
                  <form onSubmit={handleCategoriaSubmit}>
                    <div className="form-group">
                      <label>Nombre *</label>
                      <input
                        type="text"
                        className="form-control"
                        value={categoriaForm.nombre}
                        onChange={(e) => setCategoriaForm(prev => ({ ...prev, nombre: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Descripción</label>
                      <textarea
                        className="form-control"
                        rows="2"
                        value={categoriaForm.descripcion}
                        onChange={(e) => setCategoriaForm(prev => ({ ...prev, descripcion: e.target.value }))}
                      />
                    </div>
                    <div className="d-flex justify-content-end">
                      <button
                        type="button"
                        onClick={resetCategoriaForm}
                        className="btn btn-secondary btn-sm mr-2"
                      >
                        Cancelar
                      </button>
                      <button type="submit" className="btn btn-primary btn-sm">
                        {editingCategoria ? 'Actualizar' : 'Crear'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    {user?.is_admin && <th>Acciones</th>}
                  </tr>
                </thead>
                <tbody>
                  {categorias.length === 0 ? (
                    <tr>
                      <td colSpan={user?.is_admin ? "3" : "2"} className="text-center text-muted py-3">
                        <Package size={24} className="mb-2" />
                        <p>No hay categorías registradas</p>
                      </td>
                    </tr>
                  ) : (
                    categorias.map((categoria) => (
                      <tr key={categoria.id}>
                        <td className="font-weight-bold">
                          {(categoria.nombre || categoria.name || '').trim() || '-'}
                        </td>
                        <td className="text-muted">
                          {(categoria.descripcion || categoria.description || '').trim() || '-'}
                        </td>
                        {user?.is_admin && (
                          <td>
                            <button
                              onClick={() => startEditCategoria(categoria)}
                              className="btn btn-sm btn-outline-primary mr-1"
                            >
                              <Edit2 size={12} />
                            </button>
                            <button
                              onClick={() => handleDeleteCategoria(categoria)}
                              className="btn btn-sm btn-outline-danger"
                            >
                              <Trash2 size={12} />
                            </button>
                          </td>
                        )}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </AdminLTEWidget>
        </div>

        {/* Marcas */}
        <div className="col-lg-6">
          <AdminLTEWidget
            type="card"
            title="Marcas"
            icon={Tag}
            color="info"
          >
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="mb-0">Lista de Marcas</h5>
              {user?.is_admin && (
                <button
                  onClick={() => setShowMarcaForm(true)}
                  className="btn btn-info btn-sm"
                >
                  <Plus size={14} className="mr-1" />
                  Nueva Marca
                </button>
              )}
            </div>

            {showMarcaForm && (
              <div className="card mb-3">
                <div className="card-body">
                  <h6>{editingMarca ? 'Editar' : 'Nueva'} Marca</h6>
                  <form onSubmit={handleMarcaSubmit}>
                    <div className="form-group">
                      <label>Nombre *</label>
                      <input
                        type="text"
                        className="form-control"
                        value={marcaForm.nombre}
                        onChange={(e) => setMarcaForm(prev => ({ ...prev, nombre: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="d-flex justify-content-end">
                      <button
                        type="button"
                        onClick={resetMarcaForm}
                        className="btn btn-secondary btn-sm mr-2"
                      >
                        Cancelar
                      </button>
                      <button type="submit" className="btn btn-info btn-sm">
                        {editingMarca ? 'Actualizar' : 'Crear'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    {user?.is_admin && <th>Acciones</th>}
                  </tr>
                </thead>
                <tbody>
                  {marcas.length === 0 ? (
                    <tr>
                      <td colSpan={user?.is_admin ? "2" : "1"} className="text-center text-muted py-3">
                        <Tag size={24} className="mb-2" />
                        <p>No hay marcas registradas</p>
                      </td>
                    </tr>
                  ) : (
                    marcas.map((marca) => (
                      <tr key={marca.id}>
                        <td className="font-weight-bold">
                          {(marca.nombre || marca.name || '').trim() || '-'}
                        </td>
                        {user?.is_admin && (
                          <td>
                            <button
                              onClick={() => startEditMarca(marca)}
                              className="btn btn-sm btn-outline-info mr-1"
                            >
                              <Edit2 size={12} />
                            </button>
                            <button
                              onClick={() => handleDeleteMarca(marca)}
                              className="btn btn-sm btn-outline-danger"
                            >
                              <Trash2 size={12} />
                            </button>
                          </td>
                        )}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </AdminLTEWidget>
        </div>
      </div>
    </div>
  );
}
