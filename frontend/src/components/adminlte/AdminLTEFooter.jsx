import React from 'react'

/**
 * AdminLTE3 Footer Component
 * Provides footer with copyright and version information
 */
const AdminLTEFooter = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="main-footer">
      <strong>
        Copyright &copy; {currentYear} 
        <a href="#"> GSIH System</a>.
      </strong>
      Todos los derechos reservados.
      <div className="float-right d-none d-sm-inline-block">
        <b>Versión</b> 2.0.0
      </div>
    </footer>
  )
}

export default AdminLTEFooter