import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Filter } from 'lucide-react';
import Swal from 'sweetalert2';

export default function Movimientos() {
    const [movimientos, setMovimientos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [filtros, setFiltros] = useState({
        tipo_movimiento: '',
        acueducto_origen: '',
        acueducto_destino: ''
    });
    const [formData, setFormData] = useState({
        tipo_movimiento: 'ENTRADA',
        tuberia: '',
        equipo: '',
        acueducto_origen: '',
        acueducto_destino: '',
        cantidad: '',
        razon: ''
    });
    const [tuberias, setTuberias] = useState([]);
    const [equipos, setEquipos] = useState([]);
    const [acueductos, setAcueductos] = useState([]);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Cargar datos iniciales
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [movRes, tubRes, eqRes, acuRes] = await Promise.all([
                    axios.get(`${API_URL}/api/movimientos/`),
                    axios.get(`${API_URL}/api/tuberias/`),
                    axios.get(`${API_URL}/api/equipos/`),
                    axios.get(`${API_URL}/api/acueductos/`)
                ]);

                setMovimientos(movRes.data.results || movRes.data);
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

        fetchData();
    }, []);

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFiltros(prev => ({ ...prev, [name]: value }));
    };

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        // Validar que acueducto origen y destino sean diferentes en transferencias
        if (formData.tipo_movimiento === 'TRANSFERENCIA' && 
            formData.acueducto_origen && 
            formData.acueducto_destino && 
            formData.acueducto_origen === formData.acueducto_destino) {
            Swal.fire({
                icon: 'warning',
                title: 'Acueducto Inválido',
                text: 'El acueducto destino no puede ser igual al acueducto origen',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        try {
            const payload = {
                tipo_movimiento: formData.tipo_movimiento,
                cantidad: parseInt(formData.cantidad),
                razon: formData.razon,
                tuberia: formData.tuberia || null,
                equipo: formData.equipo || null,
                acueducto_origen: formData.acueducto_origen || null,
                acueducto_destino: formData.acueducto_destino || null
            };

            await axios.post(`${API_URL}/api/movimientos/`, payload);
            
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: 'Movimiento registrado exitosamente',
                confirmButtonColor: '#10b981',
                timer: 2000,
                timerProgressBar: true
            });
            
            setFormData({
                tipo_movimiento: 'ENTRADA',
                tuberia: '',
                equipo: '',
                acueducto_origen: '',
                acueducto_destino: '',
                cantidad: '',
                razon: ''
            });
            setShowForm(false);

            // Recargar movimientos
            const movRes = await axios.get(`${API_URL}/api/movimientos/`);
            setMovimientos(movRes.data.results || movRes.data);
        } catch (err) {
            console.error("Error creating movement", err);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: err.response?.data?.detail || err.response?.data?.cantidad?.[0] || 'Error al crear el movimiento',
                confirmButtonColor: '#ef4444'
            });
        }
    };

    const getTipoMovimientoColor = (tipo) => {
        switch (tipo) {
            case 'ENTRADA': return 'bg-green-100 text-green-800';
            case 'SALIDA': return 'bg-red-100 text-red-800';
            case 'TRANSFERENCIA': return 'bg-blue-100 text-blue-800';
            case 'AJUSTE': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando movimientos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Movimientos de Inventario</h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                    <Plus size={20} /> Nuevo Movimiento
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
                    <h2 className="text-xl font-bold mb-4">Registrar Nuevo Movimiento</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Tipo de Movimiento */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Tipo de Movimiento *
                                </label>
                                <select
                                    name="tipo_movimiento"
                                    value={formData.tipo_movimiento}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="ENTRADA">Entrada</option>
                                    <option value="SALIDA">Salida</option>
                                    <option value="TRANSFERENCIA">Transferencia</option>
                                    <option value="AJUSTE">Ajuste</option>
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
                                        <option value="">Seleccionar Tubería...</option>
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
                                        <option value="">Seleccionar Equipo...</option>
                                        {equipos.map(e => (
                                            <option key={e.id} value={e.id}>{e.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Cantidad */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Cantidad *
                                </label>
                                <input
                                    type="number"
                                    name="cantidad"
                                    value={formData.cantidad}
                                    onChange={handleFormChange}
                                    min="1"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            {/* Acueducto Origen */}
                            {(formData.tipo_movimiento === 'SALIDA' || formData.tipo_movimiento === 'TRANSFERENCIA' || formData.tipo_movimiento === 'AJUSTE') && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Acueducto Origen *
                                    </label>
                                    <select
                                        name="acueducto_origen"
                                        value={formData.acueducto_origen}
                                        onChange={handleFormChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="">Seleccionar...</option>
                                        {acueductos.map(a => (
                                            <option key={a.id} value={a.id}>{a.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {/* Acueducto Destino */}
                            {(formData.tipo_movimiento === 'ENTRADA' || formData.tipo_movimiento === 'TRANSFERENCIA') && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Acueducto Destino *
                                    </label>
                                    <select
                                        name="acueducto_destino"
                                        value={formData.acueducto_destino}
                                        onChange={handleFormChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="">Seleccionar...</option>
                                        {acueductos.map(a => (
                                            <option key={a.id} value={a.id}>{a.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {/* Razón */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Razón/Observaciones
                                </label>
                                <textarea
                                    name="razon"
                                    value={formData.razon}
                                    onChange={handleFormChange}
                                    rows="3"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <button
                                type="submit"
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                Registrar Movimiento
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition"
                            >
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Filtros */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center gap-2 mb-4">
                    <Filter size={20} />
                    <h3 className="font-bold">Filtros</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select
                        name="tipo_movimiento"
                        value={filtros.tipo_movimiento}
                        onChange={handleFilterChange}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">Todos los tipos</option>
                        <option value="ENTRADA">Entrada</option>
                        <option value="SALIDA">Salida</option>
                        <option value="TRANSFERENCIA">Transferencia</option>
                        <option value="AJUSTE">Ajuste</option>
                    </select>
                </div>
            </div>

            {/* Lista de Movimientos */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Tipo</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Artículo</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Cantidad</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Origen</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Destino</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Fecha</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {movimientos.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                        No hay movimientos registrados
                                    </td>
                                </tr>
                            ) : (
                                movimientos.map(mov => (
                                    <tr key={mov.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTipoMovimientoColor(mov.tipo_movimiento)}`}>
                                                {mov.tipo_movimiento}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm">{mov.articulo_nombre}</td>
                                        <td className="px-6 py-4 text-sm font-semibold">{mov.cantidad}</td>
                                        <td className="px-6 py-4 text-sm">{mov.acueducto_origen_nombre || '-'}</td>
                                        <td className="px-6 py-4 text-sm">{mov.acueducto_destino_nombre || '-'}</td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {new Date(mov.fecha_movimiento).toLocaleDateString()}
                                        </td>
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