import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, AlertCircle, Bell } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Alertas() {
    const { user } = useAuth();
    const [alertas, setAlertas] = useState([]);
    const [notificaciones, setNotificaciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [activeTab, setActiveTab] = useState('alertas');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [tuberias, setTuberias] = useState([]);
    const [equipos, setEquipos] = useState([]);
    const [acueductos, setAcueductos] = useState([]);

    const [formData, setFormData] = useState({
        tuberia: '',
        equipo: '',
        acueducto: '',
        umbral_minimo: '',
        activo: true
    });

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [alertasRes, notifRes, tubRes, eqRes, acuRes] = await Promise.all([
                axios.get(`${API_URL}/api/alertas/`),
                axios.get(`${API_URL}/api/notificaciones/`),
                axios.get(`${API_URL}/api/tuberias/`),
                axios.get(`${API_URL}/api/equipos/`),
                axios.get(`${API_URL}/api/acueductos/`)
            ]);

            setAlertas(alertasRes.data.results || alertasRes.data);
            setNotificaciones(notifRes.data.results || notifRes.data);
            setTuberias(tubRes.data.results || tubRes.data);
            setEquipos(eqRes.data.results || eqRes.data);
            setAcueductos(acuRes.data.results || acuRes.data);
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
            const payload = {
                tuberia: formData.tuberia ? parseInt(formData.tuberia) : null,
                equipo: formData.equipo ? parseInt(formData.equipo) : null,
                acueducto: parseInt(formData.acueducto),
                umbral_minimo: parseInt(formData.umbral_minimo),
                activo: formData.activo
            };

            if (editingId) {
                await axios.put(`${API_URL}/api/alertas/${editingId}/`, payload);
                setSuccess("Alerta actualizada exitosamente");
            } else {
                await axios.post(`${API_URL}/api/alertas/`, payload);
                setSuccess("Alerta creada exitosamente");
            }

            resetForm();
            fetchData();
        } catch (err) {
            console.error("Error saving alert", err);
            setError(err.response?.data?.detail || "Error al guardar la alerta");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de que deseas eliminar esta alerta?')) return;

        try {
            await axios.delete(`${API_URL}/api/alertas/${id}/`);
            setSuccess("Alerta eliminada exitosamente");
            fetchData();
        } catch (err) {
            console.error("Error deleting alert", err);
            setError("Error al eliminar la alerta");
        }
    };

    const handleEdit = (alerta) => {
        setEditingId(alerta.id);
        setFormData({
            tuberia: alerta.tuberia || '',
            equipo: alerta.equipo || '',
            acueducto: alerta.acueducto,
            umbral_minimo: alerta.umbral_minimo,
            activo: alerta.activo
        });
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({
            tuberia: '',
            equipo: '',
            acueducto: '',
            umbral_minimo: '',
            activo: true
        });
        setEditingId(null);
        setShowForm(false);
    };

    const markNotificationAsRead = async (id) => {
        try {
            await axios.patch(`${API_URL}/api/notificaciones/${id}/`, { enviada: true });
            fetchData();
        } catch (err) {
            console.error("Error updating notification", err);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando alertas...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Gestión de Alertas</h1>
                {user?.role === 'ADMIN' && (
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                        <Plus size={20} /> Nueva Alerta
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
                        {editingId ? 'Editar Alerta' : 'Crear Nueva Alerta'}
                    </h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Acueducto */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Acueducto *
                                </label>
                                <select
                                    name="acueducto"
                                    value={formData.acueducto}
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

                            {/* Artículo */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Artículo *
                                </label>
                                <div className="flex gap-2">
                                    <select
                                        name="tuberia"
                                        value={formData.tuberia}
                                        onChange={(e) => {
                                            handleFormChange(e);
                                            if (e.target.value) setFormData(prev => ({ ...prev, equipo: '' }));
                                        }}
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="">Tubería...</option>
                                        {tuberias.map(t => (
                                            <option key={t.id} value={t.id}>{t.nombre}</option>
                                        ))}
                                    </select>
                                    <select
                                        name="equipo"
                                        value={formData.equipo}
                                        onChange={(e) => {
                                            handleFormChange(e);
                                            if (e.target.value) setFormData(prev => ({ ...prev, tuberia: '' }));
                                        }}
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="">Equipo...</option>
                                        {equipos.map(e => (
                                            <option key={e.id} value={e.id}>{e.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Umbral Mínimo */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Umbral Mínimo *
                                </label>
                                <input
                                    type="number"
                                    name="umbral_minimo"
                                    value={formData.umbral_minimo}
                                    onChange={handleFormChange}
                                    min="0"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            {/* Activo */}
                            <div className="flex items-end">
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        name="activo"
                                        checked={formData.activo}
                                        onChange={handleFormChange}
                                        className="w-4 h-4 rounded"
                                    />
                                    <span className="text-sm font-medium text-gray-700">Alerta Activa</span>
                                </label>
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <button
                                type="submit"
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                {editingId ? 'Actualizar' : 'Crear'} Alerta
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
                    onClick={() => setActiveTab('alertas')}
                    className={`px-4 py-2 font-medium border-b-2 transition ${
                        activeTab === 'alertas'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-800'
                    }`}
                >
                    Alertas ({alertas.length})
                </button>
                <button
                    onClick={() => setActiveTab('notificaciones')}
                    className={`px-4 py-2 font-medium border-b-2 transition ${
                        activeTab === 'notificaciones'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-800'
                    }`}
                >
                    Notificaciones ({notificaciones.length})
                </button>
            </div>

            {/* Alertas Tab */}
            {activeTab === 'alertas' && (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Artículo</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acueducto</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Umbral</th>
                                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Estado</th>
                                    {user?.role === 'ADMIN' && (
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acciones</th>
                                    )}
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {alertas.length === 0 ? (
                                    <tr>
                                        <td colSpan={user?.role === 'ADMIN' ? 5 : 4} className="px-6 py-8 text-center text-gray-500">
                                            No hay alertas configuradas
                                        </td>
                                    </tr>
                                ) : (
                                    alertas.map(alerta => (
                                        <tr key={alerta.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 text-sm font-medium">
                                                {alerta.tuberia ? `Tubería ${alerta.tuberia}` : `Equipo ${alerta.equipo}`}
                                            </td>
                                            <td className="px-6 py-4 text-sm">{alerta.acueducto}</td>
                                            <td className="px-6 py-4 text-sm font-semibold">{alerta.umbral_minimo}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                                    alerta.activo
                                                        ? 'bg-green-100 text-green-800'
                                                        : 'bg-gray-100 text-gray-800'
                                                }`}>
                                                    {alerta.activo ? 'Activa' : 'Inactiva'}
                                                </span>
                                            </td>
                                            {user?.role === 'ADMIN' && (
                                                <td className="px-6 py-4 text-sm flex gap-2">
                                                    <button
                                                        onClick={() => handleEdit(alerta)}
                                                        className="text-blue-600 hover:text-blue-800"
                                                    >
                                                        <Edit2 size={18} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(alerta.id)}
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
            )}

            {/* Notificaciones Tab */}
            {activeTab === 'notificaciones' && (
                <div className="space-y-4">
                    {notificaciones.length === 0 ? (
                        <div className="bg-white rounded-lg shadow p-8 text-center">
                            <Bell size={48} className="mx-auto text-gray-400 mb-4" />
                            <p className="text-gray-600">No hay notificaciones</p>
                        </div>
                    ) : (
                        notificaciones.map(notif => (
                            <div
                                key={notif.id}
                                className={`rounded-lg p-4 border-l-4 ${
                                    notif.enviada
                                        ? 'bg-gray-50 border-gray-400'
                                        : 'bg-yellow-50 border-yellow-400'
                                }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <AlertCircle size={20} className={notif.enviada ? 'text-gray-600' : 'text-yellow-600'} />
                                            <p className="font-semibold text-gray-800">{notif.mensaje}</p>
                                        </div>
                                        <p className="text-sm text-gray-600">
                                            {new Date(notif.creada_en).toLocaleString()}
                                        </p>
                                    </div>
                                    {!notif.enviada && (
                                        <button
                                            onClick={() => markNotificationAsRead(notif.id)}
                                            className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
                                        >
                                            Marcar como leída
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}