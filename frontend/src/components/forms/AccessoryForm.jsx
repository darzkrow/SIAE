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
    <form onSubmit={submit}>
      <div className="row">
        <div className="col-md-8">
          <div className="form-group">
            <label>Nombre *</label>
            <input
              name="nombre"
              value={data.nombre}
              onChange={handleChange}
              className="form-control"
              placeholder="Nombre del accesorio"
              required
            />
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Categoría *</label>
            <select name="categoria" value={data.categoria} onChange={handleChange} className="form-control" required>
              <option value="">Seleccionar...</option>
              {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="form-group">
            <label>Unidad de Medida *</label>
            <select name="unidad_medida" value={data.unidad_medida} onChange={handleChange} className="form-control" required>
              <option value="">Seleccionar...</option>
              {units.map(u => <option key={u.id} value={u.id}>{u.nombre} ({u.simbolo})</option>)}
            </select>
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Proveedor *</label>
            <select name="proveedor" value={data.proveedor} onChange={handleChange} className="form-control" required>
              <option value="">Seleccionar...</option>
              {suppliers.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
            </select>
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Tipo de Accesorio</label>
            <select name="tipo_accesorio" value={data.tipo_accesorio} onChange={handleChange} className="form-control">
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
        </div>
      </div>

      <div className="row">
        <div className="col-md-3">
          <div className="form-group">
            <label>Diámetro Entrada</label>
            <input type="number" step="0.01" name="diametro_entrada" value={data.diametro_entrada} onChange={handleChange} className="form-control" />
          </div>
        </div>
        <div className="col-md-3">
          <div className="form-group">
            <label>Unidad Diámetro</label>
            <select name="unidad_diametro" value={data.unidad_diametro} onChange={handleChange} className="form-control">
              <option value="PULGADAS">Pulgadas</option>
              <option value="MM">mm</option>
            </select>
          </div>
        </div>
        <div className="col-md-3">
          <div className="form-group">
            <label>Tipo Conexión</label>
            <select name="tipo_conexion" value={data.tipo_conexion} onChange={handleChange} className="form-control">
              <option value="BRIDADA">Bridada</option>
              <option value="ROSCADA">Roscada</option>
              <option value="SOLDABLE">Soldable</option>
              <option value="CAMPANA">Espiga y Campana</option>
              <option value="RAPIDA">Conexión Rápida</option>
            </select>
          </div>
        </div>
        <div className="col-md-3">
          <div className="form-group">
            <label>Precio Unitario Est.</label>
            <div className="input-group">
              <div className="input-group-prepend">
                <span className="input-group-text">$</span>
              </div>
              <input type="number" step="0.01" name="precio_unitario" value={data.precio_unitario} onChange={handleChange} className="form-control" />
            </div>
          </div>
        </div>
      </div>

      <div className="form-group">
        <label>Descripción / Detalles</label>
        <textarea
          name="descripcion"
          value={data.descripcion}
          onChange={handleChange}
          className="form-control"
          rows="2"
          placeholder="Material, presión máxima, etc..."
        ></textarea>
      </div>

      <div className="card-footer px-0 pb-0 bg-transparent text-right">
        <button type="button" onClick={onCancel} className="btn btn-default mr-2">Cancelar</button>
        <button type="submit" className="btn btn-primary">
          {initialData?.id ? 'Actualizar Accesorio' : 'Crear Accesorio'}
        </button>
      </div>
    </form>
  );
}
