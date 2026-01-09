import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Movimientos from './pages/Movimientos'
import Stock from './pages/Stock'
import Articulos from './pages/Articulos'
import Reportes from './pages/Reportes'
import Alertas from './pages/Alertas'
import Usuarios from './pages/Usuarios'
import Administracion from './pages/Administracion'

const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="flex items-center justify-center h-screen">Cargando...</div>;
    if (!user) return <Navigate to="/login" />;
    return <Sidebar>{children}</Sidebar>;
};

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/movimientos" element={
                        <ProtectedRoute>
                            <Movimientos />
                        </ProtectedRoute>
                    } />
                    {/* Rutas para módulos (placeholder por ahora) */}
                    <Route path="/stock" element={
                        <ProtectedRoute>
                            <Stock />
                        </ProtectedRoute>
                    } />
                    <Route path="/articulos" element={
                        <ProtectedRoute>
                            <Articulos />
                        </ProtectedRoute>
                    } />
                    <Route path="/alertas" element={
                        <ProtectedRoute>
                            <Alertas />
                        </ProtectedRoute>
                    } />
                    <Route path="/reportes" element={
                        <ProtectedRoute>
                            <Reportes />
                        </ProtectedRoute>
                    } />
                    <Route path="/usuarios" element={
                        <ProtectedRoute>
                            <Usuarios />
                        </ProtectedRoute>
                    } />
                    <Route path="/administracion" element={
                        <ProtectedRoute>
                            <Administracion />
                        </ProtectedRoute>
                    } />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    )
}

export default App
