import { useEffect, useState } from 'react';
import { InventoryService } from '../services/inventory.service';

export default function Geografia() {
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
        setStates(sRes.data || []);
        setMunicipalities(mRes.data || []);
        setParishes(pRes.data || []);
        setUbicaciones(uRes.data || []);
      } catch (e) {
        setError('No se pudo cargar la geografía');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="text-gray-600">Cargando geografía...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-3">Estados</h3>
        <ul className="space-y-1 text-sm">
          {states.map(s => (
            <li key={s.id} className="py-1 border-b">{s.nombre || s.name}</li>
          ))}
          {states.length === 0 && <li className="text-gray-500">Sin estados</li>}
        </ul>
      </section>

      <section className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-3">Municipios</h3>
        <ul className="space-y-1 text-sm">
          {municipalities.map(m => (
            <li key={m.id} className="py-1 border-b">{m.nombre || m.name}</li>
          ))}
          {municipalities.length === 0 && <li className="text-gray-500">Sin municipios</li>}
        </ul>
      </section>

      <section className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-3">Parroquias</h3>
        <ul className="space-y-1 text-sm">
          {parishes.map(p => (
            <li key={p.id} className="py-1 border-b">{p.nombre || p.name}</li>
          ))}
          {parishes.length === 0 && <li className="text-gray-500">Sin parroquias</li>}
        </ul>
      </section>

      <section className="bg-white rounded-lg shadow p-4 lg:col-span-2">
        <h3 className="text-lg font-semibold mb-3">Ubicaciones</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 px-3">Nombre</th>
                <th className="py-2 px-3">Dirección</th>
                <th className="py-2 px-3">Acueducto</th>
              </tr>
            </thead>
            <tbody>
              {ubicaciones.map(u => (
                <tr key={u.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-3">{u.nombre || u.name}</td>
                  <td className="py-2 px-3 text-gray-600">{u.direccion || u.address || '-'}</td>
                  <td className="py-2 px-3">{u.acueducto_nombre || u.acueducto || '-'}</td>
                </tr>
              ))}
              {ubicaciones.length === 0 && (
                <tr><td className="py-3 px-3 text-gray-500" colSpan={3}>Sin ubicaciones</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
