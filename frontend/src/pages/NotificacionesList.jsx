import { useEffect, useState } from 'react';
import { InventoryService } from '../services/inventory.service';

export default function NotificacionesList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      const res = await InventoryService.notificaciones.getAll();
      setItems(res.data || []);
    } catch (e) {
      setError('No se pudo cargar las notificaciones');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const markAsRead = async (id) => {
    try {
      await InventoryService.notificaciones.markAsRead(id);
      await load();
    } catch (e) {
      // ignore
    }
  };

  if (loading) return <div className="text-gray-600">Cargando notificaciones...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-3">Notificaciones</h3>
      <ul className="divide-y">
        {items.map(n => (
          <li key={n.id} className="py-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{n.titulo || n.title || 'Notificación'}</p>
              <p className="text-xs text-gray-600">{n.mensaje || n.message || ''}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-1 rounded ${n.leida ? 'bg-gray-200 text-gray-700' : 'bg-blue-100 text-blue-700'}`}>
                {n.leida ? 'Leída' : 'Nueva'}
              </span>
              {!n.leida && (
                <button onClick={() => markAsRead(n.id)} className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Marcar leída</button>
              )}
            </div>
          </li>
        ))}
        {items.length === 0 && (
          <li className="py-3 text-gray-500">Sin notificaciones</li>
        )}
      </ul>
    </div>
  );
}
