import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import UserAvatar from '../UserAvatar'
import { 
  Home, 
  Package, 
  ShoppingCart, 
  Users, 
  BarChart3, 
  Settings, 
  Bell,
  FileText,
  MapPin,
  Shield
} from 'lucide-react'

/**
 * AdminLTE3 Sidebar Component
 * Provides navigation menu with AdminLTE3 styling
 */
const AdminLTESidebar = ({ collapsed, theme }) => {
  const location = useLocation()
  const { user } = useAuth()

  const menuItems = [
    {
      title: 'Dashboard',
      icon: Home,
      path: '/',
      badge: null
    },
    {
      title: 'Inventario',
      icon: Package,
      path: '/inventario',
      children: [
        { title: 'Artículos', path: '/articulos' },
        { title: 'Stock', path: '/stock' },
        { title: 'Movimientos', path: '/movimientos' }
      ]
    },
    {
      title: 'Compras',
      icon: ShoppingCart,
      path: '/compras',
      badge: { text: '3', color: 'warning' }
    },
    {
      title: 'Catálogo',
      icon: FileText,
      path: '/catalogo'
    },
    {
      title: 'Geografía',
      icon: MapPin,
      path: '/geografia'
    },
    {
      title: 'Reportes',
      icon: BarChart3,
      path: '/reportes'
    },
    {
      title: 'Notificaciones',
      icon: Bell,
      path: '/notificaciones',
      badge: { text: '5', color: 'danger' }
    }
  ]

  // Add admin-only menu items
  if (user?.is_admin || user?.role === 'ADMIN') {
    menuItems.push(
      {
        title: 'Usuarios',
        icon: Users,
        path: '/usuarios'
      },
      {
        title: 'Administración',
        icon: Settings,
        path: '/administracion',
        children: [
          { title: 'Configuración', path: '/configuracion' },
          { title: 'Permisos', path: '/permisos' },
          { title: 'Auditoría', path: '/auditoria' }
        ]
      }
    )
  }

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  const renderMenuItem = (item, index) => {
    const Icon = item.icon
    const hasChildren = item.children && item.children.length > 0
    const isItemActive = isActive(item.path)

    if (hasChildren) {
      return (
        <li key={index} className={`nav-item ${isItemActive ? 'menu-open' : ''}`}>
          <a href="#" className={`nav-link ${isItemActive ? 'active' : ''}`}>
            <Icon className="nav-icon" size={16} />
            <p>
              {item.title}
              <i className="right fas fa-angle-left"></i>
              {item.badge && (
                <span className={`badge badge-${item.badge.color} right`}>
                  {item.badge.text}
                </span>
              )}
            </p>
          </a>
          <ul className="nav nav-treeview">
            {item.children.map((child, childIndex) => (
              <li key={childIndex} className="nav-item">
                <Link 
                  to={child.path} 
                  className={`nav-link ${isActive(child.path) ? 'active' : ''}`}
                >
                  <i className="far fa-circle nav-icon"></i>
                  <p>{child.title}</p>
                </Link>
              </li>
            ))}
          </ul>
        </li>
      )
    }

    return (
      <li key={index} className="nav-item">
        <Link to={item.path} className={`nav-link ${isItemActive ? 'active' : ''}`}>
          <Icon className="nav-icon" size={16} />
          <p>
            {item.title}
            {item.badge && (
              <span className={`badge badge-${item.badge.color} right`}>
                {item.badge.text}
              </span>
            )}
          </p>
        </Link>
      </li>
    )
  }

  return (
    <aside className={`main-sidebar sidebar-${theme === 'dark' ? 'dark' : 'light'}-primary elevation-4`}>
      <Link to="/" className="brand-link">
        <div className="brand-image" style={{
          width: '33px',
          height: '33px',
          backgroundColor: '#1F2937',
          borderRadius: '50%',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '16px',
          fontWeight: 'bold',
          marginRight: '10px'
        }}>
          G
        </div>
        <span className="brand-text font-weight-light">GSIH System</span>
      </Link>

      <div className="sidebar">
        <div className="user-panel mt-3 pb-3 mb-3 d-flex">
          <div className="image">
            <UserAvatar 
              username={user?.username} 
              size={34} 
              className="elevation-2"
            />
          </div>
          <div className="info">
            <a href="#" className="d-block">
              {user?.username || 'Usuario'}
            </a>
            <small className="text-muted">
              {user?.is_admin || user?.role === 'ADMIN' ? 'Administrador' : 'Operador'}
            </small>
            {user?.sucursal && (
              <small className="d-block text-muted">
                {user.sucursal.nombre}
              </small>
            )}
          </div>
        </div>

        <div className="form-inline">
          <div className="input-group" data-widget="sidebar-search">
            <input 
              className="form-control form-control-sidebar" 
              type="search" 
              placeholder="Buscar..." 
              aria-label="Search"
            />
            <div className="input-group-append">
              <button className="btn btn-sidebar">
                <i className="fas fa-search fa-fw"></i>
              </button>
            </div>
          </div>
        </div>

        <nav className="mt-2">
          <ul className="nav nav-pills nav-sidebar flex-column" data-widget="treeview" role="menu" data-accordion="false">
            {menuItems.map(renderMenuItem)}
          </ul>
        </nav>
      </div>
    </aside>
  )
}

export default AdminLTESidebar