import { useEffect, useState } from 'react';
import { InventoryService } from '../services/inventory.service';

export default function Catalogo() {
  const [categorias, setCategorias] = useState([]);
  const [marcas, setMarcas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [catRes, marRes] = await Promise.all([
          InventoryService.categories.getAll(),
          InventoryService.marcas.getAll(),
        ]);
        setCategorias(Array.isArray(catRes.data) ? catRes.data : (catRes.data?.results || []));
        setMarcas(Array.isArray(marRes.data) ? marRes.data : (marRes.data?.results || []));
      } catch (e) {
        setError('No se pudo cargar el catálogo');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="text-gray-600">Cargando catálogo...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-3">Categorías</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 px-3">Nombre</th>
                <th className="py-2 px-3">Descripción</th>
              </tr>
            </thead>
            <tbody>
              {categorias.map((c) => (
                <tr key={c.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-3">{c.nombre || c.name}</td>
                  <td className="py-2 px-3 text-gray-600">{c.descripcion || c.description || '-'}</td>
                </tr>
              ))}
              {categorias.length === 0 && (
                <tr><td className="py-3 px-3 text-gray-500" colSpan={2}>Sin categorías</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-3">Marcas</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 px-3">Nombre</th>
              </tr>
            </thead>
            <tbody>
              {marcas.map((m) => (
                <tr key={m.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-3">{m.nombre || m.name}</td>
                </tr>
              ))}
              {marcas.length === 0 && (
                <tr><td className="py-3 px-3 text-gray-500">Sin marcas</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
