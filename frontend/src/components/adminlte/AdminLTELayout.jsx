import React, { useEffect, useState } from 'react'
import { adminLTEConfig } from '../../config/adminlte'
import { useTheme } from '../../context/ThemeContext'
import AdminLTESidebar from './AdminLTESidebar'
import AdminLTENavbar from './AdminLTENavbar'
import AdminLTEFooter from './AdminLTEFooter'
import './adminlte.css'

/**
 * AdminLTE3 Base Layout Component
 * Provides the main layout structure with sidebar, navbar, and content area
 */
const AdminLTELayout = ({ children, title = 'GSIH System' }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(adminLTEConfig.sidebar.collapsed)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    // Set page title
    document.title = title
    
    // Add sidebar collapse class if needed
    if (sidebarCollapsed) {
      document.body.classList.add('sidebar-collapse')
    } else {
      document.body.classList.remove('sidebar-collapse')
    }

    return () => {
      // Cleanup classes on unmount (but preserve theme classes)
      document.body.classList.remove('sidebar-collapse')
    }
  }, [sidebarCollapsed, title])

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  return (
    <div className="wrapper">
      <AdminLTENavbar 
        onToggleSidebar={toggleSidebar}
        onToggleTheme={toggleTheme}
        theme={theme}
      />
      
      <AdminLTESidebar 
        collapsed={sidebarCollapsed}
        theme={theme}
      />

      <div className="content-wrapper">
        <div className="content-header">
          <div className="container-fluid">
            <div className="row mb-2">
              <div className="col-sm-6">
                <h1 className="m-0">{title}</h1>
              </div>
              <div className="col-sm-6">
                <ol className="breadcrumb float-sm-right">
                  <li className="breadcrumb-item">
                    <a href="/">Inicio</a>
                  </li>
                  <li className="breadcrumb-item active">{title}</li>
                </ol>
              </div>
            </div>
          </div>
        </div>

        <section className="content">
          <div className="container-fluid">
            {children}
          </div>
        </section>
      </div>

      <AdminLTEFooter />
    </div>
  )
}

export default AdminLTELayout