import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { InventoryService } from '../services/inventory.service';

export default function OrdenDetalle() {
  const { id } = useParams();
  const [orden, setOrden] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const oRes = await InventoryService.compras.ordenes.getById(id);
        setOrden(oRes.data);
        const iRes = await InventoryService.compras.items.getAll();
        const its = (iRes.data.results || iRes.data).filter(it => String(it.orden) === String(id));
        setItems(its);
      } catch (e) {
        console.error(e);
        setError('Error al cargar el detalle de la orden');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  if (loading) return <p className="text-gray-500">Cargando...</p>;
  if (error) return <div className="p-4 bg-red-50 border-l-4 border-red-600 text-red-700 rounded">{error}</div>;
  if (!orden) return <p>No encontrado</p>;

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded p-6">
        <h2 className="text-2xl font-bold mb-2">Orden #{orden.id}</h2>
        <p className="text-gray-600">Estado: <span className="px-2 py-1 text-xs rounded bg-blue-50 text-blue-700">{orden.estado}</span></p>
        <p className="text-gray-600">Solicitante: {orden.solicitante_nombre || orden.solicitante}</p>
        <p className="text-gray-600">Aprobador: {orden.aprobador_nombre || orden.aprobador || '—'}</p>
        <p className="text-gray-600">Creado: {orden.creado_en}</p>
      </div>
      <div className="bg-white shadow rounded p-6">
        <h3 className="text-xl font-semibold mb-4">Items</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cantidad</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Precio</th>
              </tr>
            </thead>
            <tbody>
              {items.map(it => (
                <tr key={it.id} className="border-t">
                  <td className="px-4 py-2">{it.id}</td>
                  <td className="px-4 py-2">{it.producto_str || `${it.product_type_read}:${it.product_id_read}`}</td>
                  <td className="px-4 py-2">{it.cantidad}</td>
                  <td className="px-4 py-2">{it.precio_unitario ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
