import { useState, useEffect } from 'react';

export default function AccessoryForm({ categorias = [], units = [], suppliers = [], initialData = {}, onSubmit, onCancel }) {
  const [data, setData] = useState({
    nombre: '', descripcion: '', categoria: '', unidad_medida: '', proveedor: '',
    stock_minimo: 0, precio_unitario: 0,
    tipo_accesorio: 'VALVULA', unidad_diametro: 'PULGADAS', diametro_entrada: 1,
    tipo_conexion: 'ROSCADA'
  });

  useEffect(() => {
    if (initialData && Object.keys(initialData).length) {
      setData(prev => ({
        ...prev,
        ...initialData,
        categoria: initialData.categoria?.id || initialData.categoria || '',
        unidad_medida: initialData.unidad_medida?.id || initialData.unidad_medida || '',
        proveedor: initialData.proveedor?.id || initialData.proveedor || ''
      }));
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setData(prev => ({ ...prev, [name]: value }));
  };

  const validate = () => {
    if (!data.nombre || !data.categoria || !data.unidad_medida || !data.proveedor) return false;
    return true;
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
        <div>
          <label className="block text-sm font-medium mb-1">Unidad *</label>
          <select name="unidad_medida" value={data.unidad_medida} onChange={handleChange} className="w-full border p-2 rounded" required>
            <option value="">Seleccionar...</option>
            {units.map(u => <option key={u.id} value={u.id}>{u.nombre} ({u.simbolo})</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Proveedor *</label>
          <select name="proveedor" value={data.proveedor} onChange={handleChange} className="w-full border p-2 rounded" required>
            <option value="">Seleccionar...</option>
            {suppliers.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Mínimo Stock</label>
          <input type="number" name="stock_minimo" value={data.stock_minimo} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Precio Unitario</label>
          <input type="number" step="0.01" name="precio_unitario" value={data.precio_unitario} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Tipo Accesorio</label>
          <select name="tipo_accesorio" value={data.tipo_accesorio} onChange={handleChange} className="w-full border p-2 rounded">
            <option value="VALVULA">Válvula</option>
            <option value="CODO">Codo</option>
            <option value="TEE">Tee</option>
            <option value="REDUCCION">Reducción</option>
            <option value="TAPON">Tapón</option>
            <option value="BRIDA">Brida</option>
            <option value="UNION">Unión</option>
            <option value="COLLAR">Collar</option>
            <option value="ADAPTADOR">Adaptador</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Unidad diámetro</label>
          <select name="unidad_diametro" value={data.unidad_diametro} onChange={handleChange} className="w-full border p-2 rounded">
            <option value="PULGADAS">Pulgadas</option>
            <option value="MM">mm</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Diámetro entrada</label>
          <input type="number" step="0.01" name="diametro_entrada" value={data.diametro_entrada} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Tipo conexión</label>
          <select name="tipo_conexion" value={data.tipo_conexion} onChange={handleChange} className="w-full border p-2 rounded">
            <option value="BRIDADA">Bridada</option>
            <option value="ROSCADA">Roscada</option>
            <option value="SOLDABLE">Soldable</option>
            <option value="CAMPANA">Espiga y Campana</option>
            <option value="RAPIDA">Conexión Rápida</option>
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
