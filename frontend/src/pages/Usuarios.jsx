import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { InventoryService } from '../services/inventory.service';

export default function Usuarios() {
    const { user } = useAuth();
    const [usuarios, setUsuarios] = useState([]);
    const [sucursales, setSucursales] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        role: 'OPERADOR',
        sucursal: ''
    });

    useEffect(() => {
        // Solo ADMIN puede acceder
        if (user?.role !== 'ADMIN') {
            setError('No tienes permiso para acceder a esta sección');
            return;
        }
        fetchData();
    }, [user]);

    const fetchData = async () => {
        try {
            const [usersRes, sucRes] = await Promise.all([
                InventoryService.users.getAll(),
                InventoryService.sucursales.getAll()
            ]);

            setUsuarios(usersRes.data.results || usersRes.data);
            setSucursales(sucRes.data.results || sucRes.data);
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
            const payload = {
                username: formData.username,
                email: formData.email,
                first_name: formData.first_name,
                last_name: formData.last_name,
                role: formData.role,
                sucursal: formData.sucursal ? parseInt(formData.sucursal) : null
            };

            if (formData.password) {
                payload.password = formData.password;
            }

            if (editingId) {
                await InventoryService.users.update(editingId, payload);
                setSuccess("Usuario actualizado exitosamente");
            } else {
                if (!formData.password) {
                    setError("La contraseña es requerida para nuevos usuarios");
                    return;
                }
                await InventoryService.users.create(payload);
                setSuccess("Usuario creado exitosamente");
            }

            resetForm();
            fetchData();
        } catch (err) {
            console.error("Error saving user", err);
            setError(err.response?.data?.detail || "Error al guardar el usuario");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de que deseas eliminar este usuario?')) return;

        try {
            await InventoryService.users.delete(id);
            setSuccess("Usuario eliminado exitosamente");
            fetchData();
        } catch (err) {
            console.error("Error deleting user", err);
            setError("Error al eliminar el usuario");
        }
    };

    const handleEdit = (usuario) => {
        setEditingId(usuario.id);
        setFormData({
            username: usuario.username,
            email: usuario.email,
            first_name: usuario.first_name,
            last_name: usuario.last_name,
            password: '',
            role: usuario.role,
            sucursal: usuario.sucursal || ''
        });
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({
            username: '',
            email: '',
            first_name: '',
            last_name: '',
            password: '',
            role: 'OPERADOR',
            sucursal: ''
        });
        setEditingId(null);
        setShowForm(false);
    };

    if (user?.role !== 'ADMIN') {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                <Lock size={48} className="mx-auto text-red-600 mb-4" />
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
                    <p className="text-gray-600">Cargando usuarios...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Gestión de Usuarios</h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                    <Plus size={20} /> Nuevo Usuario
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
                        {editingId ? 'Editar Usuario' : 'Crear Nuevo Usuario'}
                    </h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Username */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Usuario *
                                </label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleFormChange}
                                    disabled={editingId}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                                    required
                                />
                            </div>

                            {/* Email */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email *
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            {/* Nombre */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre
                                </label>
                                <input
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            {/* Apellido */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Apellido
                                </label>
                                <input
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            {/* Contraseña */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Contraseña {editingId ? '(dejar en blanco para no cambiar)' : '*'}
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required={!editingId}
                                />
                            </div>

                            {/* Rol */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Rol *
                                </label>
                                <select
                                    name="role"
                                    value={formData.role}
                                    onChange={handleFormChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="ADMIN">Administrador</option>
                                    <option value="OPERADOR">Operador</option>
                                </select>
                            </div>

                            {/* Sucursal */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Sucursal {formData.role === 'OPERADOR' ? '*' : '(opcional)'}
                                </label>
                                <select
                                    name="sucursal"
                                    value={formData.sucursal}
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
                        </div>

                        <div className="flex gap-2">
                            <button
                                type="submit"
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                            >
                                {editingId ? 'Actualizar' : 'Crear'} Usuario
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

            {/* Tabla de Usuarios */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Usuario</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Nombre</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Rol</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Sucursal</th>
                                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {usuarios.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                                        No hay usuarios
                                    </td>
                                </tr>
                            ) : (
                                usuarios.map(usuario => (
                                    <tr key={usuario.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm font-medium">{usuario.username}</td>
                                        <td className="px-6 py-4 text-sm">{usuario.email}</td>
                                        <td className="px-6 py-4 text-sm">
                                            {usuario.first_name} {usuario.last_name}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${usuario.role === 'ADMIN'
                                                    ? 'bg-red-100 text-red-800'
                                                    : 'bg-blue-100 text-blue-800'
                                                }`}>
                                                {usuario.role === 'ADMIN' ? 'Administrador' : 'Operador'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            {usuario.sucursal ? usuario.sucursal.nombre : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm flex gap-2">
                                            <button
                                                onClick={() => handleEdit(usuario)}
                                                className="text-blue-600 hover:text-blue-800"
                                            >
                                                <Edit2 size={18} />
                                            </button>
                                            {usuario.id !== user.id && (
                                                <button
                                                    onClick={() => handleDelete(usuario.id)}
                                                    className="text-red-600 hover:text-red-800"
                                                >
                                                    <Trash2 size={18} />
                                                </button>
                                            )}
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