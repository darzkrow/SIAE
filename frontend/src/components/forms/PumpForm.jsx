import { useState, useEffect } from 'react';

export default function PumpForm({ categorias = [], units = [], suppliers = [], marcas = [], initialData = {}, onSubmit, onCancel }) {
  const [data, setData] = useState({
    nombre: '', descripcion: '', categoria: '', unidad_medida: '', proveedor: '',
    stock_minimo: 0, precio_unitario: 0,
    tipo_equipo: 'BOMBA_CENTRIFUGA', marca: '', modelo: '', numero_serie: '',
    potencia_hp: 0, voltaje: 110, fases: 'MONOFASICO'
  });

  useEffect(() => {
    if (initialData && Object.keys(initialData).length) {
      setData(prev => ({
        ...prev,
        ...initialData,
        categoria: initialData.categoria?.id || initialData.categoria || '',
        proveedor: initialData.proveedor?.id || initialData.proveedor || '',
        marca: initialData.marca?.id || initialData.marca || ''
      }));
    }
  }, [initialData]);

  // Auto-select a sensible default unit (UNIDAD) for pumps/motors
  useEffect(() => {
    if (!data.unidad_medida && Array.isArray(units) && units.length > 0) {
      const unidad = units.find(u => (u.tipo === 'UNIDAD') || /unidad/i.test(u.nombre));
      setData(prev => ({ ...prev, unidad_medida: (unidad?.id ?? units[0].id) }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [units]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setData(prev => ({ ...prev, [name]: value }));
  };

  const validate = () => {
    const required = ['nombre', 'categoria', 'unidad_medida', 'proveedor', 'tipo_equipo', 'marca', 'modelo', 'numero_serie', 'potencia_hp', 'voltaje', 'fases'];
    return required.every(k => data[k] || data[k] === 0);
  };

  const submit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit?.(data);
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-1">Nombre *</label>
          <input name="nombre" value={data.nombre} onChange={handleChange} className="w-full border p-2 rounded" required />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Categoría *</label>
          <select name="categoria" value={data.categoria} onChange={handleChange} className="w-full border p-2 rounded" required>
            <option value="">Seleccionar...</option>
            {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
          </select>
        </div>
        {/* Unidad se selecciona automáticamente como 'UNIDAD'; se oculta en el formulario */}
        <div>
          <label className="block text-sm font-medium mb-1">Proveedor *</label>
          <select name="proveedor" value={data.proveedor} onChange={handleChange} className="w-full border p-2 rounded" required>
            <option value="">Seleccionar...</option>
            {suppliers.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Tipo de equipo *</label>
          <select name="tipo_equipo" value={data.tipo_equipo} onChange={handleChange} className="w-full border p-2 rounded">
            <option value="BOMBA_CENTRIFUGA">Bomba Centrífuga</option>
            <option value="BOMBA_SUMERGIBLE">Bomba Sumergible</option>
            <option value="BOMBA_PERIFERICA">Bomba Periférica</option>
            <option value="BOMBA_TURBINA">Bomba de Turbina</option>
            <option value="MOTOR_ELECTRICO">Motor Eléctrico</option>
            <option value="VARIADOR">Variador de Frecuencia</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Marca *</label>
          <select name="marca" value={data.marca} onChange={handleChange} className="w-full border p-2 rounded">
            <option value="">Seleccionar...</option>
            {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Modelo *</label>
          <input name="modelo" value={data.modelo} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Número de serie *</label>
          <input name="numero_serie" value={data.numero_serie} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Potencia (HP) *</label>
          <input type="number" step="0.01" name="potencia_hp" value={data.potencia_hp} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Voltaje *</label>
          <input type="number" name="voltaje" value={data.voltaje} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Fases *</label>
          <select name="fases" value={data.fases} onChange={handleChange} className="w-full border p-2 rounded">
            <option value="MONOFASICO">Monofásico</option>
            <option value="TRIFASICO">Trifásico</option>
          </select>
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Guardar</button>
      </div>
    </form>
  );
}
