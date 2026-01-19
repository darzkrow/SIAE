import { useEffect, useState } from 'react';
import { InventoryService } from '../services/inventory.service';

export default function Auditoria() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await InventoryService.auditoria.logs();
        const arr = Array.isArray(res.data) ? res.data : (res.data?.results || []);
        setLogs(arr);
      } catch (e) {
        if (e.response?.status === 403) {
          setError('No autorizado: requiere permisos de administrador');
        } else {
          setError('No se pudo cargar los logs de auditoría');
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="text-gray-600">Cargando auditoría...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-3">Logs</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2 px-3">ID</th>
              <th className="py-2 px-3">Acción</th>
              <th className="py-2 px-3">Usuario</th>
              <th className="py-2 px-3">Objeto</th>
              <th className="py-2 px-3">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id} className="border-b hover:bg-gray-50">
                <td className="py-2 px-3">{l.id}</td>
                <td className="py-2 px-3">{l.action || l.accion || '-'}</td>
                <td className="py-2 px-3">{l.user_name || l.usuario || '-'}</td>
                <td className="py-2 px-3">{l.content_type || l.objeto || '-'}#{l.object_id || ''}</td>
                <td className="py-2 px-3">{l.created_at || l.fecha || l.timestamp || '-'}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td className="py-3 px-3 text-gray-500" colSpan={5}>Sin registros</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
