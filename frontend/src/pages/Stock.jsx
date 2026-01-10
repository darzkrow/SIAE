import { useState, useEffect } from 'react';
import { InventoryService } from '../services/inventory.service';
import { Search, Package, Droplets, Activity, Wrench } from 'lucide-react';

export default function Stock() {
    const [activeTab, setActiveTab] = useState('chemical');
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const tabs = [
        { id: 'chemical', label: 'Químicos', icon: <Package size={18} /> },
        { id: 'pipe', label: 'Tuberías', icon: <Droplets size={18} /> },
        { id: 'pump', label: 'Bombas/Equipos', icon: <Activity size={18} /> },
        { id: 'accessory', label: 'Accesorios', icon: <Wrench size={18} /> },
    ];

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setItems([]);
            try {
                let res;
                switch (activeTab) {
                    case 'chemical':
                        res = await InventoryService.chemicals.getAll();
                        break;
                    case 'pipe':
                        res = await InventoryService.pipes.getAll();
                        break;
                    case 'pump':
                        res = await InventoryService.pumps.getAll();
                        break;
                    case 'accessory':
                        res = await InventoryService.accessories.getAll();
                        break;
                    default:
                        res = { data: [] };
                }
                setItems(res.data.results || res.data);
            } catch (err) {
                console.error("Error fetching stock data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [activeTab]);

    const filteredItems = items.filter(item => {
        const term = searchTerm.toLowerCase();
        return (
            (item.nombre && item.nombre.toLowerCase().includes(term)) ||
            (item.codigo && item.codigo.toLowerCase().includes(term)) ||
            (item.marca && item.marca.toLowerCase().includes(term))
        );
    });

    const getStockStatus = (cantidad) => {
        if (cantidad === 0 || cantidad === undefined) return { color: 'bg-red-100 text-red-800', label: 'Sin stock' };
        if (cantidad <= 5) return { color: 'bg-yellow-100 text-yellow-800', label: 'Bajo' };
        return { color: 'bg-green-100 text-green-800', label: 'Normal' };
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Inventario de Artículos</h1>
                <p className="text-gray-600 mt-2">Gestión de stock por categorías</p>
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow p-2 flex overflow-x-auto gap-2">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition whitespace-nowrap ${activeTab === tab.id
                                ? 'bg-blue-600 text-white font-medium'
                                : 'text-gray-600 hover:bg-gray-100'
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Search */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="relative">
                    <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Buscar por nombre, código o marca..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marca/Modelo</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock Total</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-8 text-center">
                                        <div className="flex justify-center">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                        </div>
                                    </td>
                                </tr>
                            ) : filteredItems.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                                        No se encontraron artículos
                                    </td>
                                </tr>
                            ) : (
                                filteredItems.map(item => {
                                    // Asumiendo que el backend devuelve un campo 'stock_actual' o 'cantidad'
                                    // Si no, mostramos '-'
                                    const stock = item.stock_actual ?? item.cantidad ?? 0;
                                    const status = getStockStatus(stock);

                                    return (
                                        <tr key={item.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {item.codigo || '-'}
                                            </td>
                                            <td className="px-6 py-4 text-sm font-medium text-gray-900">
                                                {item.nombre}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-500">
                                                {item.marca || '-'}
                                                {item.modelo ? ` / ${item.modelo}` : ''}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                                                {stock} {item.unidad_medida_nombre || ''}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${status.color}`}>
                                                    {status.label}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}