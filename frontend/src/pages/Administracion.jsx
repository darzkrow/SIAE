import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, Building2, Droplets, Zap, Wrench, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Administracion() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('sucursales');
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Data states
    const [sucursales, setSucursales] = useState([]);
    const [acueductos, setAcueductos] = useState([]);
    const [tuberias, setTuberias] = useState([]);
    const [equipos, setEquipos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [organizaciones, setOrganizaciones] = useState([]);
    const [usuarios, setUsuarios] = useState([]);
    const [stockTuberias, setStockTuberias] = useState([]);
    const [stockEquipos, setStockEquipos] = useState([]);

    // Form data
    const [formData, setFormData] = useState({});

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (user?.role !== 'ADMIN') {
            setError('No tienes permiso para acceder a esta sección');
            return;
        }
        fetchAllData();
    }, [user]);

    const fetchAllData = async () => {
        setLoading(true);
        try {
            const [sucRes, acuRes, tubRes, eqRes, catRes, orgRes, usersRes, stockTubRes, stockEqRes] = await Promise.all([
                axios.get(`${API_URL}/api/sucursales/`),
                axios.get(`${API_URL}/api/acueductos/`),
                axios.get(`${API_URL}/api/tuberias/`),
                axios.get(`${API_URL}/api/equipos/`),
                axios.get(`${API_URL}/api/categorias/`),
                axios.get(`${API_URL}/api/organizaciones/`),
                axios.get(`${API_URL}/api/users/`),
                axios.get(`${API_URL}/api/stock-tuberias/`),
                axios.get(`${API_URL}/api/stock-equipos/`)
            ]);

            setSucursales(sucRes.data.results || sucRes.data);
            setAcueductos(acuRes.data.results || acuRes.data);
            setTuberias(tubRes.data.results || tubRes.data);
            setEquipos(eqRes.data.results || eqRes.data);
            setCategorias(catRes.data.results || catRes.data);
            setOrganizaciones(orgRes.data.results || orgRes.data);
            setUsuarios(usersRes.data.results || usersRes.data);
            setStockTuberias(stockTubRes.data.results || stockTubRes.data);
            setStockEquipos(stockEqRes.data.results || stockEqRes.data);
        } catch (err) {
            console.error("Error fetching data", err);
            setError("Error al cargar los datos");
        } finally {
            setLoading(false);
        }
    };

    const handleFormChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        try {
            const endpoint = `${API_URL}/api/${activeTab}/`;
            let payload = { ...formData };

            // Convertir valores numéricos para stock
            if (activeTab === 'stock-tuberias' || activeTab === 'stock-equipos') {
                if (activeTab === 'stock-tuberias') {
                    payload.tuberia = parseInt(payload.tuberia);
                } else {
                    payload.equipo = parseInt(payload.equipo);
                }
                payload.acueducto = parseInt(payload.acueducto);
                payload.cantidad = parseInt(payload.cantidad);
            }

            if (editingId) {
                await axios.put(`${endpoint}${editingId}/`, payload);
                setSuccess(`${activeTab} actualizado exitosamente`);
            } else {
                await axios.post(endpoint, payload);
                setSuccess(`${activeTab} creado exitosamente`);
            }

            resetForm();
            fetchAllData();
        } catch (err) {
            console.error("Error saving data", err);
            setError(err.response?.data?.detail || `Error al guardar ${activeTab}`);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm(`¿Estás seguro de que deseas eliminar este elemento?`)) return;

        try {
            await axios.delete(`${API_URL}/api/${activeTab}/${id}/`);
            setSuccess(`${activeTab} eliminado exitosamente`);
            fetchAllData();
        } catch (err) {
            console.error("Error deleting data", err);
            setError("Error al eliminar el elemento");
        }
    };

    const handleEdit = (item) => {
        setEditingId(item.id);
        setFormData(item);
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({});
        setEditingId(null);
        setShowForm(false);
    };

    const renderForm = () => {
        switch (activeTab) {
            case 'sucursales':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre *
                                </label>
                                <input
                                    type="text"
                                    name="nombre"
                                    value={formData.nombre || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Organización Central *
                                </label>
                                <select
                                    name="organizacion_central"
                                    value={formData.organizacion_central || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {organizaciones.map(o => (
                                        <option key={o.id} value={o.id}>{o.nombre}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Sucursal
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            case 'acueductos':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre *
                                </label>
                                <input
                                    type="text"
                                    name="nombre"
                                    value={formData.nombre || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Sucursal *
                                </label>
                                <select
                                    name="sucursal"
                                    value={formData.sucursal || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {sucursales.map(s => (
                                        <option key={s.id} value={s.id}>{s.nombre}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Acueducto
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            case 'tuberias':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre *
                                </label>
                                <input
                                    type="text"
                                    name="nombre"
                                    value={formData.nombre || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Categoría *
                                </label>
                                <select
                                    name="categoria"
                                    value={formData.categoria || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {categorias.map(c => (
                                        <option key={c.id} value={c.id}>{c.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Material *
                                </label>
                                <select
                                    name="material"
                                    value={formData.material || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    <option value="PVC">PVC</option>
                                    <option value="HIERRO">Hierro Dúctil</option>
                                    <option value="CEMENTO">Cemento</option>
                                    <option value="OTRO">Otro</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Tipo de Uso *
                                </label>
                                <select
                                    name="tipo_uso"
                                    value={formData.tipo_uso || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    <option value="POTABLE">Aguas Potables</option>
                                    <option value="SERVIDAS">Aguas Servidas</option>
                                    <option value="RIEGO">Riego</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Diámetro Nominal (mm) *
                                </label>
                                <input
                                    type="number"
                                    name="diametro_nominal_mm"
                                    value={formData.diametro_nominal_mm || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Longitud (m) *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="longitud_m"
                                    value={formData.longitud_m || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Descripción
                            </label>
                            <textarea
                                name="descripcion"
                                value={formData.descripcion || ''}
                                onChange={handleFormChange}
                                rows="3"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Tubería
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            case 'equipos':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre *
                                </label>
                                <input
                                    type="text"
                                    name="nombre"
                                    value={formData.nombre || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Categoría *
                                </label>
                                <select
                                    name="categoria"
                                    value={formData.categoria || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {categorias.map(c => (
                                        <option key={c.id} value={c.id}>{c.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Marca
                                </label>
                                <input
                                    type="text"
                                    name="marca"
                                    value={formData.marca || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Modelo
                                </label>
                                <input
                                    type="text"
                                    name="modelo"
                                    value={formData.modelo || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Potencia (HP)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="potencia_hp"
                                    value={formData.potencia_hp || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Número de Serie *
                                </label>
                                <input
                                    type="text"
                                    name="numero_serie"
                                    value={formData.numero_serie || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Descripción
                            </label>
                            <textarea
                                name="descripcion"
                                value={formData.descripcion || ''}
                                onChange={handleFormChange}
                                rows="3"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Equipo
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            case 'usuarios':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Usuario *
                                </label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username || ''}
                                    onChange={handleFormChange}
                                    disabled={editingId}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email *
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre
                                </label>
                                <input
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Apellido
                                </label>
                                <input
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Contraseña {editingId ? '(dejar en blanco para no cambiar)' : '*'}
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required={!editingId}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Rol *
                                </label>
                                <select
                                    name="role"
                                    value={formData.role || 'OPERADOR'}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="ADMIN">Administrador</option>
                                    <option value="OPERADOR">Operador</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Sucursal {formData.role === 'OPERADOR' ? '*' : '(opcional)'}
                                </label>
                                <select
                                    name="sucursal"
                                    value={formData.sucursal || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required={formData.role === 'OPERADOR'}
                                >
                                    <option value="">Seleccionar...</option>
                                    {sucursales.map(s => (
                                        <option key={s.id} value={s.id}>{s.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex items-end">
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active !== false}
                                        onChange={handleFormChange}
                                        className="w-4 h-4 rounded"
                                    />
                                    <span className="text-sm font-medium text-gray-700">Usuario Activo</span>
                                </label>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Usuario
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            case 'stock-tuberias':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Tubería *
                                </label>
                                <select
                                    name="tuberia"
                                    value={formData.tuberia || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {tuberias.map(t => (
                                        <option key={t.id} value={t.id}>{t.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Acueducto *
                                </label>
                                <select
                                    name="acueducto"
                                    value={formData.acueducto || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {acueductos.map(a => (
                                        <option key={a.id} value={a.id}>{a.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Cantidad *
                                </label>
                                <input
                                    type="number"
                                    name="cantidad"
                                    value={formData.cantidad || ''}
                                    onChange={handleFormChange}
                                    min="0"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Stock Tubería
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            case 'stock-equipos':
                return (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Equipo *
                                </label>
                                <select
                                    name="equipo"
                                    value={formData.equipo || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {equipos.map(e => (
                                        <option key={e.id} value={e.id}>{e.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Acueducto *
                                </label>
                                <select
                                    name="acueducto"
                                    value={formData.acueducto || ''}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Seleccionar...</option>
                                    {acueductos.map(a => (
                                        <option key={a.id} value={a.id}>{a.nombre}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Cantidad *
                                </label>
                                <input
                                    type="number"
                                    name="cantidad"
                                    value={formData.cantidad || ''}
                                    onChange={handleFormChange}
                                    min="0"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                                {editingId ? 'Actualizar' : 'Crear'} Stock Equipo
                            </button>
                            <button type="button" onClick={resetForm} className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition">
                                Cancelar
                            </button>
                        </div>
                    </form>
                );

            default:
                return null;
        }
    };

    const renderTable = () => {
        let data = [];
        let columns = [];

        switch (activeTab) {
            case 'sucursales':
                data = sucursales;
                columns = ['nombre', 'organizacion_central'];
                break;
            case 'acueductos':
                data = acueductos;
                columns = ['nombre', 'sucursal'];
                break;
            case 'tuberias':
                data = tuberias;
                columns = ['nombre', 'material', 'tipo_uso', 'diametro_nominal_mm', 'longitud_m'];
                break;
            case 'equipos':
                data = equipos;
                columns = ['nombre', 'marca', 'modelo', 'numero_serie'];
                break;
            case 'usuarios':
                data = usuarios;
                columns = ['username', 'email', 'first_name', 'role', 'is_active'];
                break;
            case 'stock-tuberias':
                data = stockTuberias;
                columns = ['tuberia', 'acueducto', 'cantidad'];
                break;
            case 'stock-equipos':
                data = stockEquipos;
                columns = ['equipo', 'acueducto', 'cantidad'];
                break;
            default:
                return null;
        }

        return (
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                {columns.map(col => (
                                    <th key={col} className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                                        {col.charAt(0).toUpperCase() + col.slice(1).replace(/_/g, ' ')}
                                    </th>
                                ))}
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {data.length === 0 ? (
                                <tr>
                                    <td colSpan={columns.length + 1} className="px-6 py-8 text-center text-gray-500">
                                        No hay datos
                                    </td>
                                </tr>
                            ) : (
                                data.map(item => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        {columns.map(col => (
                                            <td key={col} className="px-6 py-4 text-sm">
                                                {typeof item[col] === 'object' ? item[col]?.nombre || '-' : item[col] || '-'}
                                            </td>
                                        ))}
                                        <td className="px-6 py-4 text-sm flex gap-2">
                                            <button
                                                onClick={() => handleEdit(item)}
                                                className="text-blue-600 hover:text-blue-800"
                                            >
                                                <Edit2 size={18} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(item.id)}
                                                className="text-red-600 hover:text-red-800"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    };

    if (user?.role !== 'ADMIN') {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                <h2 className="text-2xl font-bold text-red-800 mb-2">Acceso Denegado</h2>
                <p className="text-red-700">Solo los administradores pueden acceder a esta sección</p>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando datos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Administración</h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                    <Plus size={20} /> Nuevo
                </button>
            </div>

            {/* Messages */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                    {error}
                </div>
            )}
            {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
                    {success}
                </div>
            )}

            {/* Form */}
            {showForm && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-bold mb-4">
                        {editingId ? 'Editar' : 'Crear Nuevo'} {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
                    </h2>
                    {renderForm()}
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-4 border-b bg-white rounded-t-lg overflow-x-auto">
                {[
                    { id: 'sucursales', label: 'Sucursales', icon: Building2 },
                    { id: 'acueductos', label: 'Acueductos', icon: Droplets },
                    { id: 'tuberias', label: 'Tuberías', icon: Zap },
                    { id: 'equipos', label: 'Equipos', icon: Wrench },
                    { id: 'stock-tuberias', label: 'Stock Tuberías', icon: Zap },
                    { id: 'stock-equipos', label: 'Stock Equipos', icon: Wrench },
                    { id: 'usuarios', label: 'Usuarios', icon: Users }
                ].map(tab => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => {
                                setActiveTab(tab.id);
                                resetForm();
                            }}
                            className={`px-4 py-3 font-medium border-b-2 transition flex items-center gap-2 ${
                                activeTab === tab.id
                                    ? 'border-blue-600 text-blue-600'
                                    : 'border-transparent text-gray-600 hover:text-gray-800'
                            }`}
                        >
                            <Icon size={20} />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {/* Table */}
            {renderTable()}
        </div>
    );
}
