import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Search, Edit2, Trash2, Filter } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Articulos() {
    const { user } = useAuth();
    const [tuberias, setTuberias] = useState([]);
    const [equipos, setEquipos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('tuberias');
    const [searchTerm, setSearchTerm] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [categorias, setCategorias] = useState([]);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [formData, setFormData] = useState({
        nombre: '',
        descripcion: '',
        categoria: '',
        material: 'PVC',
        tipo_uso: 'POTABLE',
        diametro_nominal_mm: '',
        longitud_m: '',
        marca: '',
        modelo: '',
        potencia_hp: '',
        numero_serie: ''
    });

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [tubRes, eqRes, catRes] = await Promise.all([
                axios.get(`${API_URL}/api/tuberias/`),
                axios.get(`${API_URL}/api/equipos/`),
                axios.get(`${API_URL}/api/categorias/`)
            ]);

            setTuberias(tubRes.data.results || tubRes.data);
            setEquipos(eqRes.data.results || eqRes.data);
            setCategorias(catRes.data.results || catRes.data);
        } catch (err) {
            console.error("Error fetching data", err);
            setError("Error al cargar los datos");
        } finally {
            setLoading(false);
        }
    };

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        try {
            const payload = activeTab === 'tuberias' ? {
                nombre: formData.nombre,
                descripcion: formData.descripcion,
                categoria: parseInt(formData.categoria),
                material: formData.material,
                tipo_uso: formData.tipo_uso,
                diametro_nominal_mm: parseInt(formData.diametro_nominal_mm),
                longitud_m: parseFloat(formData.longitud_m)
            } : {
                nombre: formData.nombre,
                descripcion: formData.descripcion,
                categoria: parseInt(formData.categoria),
                marca: formData.marca,
                modelo: formData.modelo,
                potencia_hp: parseFloat(formData.potencia_hp) || null,
                numero_serie: formData.numero_serie
            };

            if (editingId) {
                const endpoint = activeTab === 'tuberias' ? 'tuberias' : 'equipos';
                await axios.put(`${API_URL}/api/${endpoint}/${editingId}/`, payload);
                setSuccess("Artículo actualizado exitosamente");
            } else {
                const endpoint = activeTab === 'tuberias' ? 'tuberias' : 'equipos';
                await axios.post(`${API_URL}/api/${endpoint}/`, payload);
                setSuccess("Artículo creado exitosamente");
            }

            resetForm();
            fetchData();
        } catch (err) {
            console.error("Error saving article", err);
            setError(err.response?.data?.detail || "Error al guardar el artículo");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de que deseas eliminar este artículo?')) return;

        try {
            const endpoint = activeTab === 'tuberias' ? 'tuberias' : 'equipos';
            await axios.delete(`${API_URL}/api/${endpoint}/${id}/`);
            setSuccess("Artículo eliminado exitosamente");
            fetchData();
        } catch (err) {
            console.error("Error deleting article", err);
            setError("Error al eliminar el artículo");
        }
    };

    const handleEdit = (item) => {
        setEditingId(item.id);
        if (activeTab === 'tuberias') {
            setFormData({
                nombre: item.nombre,
                descripcion: item.descripcion,
                categoria: item.categoria,
                material: item.material,
                tipo_uso: item.tipo_uso,
                diametro_nominal_mm: item.diametro_nominal_mm,
                longitud_m: item.longitud_m,
                marca: '',
                modelo: '',
                potencia_hp: '',
                numero_serie: ''
            });
        } else {
            setFormData({
                nombre: item.nombre,
                descripcion: item.descripcion,
                categoria: item.categoria,
                material: 'PVC',
                tipo_uso: 'POTABLE',
                diametro_nominal_mm: '',
                longitud_m: '',
                marca: item.marca,
                modelo: item.modelo,
                potencia_hp: item.potencia_hp || '',
                numero_serie: item.numero_serie
            });
        }
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({
            nombre: '',
            descripcion: '',
            categoria: '',
            material: 'PVC',
            tipo_uso: 'POTABLE',
            diametro_nominal_mm: '',
            longitud_m: '',
            marca: '',
            modelo: '',
            potencia_hp: '',
            numero_serie: ''
        });
        setEditingId(null);
        setShowForm(false);
    };

    const filteredItems = activeTab === 'tuberias' 
        ? tuberias.filter(t => t.nombre.toLowerCase().includes(searchTerm.toLowerCase()))
        : equipos.filter(e => e.nombre.toLowerCase().includes(searchTerm.toLowerCase()));

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando artículos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Gestión de Artículos</h1>
                {user?.role === 'ADMIN' && (
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                        <Plus size={20} /> Nuevo Artículo
                    </button>
                )}
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
            {showForm && user?.role === 'ADMIN' && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-bold mb-4">
                        {editingId ? 'Editar Artículo' : 'Crear Nuevo Artículo'}
                    </h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Nombre */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre *
                                </label>
                                <input
                                    type="text"
                                    name="nombre"
                                    value={formData.nombre}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            {/* Categoría */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Categoría *
                                </label>
                                <select
                                    name="categoria"
                                    value={formData.categoria}
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

                            {/* Descripción */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Descripción
                                </label>
                                <textarea
                                    name="descripcion"
                                    value={formData.descripcion}
                                    onChange={handleFormChange}
                                    rows="2"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            {/* Campos específicos para Tuberías */}
                            {activeTab === 'tuberias' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Material *
                                        </label>
                                        <select
                                            name="material"
                                            value={formData.material}
                                            onChange={handleFormChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
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
                                            value={formData.tipo_uso}
                                            onChange={handleFormChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
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
                                            value={formData.diametro_nominal_mm}
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
                                            value={formData.longitud_m}
                                            onChange={handleFormChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            required
                                        />
                                    </div>
                                </>
                            )}

                            {/* Campos específicos para Equipos */}
                            {activeTab === 'equipos' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Marca
                                        </label>
                                        <input
                                            type="text"
                                            name="marca"
                                            value={formData.marca}
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
                                            value={formData.modelo}
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
                                            value={formData.potencia_hp}
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
                                            value={formData.numero_serie}
                                            onChange={handleFormChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            required
                                        />
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="flex gap-2">
                            <button
                                type="submit"
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                {editingId ? 'Actualizar' : 'Crear'} Artículo
                            </button>
                            <button
                                type="button"
                                onClick={resetForm}
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition"
                            >
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-4 border-b">
                <button
                    onClick={() => setActiveTab('tuberias')}
                    className={`px-4 py-2 font-medium border-b-2 transition ${
                        activeTab === 'tuberias'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-800'
                    }`}
                >
                    Tuberías ({tuberias.length})
                </button>
                <button
                    onClick={() => setActiveTab('equipos')}
                    className={`px-4 py-2 font-medium border-b-2 transition ${
                        activeTab === 'equipos'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-800'
                    }`}
                >
                    Equipos ({equipos.length})
                </button>
            </div>

            {/* Búsqueda */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="relative">
                    <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Buscar artículo..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            {/* Tabla */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Nombre</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Categoría</th>
                                {activeTab === 'tuberias' ? (
                                    <>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Material</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Diámetro</th>
                                    </>
                                ) : (
                                    <>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Marca</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Serie</th>
                                    </>
                                )}
                                {user?.role === 'ADMIN' && (
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acciones</th>
                                )}
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {filteredItems.length === 0 ? (
                                <tr>
                                    <td colSpan={user?.role === 'ADMIN' ? 5 : 4} className="px-6 py-8 text-center text-gray-500">
                                        No hay artículos
                                    </td>
                                </tr>
                            ) : (
                                filteredItems.map(item => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm font-medium">{item.nombre}</td>
                                        <td className="px-6 py-4 text-sm">{item.categoria_nombre}</td>
                                        {activeTab === 'tuberias' ? (
                                            <>
                                                <td className="px-6 py-4 text-sm">{item.material}</td>
                                                <td className="px-6 py-4 text-sm">{item.diametro_nominal_mm}mm</td>
                                            </>
                                        ) : (
                                            <>
                                                <td className="px-6 py-4 text-sm">{item.marca}</td>
                                                <td className="px-6 py-4 text-sm">{item.numero_serie}</td>
                                            </>
                                        )}
                                        {user?.role === 'ADMIN' && (
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
                                        )}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}