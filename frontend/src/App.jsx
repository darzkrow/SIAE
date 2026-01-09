import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Sidebar from './components/Sidebar'

// Login siempre cargado (crítico)
import Login from './pages/Login'

// Lazy loading de páginas para optimizar primera carga
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Movimientos = lazy(() => import('./pages/Movimientos'))
const Stock = lazy(() => import('./pages/Stock'))
const Articulos = lazy(() => import('./pages/Articulos'))
const Reportes = lazy(() => import('./pages/Reportes'))
const Alertas = lazy(() => import('./pages/Alertas'))
const Usuarios = lazy(() => import('./pages/Usuarios'))
const Administracion = lazy(() => import('./pages/Administracion'))

// Loading component
const LoadingFallback = () => (
    <div className="flex items-center justify-center h-screen">
        <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
    </div>
)

const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <LoadingFallback />;
    if (!user) return <Navigate to="/login" />;
    return <Sidebar>{children}</Sidebar>;
};

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Suspense fallback={<LoadingFallback />}>
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
                </Suspense>
            </AuthProvider>
        </BrowserRouter>
    )
}

export default App
