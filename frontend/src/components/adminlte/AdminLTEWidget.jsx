import React from 'react'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  RefreshCw,
  MoreVertical,
  Maximize2
} from 'lucide-react'

/**
 * AdminLTE3 Dashboard Widget Component
 * Provides various widget types for dashboard display
 */
const AdminLTEWidget = ({
  type = 'metric',
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'primary',
  trend = null, // { direction: 'up'|'down'|'neutral', value: '12%', period: 'vs last month' }
  data = null,
  refreshInterval = null,
  onRefresh = null,
  onMaximize = null,
  className = '',
  children
}) => {
  const colorClasses = {
    primary: 'bg-primary',
    secondary: 'bg-secondary',
    success: 'bg-success',
    info: 'bg-info',
    warning: 'bg-warning',
    danger: 'bg-danger',
    light: 'bg-light',
    dark: 'bg-dark'
  }

  const renderTrendIcon = () => {
    if (!trend) return null
    
    switch (trend.direction) {
      case 'up':
        return <TrendingUp size={16} className="text-success" />
      case 'down':
        return <TrendingDown size={16} className="text-danger" />
      default:
        return <Minus size={16} className="text-muted" />
    }
  }

  const renderMetricWidget = () => (
    <div className={`small-box ${colorClasses[color]} ${className}`}>
      <div className="inner">
        <h3>{value}</h3>
        <p>{title}</p>
        {subtitle && <small className="text-white-50">{subtitle}</small>}
      </div>
      <div className="icon">
        {Icon && <Icon size={48} className="opacity-75" />}
      </div>
      {trend && (
        <div className="small-box-footer d-flex align-items-center justify-content-between">
          <div className="d-flex align-items-center">
            {renderTrendIcon()}
            <span className="ml-1">{trend.value} {trend.period}</span>
          </div>
        </div>
      )}
    </div>
  )

  const renderCardWidget = () => (
    <div className={`card ${className}`}>
      <div className="card-header">
        <h3 className="card-title">{title}</h3>
        <div className="card-tools">
          {onRefresh && (
            <button 
              type="button" 
              className="btn btn-tool"
              onClick={onRefresh}
              title="Actualizar"
            >
              <RefreshCw size={14} />
            </button>
          )}
          {onMaximize && (
            <button 
              type="button" 
              className="btn btn-tool"
              onClick={onMaximize}
              title="Maximizar"
            >
              <Maximize2 size={14} />
            </button>
          )}
          <button 
            type="button" 
            className="btn btn-tool" 
            data-card-widget="dropdown"
          >
            <MoreVertical size={14} />
          </button>
        </div>
      </div>
      <div className="card-body">
        {type === 'chart' && data ? (
          <div className="chart-container" style={{ height: '300px' }}>
            {/* Chart will be rendered here by parent component */}
            {children}
          </div>
        ) : (
          <>
            {value && (
              <div className="d-flex align-items-center mb-3">
                {Icon && (
                  <div className={`icon-circle ${colorClasses[color]} text-white mr-3`}>
                    <Icon size={24} />
                  </div>
                )}
                <div>
                  <h2 className="mb-0">{value}</h2>
                  {subtitle && <small className="text-muted">{subtitle}</small>}
                </div>
              </div>
            )}
            {trend && (
              <div className="d-flex align-items-center">
                {renderTrendIcon()}
                <span className="ml-2 text-sm">
                  <strong>{trend.value}</strong> {trend.period}
                </span>
              </div>
            )}
            {children}
          </>
        )}
      </div>
    </div>
  )

  const renderTableWidget = () => (
    <div className={`card ${className}`}>
      <div className="card-header">
        <h3 className="card-title">{title}</h3>
        <div className="card-tools">
          {onRefresh && (
            <button 
              type="button" 
              className="btn btn-tool"
              onClick={onRefresh}
            >
              <RefreshCw size={14} />
            </button>
          )}
        </div>
      </div>
      <div className="card-body p-0">
        <div className="table-responsive">
          {children}
        </div>
      </div>
    </div>
  )

  const renderProgressWidget = () => (
    <div className={`card ${className}`}>
      <div className="card-header">
        <h3 className="card-title">{title}</h3>
      </div>
      <div className="card-body">
        <div className="progress-group">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <span>{subtitle}</span>
            <span className="font-weight-bold">{value}</span>
          </div>
          <div className="progress progress-sm">
            <div 
              className={`progress-bar ${colorClasses[color]}`}
              style={{ width: value }}
            ></div>
          </div>
        </div>
        {children}
      </div>
    </div>
  )

  const renderInfoBoxWidget = () => (
    <div className={`info-box ${className}`}>
      <span className={`info-box-icon ${colorClasses[color]}`}>
        {Icon && <Icon size={24} />}
      </span>
      <div className="info-box-content">
        <span className="info-box-text">{title}</span>
        <span className="info-box-number">{value}</span>
        {trend && (
          <div className="progress">
            <div 
              className="progress-bar" 
              style={{ width: trend.value }}
            ></div>
          </div>
        )}
        {subtitle && (
          <span className="progress-description">{subtitle}</span>
        )}
      </div>
    </div>
  )

  // Render based on widget type
  switch (type) {
    case 'metric':
      return renderMetricWidget()
    case 'card':
      return renderCardWidget()
    case 'chart':
      return renderCardWidget()
    case 'table':
      return renderTableWidget()
    case 'progress':
      return renderProgressWidget()
    case 'info-box':
      return renderInfoBoxWidget()
    default:
      return renderCardWidget()
  }
}

// Additional CSS for icon circles
const additionalStyles = `
.icon-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-container {
  position: relative;
}

.progress-group {
  margin-bottom: 1rem;
}

.progress-group:last-child {
  margin-bottom: 0;
}
`

// Inject styles if not already present
if (!document.querySelector('#adminlte-widget-styles')) {
  const styleSheet = document.createElement('style')
  styleSheet.id = 'adminlte-widget-styles'
  styleSheet.textContent = additionalStyles
  document.head.appendChild(styleSheet)
}

export default AdminLTEWidget