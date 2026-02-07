import { useState, useEffect } from 'react';
import { TaskService } from '../services/taskService';
import { AdminLTEWidget, useNotifications } from '../components/adminlte';
import { ClipboardList, Plus, MoreHorizontal, Calendar, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Swal from 'sweetalert2';

export default function Tasks() {
    const { user } = useAuth();
    const { addNotification } = useNotifications();
    const [tasks, setTasks] = useState([]);
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [tasksRes, colsRes] = await Promise.all([
                TaskService.tareas.getAll(),
                TaskService.columnas.getAll()
            ]);
            setTasks(tasksRes.data.results || tasksRes.data);
            setColumns(colsRes.data.results || colsRes.data);
        } catch (e) {
            addNotification({ type: 'error', message: 'Error cargando tareas' });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center p-5">Cargando tablero...</div>;

    // Group tasks by column
    const tasksByColumn = columns.reduce((acc, col) => {
        acc[col.id] = tasks.filter(t => t.columna_kanban === col.id);
        return acc;
    }, {});

    // If no columns, show list
    if (columns.length === 0) {
        return (
            <div>
                <h3>Tareas</h3>
                <p>No hay columnas de Kanban configuradas.</p>
                <ul>
                    {tasks.map(t => <li key={t.id}>{t.titulo}</li>)}
                </ul>
            </div>
        )
    }

    return (
        <div className="h-100">
            <div className="row mb-3">
                <div className="col-12 d-flex justify-content-between align-items-center">
                    <div>
                        <h1 className="h3 mb-0">Tablero de Tareas</h1>
                        <p className="text-muted">Gestión de actividades y órdenes de trabajo</p>
                    </div>
                    <button className="btn btn-primary">
                        <Plus size={16} className="mr-2" /> Nueva Tarea
                    </button>
                </div>
            </div>

            <div className="d-flex overflow-auto pb-4" style={{ gap: '1rem', minHeight: 'calc(100vh - 200px)' }}>
                {columns.sort((a, b) => a.orden - b.orden).map(col => (
                    <div key={col.id} className="card bg-light" style={{ minWidth: '300px', maxWidth: '300px' }}>
                        <div className="card-header border-bottom-0 font-weight-bold d-flex justify-content-between align-items-center">
                            {col.nombre}
                            <span className="badge badge-secondary">{tasksByColumn[col.id]?.length || 0}</span>
                        </div>
                        <div className="card-body p-2 d-flex flex-column" style={{ gap: '0.5rem', overflowY: 'auto' }}>
                            {tasksByColumn[col.id]?.map(task => (
                                <div key={task.id} className="card shadow-sm mb-0">
                                    <div className="card-body p-3">
                                        <h6 className="card-title mb-1 font-weight-bold">{task.titulo}</h6>
                                        <p className="card-text text-muted small mb-2">
                                            {task.descripcion?.substring(0, 60)}...
                                        </p>
                                        <div className="d-flex justify-content-between align-items-center mt-2">
                                            <small className="text-muted d-flex align-items-center">
                                                <Calendar size={12} className="mr-1" />
                                                {task.fecha_vencimiento ? new Date(task.fecha_vencimiento).toLocaleDateString() : 'S/F'}
                                            </small>
                                            {task.prioridad && (
                                                <span className={`badge badge-${getPriorityColor(task.prioridad)}`}>
                                                    {task.prioridad}
                                                </span>
                                            )}
                                        </div>
                                        <div className="mt-2 d-flex align-items-center">
                                            <div className="user-block mb-0">
                                                <span className="username ml-0 text-xs text-primary">
                                                    <User size={12} className="mr-1" />
                                                    {task.asignado_a_nombre || 'Sin asignar'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {(!tasksByColumn[col.id] || tasksByColumn[col.id].length === 0) && (
                                <div className="text-center text-muted py-4 small border border-dashed rounded">
                                    Sin tareas
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function getPriorityColor(priority) {
    switch (priority) {
        case 'ALTA': return 'danger';
        case 'MEDIA': return 'warning';
        case 'BAJA': return 'info';
        default: return 'secondary';
    }
}
