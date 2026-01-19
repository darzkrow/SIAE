import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';
import { useAuth } from '../context/AuthContext';

export default function Compras() {
  const { user } = useAuth();
  const [ordenes, setOrdenes] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [oRes, iRes] = await Promise.all([
          InventoryService.compras.ordenes.getAll(),
          InventoryService.compras.items.getAll(),
        ]);
        setOrdenes(oRes.data.results || oRes.data);
        setItems(iRes.data.results || iRes.data);
      } catch (e) {
        console.error(e);
        setError('Error al cargar compras');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-8">
      {error && <div className="p-4 bg-red-50 border-l-4 border-red-600 text-red-700 rounded">{error}</div>}

      <section>
        <h2 className="text-xl font-semibold mb-4">Órdenes de Compra</h2>
        {loading ? (
          <p className="text-gray-500">Cargando...</p>
        ) : (
          <div className="overflow-x-auto bg-white rounded shadow">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Solicitante</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Aprobador</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Creado</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {(ordenes || []).map(o => (
                  <tr key={o.id} className="border-t">
                    <td className="px-4 py-2">{o.id}</td>
                    <td className="px-4 py-2"><span className="px-2 py-1 text-xs rounded bg-blue-50 text-blue-700">{o.estado}</span></td>
                    <td className="px-4 py-2">{o.solicitante_nombre || o.solicitante}</td>
                    <td className="px-4 py-2">{o.aprobador_nombre || o.aprobador}</td>
                    <td className="px-4 py-2">{o.creado_en}</td>
                    <td className="px-4 py-2">
                      <Link to={`/compras/orden/${o.id}`} className="text-blue-600 hover:underline">Ver detalle</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-4">Items de Órdenes</h2>
        {loading ? (
          <p className="text-gray-500">Cargando...</p>
        ) : (
          <div className="overflow-x-auto bg-white rounded shadow">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Orden</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cantidad</th>
                </tr>
              </thead>
              <tbody>
                {(items || []).map(it => (
                  <tr key={it.id} className="border-t">
                    <td className="px-4 py-2">{it.id}</td>
                    <td className="px-4 py-2">{it.orden || it.orden_id}</td>
                    <td className="px-4 py-2">{it.producto_str || `${it.product_type_read}:${it.product_id_read}`}</td>
                    <td className="px-4 py-2">{it.cantidad}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
