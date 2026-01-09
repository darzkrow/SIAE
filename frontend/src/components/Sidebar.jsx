import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Home, Package, Droplets, Activity, BarChart3, AlertCircle, Users, Settings, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ children }) {
    const [isOpen, setIsOpen] = useState(true);
    const location = useLocation();
    const { user, logout } = useAuth();

    const menuItems = [
        { path: '/', label: 'Dashboard', icon: Home },
        { path: '/movimientos', label: 'Movimientos', icon: Package },
        { path: '/stock', label: 'Stock', icon: Droplets },
        { path: '/articulos', label: 'Artículos', icon: Activity },
        { path: '/alertas', label: 'Alertas', icon: AlertCircle },
        { path: '/reportes', label: 'Reportes', icon: BarChart3 },
    ];

    // Solo mostrar opciones admin si es admin
    const adminItems = user?.role === 'ADMIN' ? [
        { path: '/usuarios', label: 'Usuarios', icon: Users },
        { path: '/administracion', label: 'Administración', icon: Settings }
    ] : [];
    const allMenuItems = [...menuItems, ...adminItems];

    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <div className={`${isOpen ? 'w-64' : 'w-20'} bg-gray-900 text-white transition-all duration-300 flex flex-col fixed h-screen z-50`}>
                {/* Header */}
                <div className="p-4 border-b border-gray-700 flex items-center justify-between">
                    {isOpen && <h1 className="text-xl font-bold">GSIH</h1>}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="p-2 hover:bg-gray-800 rounded-lg transition"
                    >
                        {isOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                {/* Menu Items */}
                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    {allMenuItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                                    isActive(item.path)
                                        ? 'bg-blue-600 text-white'
                                        : 'text-gray-300 hover:bg-gray-800'
                                }`}
                                title={!isOpen ? item.label : ''}
                            >
                                <Icon size={20} />
                                {isOpen && <span>{item.label}</span>}
                            </Link>
                        );
                    })}
                </nav>

                {/* User Info */}
                <div className="p-4 border-t border-gray-700">
                    {isOpen && (
                        <div className="mb-4">
                            <p className="text-sm text-gray-400">Usuario</p>
                            <p className="font-semibold truncate">{user?.username}</p>
                            <p className="text-xs text-gray-400">{user?.role === 'ADMIN' ? 'Administrador' : 'Operador'}</p>
                            {user?.sucursal && <p className="text-xs text-gray-400 mt-1">{user.sucursal.nombre}</p>}
                        </div>
                    )}
                    <button
                        onClick={logout}
                        className="w-full flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition text-sm"
                    >
                        <LogOut size={18} />
                        {isOpen && <span>Salir</span>}
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className={`${isOpen ? 'ml-64' : 'ml-20'} flex-1 flex flex-col transition-all duration-300`}>
                {/* Top Bar */}
                <div className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-800">
                        {allMenuItems.find(item => isActive(item.path))?.label || 'Dashboard'}
                    </h2>
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-auto p-6">
                    {children}
                </div>
            </div>
        </div>
    );
}