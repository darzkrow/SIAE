import { useState, useEffect } from 'react';

export default function PumpForm({ categorias = [], units = [], suppliers = [], marcas = [], initialData = {}, onSubmit, onCancel }) {
  const [data, setData] = useState({
    nombre: '', descripcion: '', categoria: '', unidad_medida: '', proveedor: '',
    stock_minimo: 0, precio_unitario: 0,
    tipo_equipo: 'BOMBA_CENTRIFUGA', marca: '', modelo: '', numero_serie: '',
    potencia_hp: 0, voltaje: 110, fases: 'MONOFASICO'
  });
  const [pumpCategory, setPumpCategory] = useState(null);

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

  // Lock category to 'Bombas y Motores' (codigo = 'BOM')
  useEffect(() => {
    if (Array.isArray(categorias) && categorias.length > 0) {
      const bom = categorias.find(c => c.codigo === 'BOM');
      if (bom) {
        setPumpCategory(bom);
        setData(prev => ({ ...prev, categoria: bom.id }));
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categorias]);

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
    <form onSubmit={submit}>
      <div className="row">
        <div className="col-md-9">
          <div className="form-group">
            <label>Nombre *</label>
            <input
              name="nombre"
              value={data.nombre}
              onChange={handleChange}
              className="form-control"
              placeholder="Nombre de la bomba/equipo"
              required
            />
          </div>
        </div>
        <div className="col-md-3">
          <div className="form-group">
            <label>Categoría *</label>
            {pumpCategory ? (
              <input
                value={pumpCategory.nombre}
                className="form-control"
                disabled
              />
            ) : (
              <input
                value="Cargando..."
                className="form-control"
                disabled
              />
            )}
            <input type="hidden" name="categoria" value={data.categoria} />
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="form-group">
            <label>Tipo de Equipo *</label>
            <select name="tipo_equipo" value={data.tipo_equipo} onChange={handleChange} className="form-control">
              <option value="BOMBA_CENTRIFUGA">Bomba Centrífuga</option>
              <option value="BOMBA_SUMERGIBLE">Bomba Sumergible</option>
              <option value="BOMBA_PERIFERICA">Bomba Periférica</option>
              <option value="BOMBA_TURBINA">Bomba de Turbina</option>
              <option value="MOTOR_ELECTRICO">Motor Eléctrico</option>
              <option value="VARIADOR">Variador de Frecuencia</option>
            </select>
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Marca *</label>
            <select name="marca" value={data.marca} onChange={handleChange} className="form-control">
              <option value="">Seleccionar...</option>
              {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Modelo *</label>
            <input name="modelo" value={data.modelo} onChange={handleChange} className="form-control" placeholder="Modelo / Referencia" />
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-4">
          <div className="form-group">
            <label>Número de Serie *</label>
            <input name="numero_serie" value={data.numero_serie} onChange={handleChange} className="form-control" placeholder="S/N" />
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

      <div className="row">
        <div className="col-md-4">
          <div className="form-group">
            <label>Potencia (HP) *</label>
            <input type="number" step="0.01" name="potencia_hp" value={data.potencia_hp} onChange={handleChange} className="form-control" />
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Voltaje (V) *</label>
            <input type="number" name="voltaje" value={data.voltaje} onChange={handleChange} className="form-control" />
          </div>
        </div>
        <div className="col-md-4">
          <div className="form-group">
            <label>Fases *</label>
            <select name="fases" value={data.fases} onChange={handleChange} className="form-control">
              <option value="MONOFASICO">Monofásico</option>
              <option value="TRIFASICO">Trifásico</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-group">
        <label>Descripción / Observaciones Técnicas</label>
        <textarea
          name="descripcion"
          value={data.descripcion}
          onChange={handleChange}
          className="form-control"
          rows="2"
          placeholder="Especificaciones técnicas adicionales..."
        ></textarea>
      </div>

      <div className="card-footer px-0 pb-0 bg-transparent text-right">
        <button type="button" onClick={onCancel} className="btn btn-default mr-2">Cancelar</button>
        <button type="submit" className="btn btn-primary">
          {initialData?.id ? 'Actualizar Equipo' : 'Crear Equipo'}
        </button>
      </div>
    </form>
  );
}
