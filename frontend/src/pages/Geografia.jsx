import { useEffect, useState } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { MapPin, Building, Globe, Navigation } from 'lucide-react';

export default function Geografia() {
  const { addNotification } = useNotifications();
  const [states, setStates] = useState([]);
  const [municipalities, setMunicipalities] = useState([]);
  const [parishes, setParishes] = useState([]);
  const [ubicaciones, setUbicaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [sRes, mRes, pRes, uRes] = await Promise.all([
          InventoryService.geography.states(),
          InventoryService.geography.municipalities(),
          InventoryService.geography.parishes(),
          InventoryService.geography.ubicaciones(),
        ]);
        const toArr = (d) => Array.isArray(d) ? d : (d?.results || []);
        setStates(toArr(sRes.data));
        setMunicipalities(toArr(mRes.data));
        setParishes(toArr(pRes.data));
        setUbicaciones(toArr(uRes.data));
      } catch (e) {
        console.error('Error loading geography data:', e);
        setError('No se pudo cargar la información geográfica');
        addNotification({
          type: 'error',
          title: 'Error de conexión',
          message: 'No se pudo cargar la información geográfica',
          duration: 5000
        });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [addNotification]);

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="sr-only">Cargando...</span>
          </div>
          <p className="mt-3 text-muted">Cargando información geográfica...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        <h4 className="alert-heading">Error</h4>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="h3 mb-0">
            <Globe className="mr-2" size={24} />
            Información Geográfica
          </h1>
          <p className="text-muted mb-0">
            Estados, municipios, parroquias y ubicaciones del sistema
          </p>
        </div>
      </div>

      {/* Statistics Row */}
      <div className="row mb-4">
        <div className="col-lg-3 col-6">
          <AdminLTEWidget 
            type="metric" 
            title="Estados" 
            value={states.length}
            icon={Globe}
            color="info"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget 
            type="metric" 
            title="Municipios" 
            value={municipalities.length}
            icon={Building}
            color="success"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget 
            type="metric" 
            title="Parroquias" 
            value={parishes.length}
            icon={Navigation}
            color="warning"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget 
            type="metric" 
            title="Ubicaciones" 
            value={ubicaciones.length}
            icon={MapPin}
            color="danger"
          />
        </div>
      </div>

      <div className="row">
        {/* Estados */}
        <div className="col-lg-6 col-md-12 mb-4">
          <AdminLTEWidget type="card" title="Estados" icon={Globe} color="info">
            <div className="table-responsive" style={{ maxHeight: '300px' }}>
              <table className="table table-sm table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                  </tr>
                </thead>
                <tbody>
                  {states.length === 0 ? (
                    <tr>
                      <td colSpan="2" className="text-center text-muted py-3">
                        <Globe size={24} className="mb-2" />
                        <p>No hay estados registrados</p>
                      </td>
                    </tr>
                  ) : (
                    states.map(s => (
                      <tr key={s.id}>
                        <td><span className="badge badge-light">{s.id}</span></td>
                        <td className="font-weight-bold">{s.nombre || s.name}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </AdminLTEWidget>
        </div>

        {/* Municipios */}
        <div className="col-lg-6 col-md-12 mb-4">
          <AdminLTEWidget type="card" title="Municipios" icon={Building} color="success">
            <div className="table-responsive" style={{ maxHeight: '300px' }}>
              <table className="table table-sm table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                  </tr>
                </thead>
                <tbody>
                  {municipalities.length === 0 ? (
                    <tr>
                      <td colSpan="2" className="text-center text-muted py-3">
                        <Building size={24} className="mb-2" />
                        <p>No hay municipios registrados</p>
                      </td>
                    </tr>
                  ) : (
                    municipalities.map(m => (
                      <tr key={m.id}>
                        <td><span className="badge badge-light">{m.id}</span></td>
                        <td className="font-weight-bold">{m.nombre || m.name}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </AdminLTEWidget>
        </div>

        {/* Parroquias */}
        <div className="col-lg-6 col-md-12 mb-4">
          <AdminLTEWidget type="card" title="Parroquias" icon={Navigation} color="warning">
            <div className="table-responsive" style={{ maxHeight: '300px' }}>
              <table className="table table-sm table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                  </tr>
                </thead>
                <tbody>
                  {parishes.length === 0 ? (
                    <tr>
                      <td colSpan="2" className="text-center text-muted py-3">
                        <Navigation size={24} className="mb-2" />
                        <p>No hay parroquias registradas</p>
                      </td>
                    </tr>
                  ) : (
                    parishes.map(p => (
                      <tr key={p.id}>
                        <td><span className="badge badge-light">{p.id}</span></td>
                        <td className="font-weight-bold">{p.nombre || p.name}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </AdminLTEWidget>
        </div>

        {/* Ubicaciones */}
        <div className="col-lg-6 col-md-12 mb-4">
          <AdminLTEWidget type="card" title="Ubicaciones" icon={MapPin} color="danger">
            <div className="table-responsive" style={{ maxHeight: '300px' }}>
              <table className="table table-sm table-striped">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Dirección</th>
                    <th>Acueducto</th>
                  </tr>
                </thead>
                <tbody>
                  {ubicaciones.length === 0 ? (
                    <tr>
                      <td colSpan="3" className="text-center text-muted py-3">
                        <MapPin size={24} className="mb-2" />
                        <p>No hay ubicaciones registradas</p>
                      </td>
                    </tr>
                  ) : (
                    ubicaciones.map(u => (
                      <tr key={u.id}>
                        <td className="font-weight-bold">{u.nombre || u.name}</td>
                        <td className="text-muted">{u.direccion || u.address || '-'}</td>
                        <td>
                          <span className="badge badge-info">
                            {u.acueducto_nombre || u.acueducto || '-'}
                          </span>
                        </td>
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
