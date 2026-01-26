import React, { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { AdminLTEWidget } from '../components/adminlte';
import { CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';

const EndpointTest = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(false);

  const endpoints = [
    { name: 'Dashboard Stats', service: () => InventoryService.reports.dashboardStats() },
    { name: 'User Profile', service: () => InventoryService.accounts?.me?.() || Promise.resolve({ data: 'Not implemented' }) },
    { name: 'Movimientos', service: () => InventoryService.movimientos.getAll() },
    { name: 'Categorías', service: () => InventoryService.categories.getAll() },
    { name: 'Marcas', service: () => InventoryService.marcas.getAll() },
    { name: 'Alertas', service: () => InventoryService.alertas.getAll() },
    { name: 'Notificaciones', service: () => InventoryService.notificaciones.getAll() },
    { name: 'Geography States', service: () => InventoryService.geography.states() },
    { name: 'Geography Municipalities', service: () => InventoryService.geography.municipalities() },
    { name: 'Sucursales', service: () => InventoryService.sucursales.getAll() },
    { name: 'Chemicals', service: () => InventoryService.chemicals.getAll() },
    { name: 'Pipes', service: () => InventoryService.pipes.getAll() },
    { name: 'Pumps', service: () => InventoryService.pumps.getAll() },
    { name: 'Accessories', service: () => InventoryService.accessories.getAll() },
    { name: 'Compras Ordenes', service: () => InventoryService.compras.ordenes.getAll() },
    { name: 'Auditoria Logs', service: () => InventoryService.auditoria.logs() },
  ];

  const runTests = async () => {
    setLoading(true);
    const results = [];

    for (const endpoint of endpoints) {
      const testResult = {
        name: endpoint.name,
        status: 'running',
        response: null,
        error: null,
        duration: 0
      };

      const startTime = Date.now();
      
      try {
        const response = await endpoint.service();
        testResult.status = 'success';
        testResult.response = response.data;
        testResult.duration = Date.now() - startTime;
      } catch (error) {
        testResult.status = 'error';
        testResult.error = error.response?.data || error.message;
        testResult.duration = Date.now() - startTime;
      }

      results.push(testResult);
      setTests([...results]);
    }

    setLoading(false);
  };

  useEffect(() => {
    runTests();
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="text-success" size={20} />;
      case 'error':
        return <XCircle className="text-danger" size={20} />;
      case 'running':
        return <Clock className="text-warning" size={20} />;
      default:
        return <Clock className="text-muted" size={20} />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'success':
        return 'badge-success';
      case 'error':
        return 'badge-danger';
      case 'running':
        return 'badge-warning';
      default:
        return 'badge-secondary';
    }
  };

  const successCount = tests.filter(t => t.status === 'success').length;
  const errorCount = tests.filter(t => t.status === 'error').length;
  const runningCount = tests.filter(t => t.status === 'running').length;

  return (
    <div>
      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Total Endpoints"
            value={endpoints.length}
            icon={RefreshCw}
            color="info"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Exitosos"
            value={successCount}
            icon={CheckCircle}
            color="success"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="Con Errores"
            value={errorCount}
            icon={XCircle}
            color="danger"
          />
        </div>
        <div className="col-lg-3 col-6">
          <AdminLTEWidget
            type="metric"
            title="En Progreso"
            value={runningCount}
            icon={Clock}
            color="warning"
          />
        </div>
      </div>

      {/* Test Results */}
      <AdminLTEWidget
        type="card"
        title="Resultados de Pruebas de Endpoints"
        color="primary"
      >
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 className="mb-0">Estado de los Endpoints</h5>
          <button 
            className="btn btn-primary btn-sm"
            onClick={runTests}
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner-border spinner-border-sm mr-2" role="status">
                  <span className="sr-only">Cargando...</span>
                </div>
                Probando...
              </>
            ) : (
              <>
                <RefreshCw size={16} className="mr-2" />
                Probar Nuevamente
              </>
            )}
          </button>
        </div>

        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Estado</th>
                <th>Duración (ms)</th>
                <th>Respuesta</th>
              </tr>
            </thead>
            <tbody>
              {tests.map((test, index) => (
                <tr key={index}>
                  <td className="font-weight-bold">{test.name}</td>
                  <td>
                    <div className="d-flex align-items-center">
                      {getStatusIcon(test.status)}
                      <span className={`badge ${getStatusBadge(test.status)} ml-2`}>
                        {test.status.toUpperCase()}
                      </span>
                    </div>
                  </td>
                  <td>
                    {test.duration > 0 && (
                      <span className={`badge ${test.duration > 1000 ? 'badge-warning' : 'badge-info'}`}>
                        {test.duration}ms
                      </span>
                    )}
                  </td>
                  <td>
                    {test.status === 'success' && (
                      <details>
                        <summary className="btn btn-sm btn-outline-info">Ver Respuesta</summary>
                        <pre className="mt-2 p-2 bg-light border rounded" style={{ fontSize: '12px', maxHeight: '200px', overflow: 'auto' }}>
                          {JSON.stringify(test.response, null, 2)}
                        </pre>
                      </details>
                    )}
                    {test.status === 'error' && (
                      <details>
                        <summary className="btn btn-sm btn-outline-danger">Ver Error</summary>
                        <pre className="mt-2 p-2 bg-light border rounded text-danger" style={{ fontSize: '12px', maxHeight: '200px', overflow: 'auto' }}>
                          {JSON.stringify(test.error, null, 2)}
                        </pre>
                      </details>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {tests.length === 0 && !loading && (
          <div className="text-center py-4">
            <p className="text-muted">No se han ejecutado pruebas aún.</p>
            <button className="btn btn-primary" onClick={runTests}>
              Ejecutar Pruebas
            </button>
          </div>
        )}
      </AdminLTEWidget>
    </div>
  );
};

export default EndpointTest;