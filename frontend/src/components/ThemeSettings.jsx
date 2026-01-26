import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Monitor, Settings, Palette, Eye } from 'lucide-react';

const ThemeSettings = ({ isOpen, onClose }) => {
  const { theme, toggleTheme, setLightTheme, setDarkTheme } = useTheme();
  const [showAdvanced, setShowAdvanced] = useState(false);

  if (!isOpen) return null;

  const handleThemeChange = (newTheme) => {
    if (newTheme === 'light') {
      setLightTheme();
    } else if (newTheme === 'dark') {
      setDarkTheme();
    }
  };

  const handleEyeComfortToggle = () => {
    const body = document.body;
    if (body.classList.contains('high-contrast')) {
      body.classList.remove('high-contrast');
      localStorage.setItem('gsih-high-contrast', 'false');
    } else {
      body.classList.add('high-contrast');
      localStorage.setItem('gsih-high-contrast', 'true');
    }
  };

  return (
    <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              <Palette size={20} className="mr-2" />
              Configuración de Tema
            </h5>
            <button
              type="button"
              className="close"
              onClick={onClose}
              aria-label="Cerrar"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          
          <div className="modal-body">
            {/* Theme Selection */}
            <div className="mb-4">
              <h6 className="mb-3">
                <Settings size={16} className="mr-2" />
                Seleccionar Tema
              </h6>
              
              <div className="row">
                <div className="col-6">
                  <div 
                    className={`card cursor-pointer ${theme === 'light' ? 'border-primary' : ''}`}
                    onClick={() => handleThemeChange('light')}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="card-body text-center py-3">
                      <Sun size={24} className="mb-2 text-warning" />
                      <div className="font-weight-bold">Claro</div>
                      <small className="text-muted">Tema tradicional</small>
                    </div>
                  </div>
                </div>
                
                <div className="col-6">
                  <div 
                    className={`card cursor-pointer ${theme === 'dark' ? 'border-primary' : ''}`}
                    onClick={() => handleThemeChange('dark')}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="card-body text-center py-3">
                      <Moon size={24} className="mb-2 text-info" />
                      <div className="font-weight-bold">Oscuro</div>
                      <small className="text-muted">Reduce fatiga visual</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Eye Comfort Settings */}
            <div className="mb-4">
              <h6 className="mb-3">
                <Eye size={16} className="mr-2" />
                Comodidad Visual
              </h6>
              
              <div className="custom-control custom-switch">
                <input
                  type="checkbox"
                  className="custom-control-input"
                  id="highContrastSwitch"
                  onChange={handleEyeComfortToggle}
                  defaultChecked={localStorage.getItem('gsih-high-contrast') === 'true'}
                />
                <label className="custom-control-label" htmlFor="highContrastSwitch">
                  Alto Contraste
                </label>
                <small className="form-text text-muted">
                  Mejora la legibilidad con mayor contraste entre texto y fondo
                </small>
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="mb-3">
              <button
                type="button"
                className="btn btn-link p-0 text-decoration-none"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <Settings size={16} className="mr-2" />
                Configuración Avanzada
                <span className={`ml-2 ${showAdvanced ? 'rotate-180' : ''}`}>▼</span>
              </button>
            </div>

            {showAdvanced && (
              <div className="border-top pt-3">
                <div className="mb-3">
                  <label className="form-label">Persistencia de Configuración</label>
                  <div className="form-text text-muted mb-2">
                    Tu configuración de tema se guarda automáticamente en este navegador
                  </div>
                  <button
                    type="button"
                    className="btn btn-outline-danger btn-sm"
                    onClick={() => {
                      localStorage.removeItem('gsih-theme');
                      localStorage.removeItem('gsih-high-contrast');
                      window.location.reload();
                    }}
                  >
                    Restablecer Configuración
                  </button>
                </div>

                <div className="mb-3">
                  <label className="form-label">Información del Sistema</label>
                  <div className="form-text text-muted">
                    <strong>Tema actual:</strong> {theme === 'light' ? 'Claro' : 'Oscuro'}<br />
                    <strong>Alto contraste:</strong> {localStorage.getItem('gsih-high-contrast') === 'true' ? 'Activado' : 'Desactivado'}<br />
                    <strong>Soporte del navegador:</strong> {window.matchMedia('(prefers-color-scheme: dark)').matches ? 'Tema oscuro preferido' : 'Tema claro preferido'}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Cerrar
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                // Save any additional settings here
                onClose();
              }}
            >
              Guardar Configuración
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemeSettings;