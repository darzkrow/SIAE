import React, { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { useNotifications } from './AdminLTENotification'
import ThemeSettings from '../ThemeSettings'
import UserAvatar from '../UserAvatar'
import { 
  Menu, 
  Search, 
  Bell, 
  User, 
  Settings, 
  LogOut,
  Sun,
  Moon,
  Maximize,
  MessageSquare,
  Palette
} from 'lucide-react'

/**
 * AdminLTE3 Navbar Component
 * Provides top navigation with search, notifications, and user menu
 */
const AdminLTENavbar = ({ onToggleSidebar, onToggleTheme, theme }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showThemeSettings, setShowThemeSettings] = useState(false)
  const { user, logout } = useAuth()
  const { notifications } = useNotifications()

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      // Implement global search functionality
      console.log('Searching for:', searchQuery)
    }
  }

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <nav className="main-header navbar navbar-expand navbar-white navbar-light">
      <ul className="navbar-nav">
        <li className="nav-item">
          <button 
            className="nav-link btn btn-link" 
            onClick={onToggleSidebar}
            data-widget="pushmenu"
          >
            <Menu size={16} />
          </button>
        </li>
        <li className="nav-item d-none d-sm-inline-block">
          <a href="/" className="nav-link">Inicio</a>
        </li>
        <li className="nav-item d-none d-sm-inline-block">
          <a href="/contacto" className="nav-link">Contacto</a>
        </li>
      </ul>

      <ul className="navbar-nav ml-auto">
        {/* Search */}
        <li className="nav-item">
          <button 
            className="nav-link btn btn-link" 
            data-widget="navbar-search"
            onClick={() => document.querySelector('.navbar-search-block').classList.toggle('d-none')}
          >
            <Search size={16} />
          </button>
          <div className="navbar-search-block d-none">
            <form className="form-inline" onSubmit={handleSearch}>
              <div className="input-group input-group-sm">
                <input 
                  className="form-control form-control-navbar" 
                  type="search" 
                  placeholder="Buscar..." 
                  aria-label="Search"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <div className="input-group-append">
                  <button className="btn btn-navbar" type="submit">
                    <Search size={16} />
                  </button>
                  <button 
                    className="btn btn-navbar" 
                    type="button"
                    onClick={() => document.querySelector('.navbar-search-block').classList.add('d-none')}
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </li>

        {/* Messages */}
        <li className="nav-item dropdown">
          <button className="nav-link btn btn-link" data-toggle="dropdown">
            <MessageSquare size={16} />
            <span className="badge badge-danger navbar-badge">3</span>
          </button>
          <div className="dropdown-menu dropdown-menu-lg dropdown-menu-right">
            <a href="#" className="dropdown-item">
              <div className="media">
                <UserAvatar 
                  username="Juan Pérez" 
                  size={50} 
                  className="mr-3"
                />
                <div className="media-body">
                  <h3 className="dropdown-item-title">
                    Juan Pérez
                    <span className="float-right text-sm text-danger"><i className="fas fa-star"></i></span>
                  </h3>
                  <p className="text-sm">Consulta sobre inventario...</p>
                  <p className="text-sm text-muted"><i className="far fa-clock mr-1"></i> 4 horas</p>
                </div>
              </div>
            </a>
            <div className="dropdown-divider"></div>
            <a href="#" className="dropdown-item dropdown-footer">Ver todos los mensajes</a>
          </div>
        </li>

        {/* Notifications */}
        <li className="nav-item dropdown">
          <button 
            className="nav-link btn btn-link" 
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell size={16} />
            <span className="badge badge-warning navbar-badge">
              {notifications.filter(n => !n.read).length}
            </span>
          </button>
          {showNotifications && (
            <div className="dropdown-menu dropdown-menu-lg dropdown-menu-right show" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              <span className="dropdown-item dropdown-header">
                {notifications.filter(n => !n.read).length} Notificaciones Nuevas
              </span>
              <div className="dropdown-divider"></div>
              {notifications.length === 0 ? (
                <div className="dropdown-item text-center text-muted py-3">
                  <Bell size={24} className="mb-2 text-muted" />
                  <p className="mb-0">No hay notificaciones</p>
                </div>
              ) : (
                <>
                  {notifications.slice(0, 5).map(notification => (
                    <div key={notification.id}>
                      <a href="#" className="dropdown-item d-flex align-items-start py-2">
                        <div className="mr-2 mt-1">
                          {notification.type === 'info' && <i className="fas fa-info-circle text-info"></i>}
                          {notification.type === 'warning' && <i className="fas fa-exclamation-triangle text-warning"></i>}
                          {notification.type === 'success' && <i className="fas fa-check-circle text-success"></i>}
                          {notification.type === 'error' && <i className="fas fa-times-circle text-danger"></i>}
                        </div>
                        <div className="flex-grow-1">
                          <h6 className="dropdown-item-title mb-1" style={{ fontSize: '13px' }}>
                            {notification.title}
                          </h6>
                          <p className="text-sm mb-1" style={{ fontSize: '12px' }}>
                            {notification.message}
                          </p>
                          <p className="text-sm text-muted mb-0" style={{ fontSize: '11px' }}>
                            <i className="far fa-clock mr-1"></i>
                            Hace {Math.floor((Date.now() - notification.id) / 60000)} min
                          </p>
                        </div>
                      </a>
                      <div className="dropdown-divider"></div>
                    </div>
                  ))}
                  <a href="/notificaciones" className="dropdown-item dropdown-footer">
                    Ver todas las notificaciones
                  </a>
                </>
              )}
            </div>
          )}
        </li>

        {/* Theme Toggle */}
        <li className="nav-item">
          <button 
            className="nav-link btn btn-link" 
            onClick={onToggleTheme}
            title={`Cambiar a tema ${theme === 'light' ? 'oscuro' : 'claro'}`}
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>
        </li>

        {/* Theme Settings */}
        <li className="nav-item">
          <button 
            className="nav-link btn btn-link" 
            onClick={() => setShowThemeSettings(true)}
            title="Configuración de tema"
          >
            <Palette size={16} />
          </button>
        </li>

        {/* Fullscreen */}
        <li className="nav-item">
          <button 
            className="nav-link btn btn-link" 
            onClick={toggleFullscreen}
            title="Pantalla completa"
          >
            <Maximize size={16} />
          </button>
        </li>

        {/* User Menu */}
        <li className="nav-item dropdown">
          <button 
            className="nav-link btn btn-link" 
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <User size={16} />
          </button>
          {showUserMenu && (
            <div className="dropdown-menu dropdown-menu-lg dropdown-menu-right show">
              <div className="dropdown-header">
                <div className="d-flex align-items-center">
                  <UserAvatar 
                    username={user?.username} 
                    size={30} 
                    className="mr-2"
                  />
                  <div>
                    <div>{user?.username || 'Usuario'}</div>
                    <small className="text-muted">
                      {user?.is_admin || user?.role === 'ADMIN' ? 'Administrador' : 'Operador'}
                    </small>
                  </div>
                </div>
              </div>
              <div className="dropdown-divider"></div>
              <a href="/perfil" className="dropdown-item">
                <User size={16} className="mr-2" />
                Mi Perfil
              </a>
              <a href="/configuracion" className="dropdown-item">
                <Settings size={16} className="mr-2" />
                Configuración
              </a>
              <div className="dropdown-divider"></div>
              <button onClick={handleLogout} className="dropdown-item">
                <LogOut size={16} className="mr-2" />
                Cerrar Sesión
              </button>
            </div>
          )}
        </li>
      </ul>
      
      {/* Theme Settings Modal */}
      <ThemeSettings 
        isOpen={showThemeSettings} 
        onClose={() => setShowThemeSettings(false)} 
      />
    </nav>
  )
}

export default AdminLTENavbar