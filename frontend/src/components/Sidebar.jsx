import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    Menu,
    X,
    Home,
    Package,
    Droplets,
    Activity,
    BarChart3,
    AlertCircle,
    Users,
    Settings,
    LogOut,
    BookOpen,
    MapPin,
    Bell,
    Shield
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ children }) {
    const [isOpen, setIsOpen] = useState(true);
    const location = useLocation();
    const { user, logout } = useAuth();

    const sections = [
        {
            title: 'General',
            items: [
                { path: '/', label: 'Dashboard', icon: Home },
                { path: '/reportes', label: 'Reportes', icon: BarChart3 },
            ],
        },
        {
            title: 'Inventario',
            items: [
                { path: '/movimientos', label: 'Movimientos', icon: Package },
                { path: '/stock', label: 'Stock', icon: Droplets },
                { path: '/articulos', label: 'Artículos', icon: Activity },
            ],
        },
        {
            title: 'Compras',
            items: [
                { path: '/compras', label: 'Órdenes de compra', icon: Package },
            ],
        },
        {
            title: 'Catálogo',
            items: [
                { path: '/catalogo', label: 'Catálogo', icon: BookOpen },
            ],
        },
        {
            title: 'Geografía',
            items: [
                { path: '/geografia', label: 'Geografía', icon: MapPin },
            ],
        },
        {
            title: 'Notificaciones',
            items: [
                { path: '/alertas', label: 'Alertas', icon: AlertCircle },
                { path: '/notificaciones', label: 'Notificaciones', icon: Bell },
            ],
        },
        {
            title: 'Auditoría',
            items: [
                { path: '/auditoria', label: 'Logs', icon: Shield },
            ],
        },
    ];

    // Solo mostrar opciones admin si es admin
    if (user?.is_admin) {
        sections.push({
            title: 'Administración',
            items: [
                { path: '/usuarios', label: 'Usuarios', icon: Users },
                { path: '/administracion', label: 'Administración', icon: Settings },
            ],
        });
    }

    const allMenuItems = sections.flatMap(s => s.items);

    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <div className={`${isOpen ? 'w-72' : 'w-20'} bg-gray-900 text-white transition-all duration-300 flex flex-col fixed h-screen z-50`}>
                {/* Header */}
                <div className="p-4 border-b border-gray-700 flex items-center justify-between">
                    {isOpen && <h1 className="text-xl font-bold tracking-wide">GSIH</h1>}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="p-2 hover:bg-gray-800 rounded-lg transition"
                    >
                        {isOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                {/* Menu Items */}
                <nav className="flex-1 p-3 space-y-4 overflow-y-auto">
                    {sections.map((section) => (
                        <div key={section.title}>
                            {isOpen && (
                                <div className="px-3 mb-2 text-xs uppercase tracking-wider text-gray-400">
                                    {section.title}
                                </div>
                            )}
                            <div className="space-y-1">
                                {section.items.map((item) => {
                                    const Icon = item.icon;
                                    const active = isActive(item.path);
                                    return (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            className={`flex items-center gap-3 px-4 py-2 rounded-lg transition ${
                                                active ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-300 hover:bg-gray-800'
                                            }`}
                                            title={!isOpen ? item.label : ''}
                                        >
                                            <Icon size={18} />
                                            {isOpen && <span className="text-sm">{item.label}</span>}
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </nav>

                {/* User Info */}
                <div className="p-4 border-t border-gray-700">
                    {isOpen && (
                        <div className="mb-4">
                            <p className="text-sm text-gray-400">Usuario</p>
                            <p className="font-semibold truncate">{user?.username}</p>
                            <p className="text-xs text-gray-400">{user?.is_admin ? 'Administrador' : 'Operador'}</p>
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
            <div className={`${isOpen ? 'ml-72' : 'ml-20'} flex-1 flex flex-col transition-all duration-300`}>
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