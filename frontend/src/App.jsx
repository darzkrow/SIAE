import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { AdminLTELayout, NotificationProvider } from './components/adminlte'

// Import dark theme styles
import './styles/dark-theme.css'

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
const Compras = lazy(() => import('./pages/Compras'))
const OrdenDetalle = lazy(() => import('./pages/OrdenDetalle'))
const Catalogo = lazy(() => import('./pages/Catalogo'))
const Geografia = lazy(() => import('./pages/Geografia'))
const Auditoria = lazy(() => import('./pages/Auditoria'))
const NotificacionesList = lazy(() => import('./pages/NotificacionesList'))
const EndpointTest = lazy(() => import('./pages/EndpointTest'))

// Error pages
import { Error400, Error401, Error403, Error404, Error500 } from './pages/ErrorPage'

// Loading component
const LoadingFallback = () => (
    <div className="flex items-center justify-center h-screen">
        <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
    </div>
)

const ProtectedRoute = ({ children, title }) => {
    const { user, loading } = useAuth();
    if (loading) return <LoadingFallback />;
    if (!user) return <Navigate to="/login" />;
    return (
        <AdminLTELayout title={title}>
            {children}
        </AdminLTELayout>
    );
};

function App() {
    return (
        <BrowserRouter>
            <ThemeProvider>
                <AuthProvider>
                    <NotificationProvider>
                        <Suspense fallback={<LoadingFallback />}>
                            <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route path="/" element={
                                <ProtectedRoute title="Dashboard">
                                    <Dashboard />
                                </ProtectedRoute>
                            } />
                            <Route path="/movimientos" element={
                                <ProtectedRoute title="Movimientos de Inventario">
                                    <Movimientos />
                                </ProtectedRoute>
                            } />
                            <Route path="/stock" element={
                                <ProtectedRoute title="Gestión de Stock">
                                    <Stock />
                                </ProtectedRoute>
                            } />
                            <Route path="/articulos" element={
                                <ProtectedRoute title="Artículos">
                                    <Articulos />
                                </ProtectedRoute>
                            } />
                            <Route path="/alertas" element={
                                <ProtectedRoute title="Alertas del Sistema">
                                    <Alertas />
                                </ProtectedRoute>
                            } />
                            <Route path="/reportes" element={
                                <ProtectedRoute title="Reportes y Estadísticas">
                                    <Reportes />
                                </ProtectedRoute>
                            } />
                            <Route path="/usuarios" element={
                                <ProtectedRoute title="Gestión de Usuarios">
                                    <Usuarios />
                                </ProtectedRoute>
                            } />
                            <Route path="/administracion" element={
                                <ProtectedRoute title="Administración del Sistema">
                                    <Administracion />
                                </ProtectedRoute>
                            } />
                            <Route path="/compras" element={
                                <ProtectedRoute title="Órdenes de Compra">
                                    <Compras />
                                </ProtectedRoute>
                            } />
                            <Route path="/compras/orden/:id" element={
                                <ProtectedRoute title="Detalle de Orden">
                                    <OrdenDetalle />
                                </ProtectedRoute>
                            } />

                            {/* Nuevas secciones */}
                            <Route path="/catalogo" element={
                                <ProtectedRoute title="Catálogo de Productos">
                                    <Catalogo />
                                </ProtectedRoute>
                            } />
                            <Route path="/geografia" element={
                                <ProtectedRoute title="Gestión Geográfica">
                                    <Geografia />
                                </ProtectedRoute>
                            } />
                            <Route path="/auditoria" element={
                                <ProtectedRoute title="Auditoría del Sistema">
                                    <Auditoria />
                                </ProtectedRoute>
                            } />
                            <Route path="/notificaciones" element={
                                <ProtectedRoute title="Centro de Notificaciones">
                                    <NotificacionesList />
                                </ProtectedRoute>
                            } />

                            {/* Test Page - Solo para desarrollo */}
                            <Route path="/test-endpoints" element={
                                <ProtectedRoute title="Prueba de Endpoints">
                                    <EndpointTest />
                                </ProtectedRoute>
                            } />

                            {/* Error Pages */}
                            <Route path="/error/400" element={<Error400 />} />
                            <Route path="/error/401" element={<Error401 />} />
                            <Route path="/error/403" element={<Error403 />} />
                            <Route path="/error/404" element={<Error404 />} />
                            <Route path="/error/500" element={<Error500 />} />

                            {/* Catch all - 404 */}
                            <Route path="*" element={<Error404 />} />
                        </Routes>
                    </Suspense>
                </NotificationProvider>
            </AuthProvider>
        </ThemeProvider>
        </BrowserRouter>
    )
}

export default App
