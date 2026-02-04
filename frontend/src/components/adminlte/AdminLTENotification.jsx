import React, { useState, useEffect, createContext, useContext } from 'react'
import { 
  CheckCircle, 
  AlertCircle, 
  Info, 
  AlertTriangle,
  X
} from 'lucide-react'

// Notification Context
const NotificationContext = createContext()

/**
 * Notification Provider Component
 * Manages global notification state
 */
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([])
  const [notificationHistory, setNotificationHistory] = useState(new Set())

  const addNotification = (notification) => {
    const id = Date.now() + Math.random()
    
    // Create a unique key for the notification to prevent duplicates
    const notificationKey = `${notification.type}-${notification.title}-${notification.message}`
    
    // Check if this notification was recently shown (within last 10 seconds)
    if (notificationHistory.has(notificationKey)) {
      console.log('Duplicate notification prevented:', notificationKey)
      return null
    }

    const newNotification = {
      id,
      type: 'info',
      title: '',
      message: '',
      duration: 5000,
      persistent: false,
      ...notification
    }

    setNotifications(prev => [...prev, newNotification])
    setNotificationHistory(prev => new Set([...prev, notificationKey]))

    // Auto remove non-persistent notifications
    if (!newNotification.persistent && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    // Clean notification history after 10 seconds (increased from 5)
    setTimeout(() => {
      setNotificationHistory(prev => {
        const newSet = new Set(prev)
        newSet.delete(notificationKey)
        return newSet
      })
    }, 10000)

    return id
  }

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  const clearAllNotifications = () => {
    setNotifications([])
    setNotificationHistory(new Set())
  }

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  )
}

/**
 * Hook to use notifications
 */
export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}

/**
 * Individual Notification Component
 */
const NotificationItem = ({ notification, onClose }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [isRemoving, setIsRemoving] = useState(false)

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 10)
    return () => clearTimeout(timer)
  }, [])

  const handleClose = () => {
    setIsRemoving(true)
    setTimeout(() => {
      onClose(notification.id)
    }, 300)
  }

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle size={18} className="text-success" />
      case 'error':
        return <AlertCircle size={18} className="text-danger" />
      case 'warning':
        return <AlertTriangle size={18} className="text-warning" />
      case 'info':
      default:
        return <Info size={18} className="text-info" />
    }
  }

  const getColorClasses = () => {
    switch (notification.type) {
      case 'success':
        return 'border-success bg-success'
      case 'error':
        return 'border-danger bg-danger'
      case 'warning':
        return 'border-warning bg-warning'
      case 'info':
      default:
        return 'border-info bg-info'
    }
  }

  return (
    <div 
      className={`notification-card ${getColorClasses()} ${isVisible && !isRemoving ? 'show' : ''}`}
      style={{
        marginBottom: '0.75rem',
        transform: isRemoving ? 'translateX(100%)' : 'translateX(0)',
        opacity: isRemoving ? 0 : 1,
        transition: 'all 0.3s ease-in-out',
        borderRadius: '8px',
        border: '1px solid',
        backgroundColor: 'white',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}
    >
      <div className="d-flex align-items-start p-3">
        <div className="mr-3 mt-1">
          {getIcon()}
        </div>
        <div className="flex-grow-1">
          {notification.title && (
            <h6 className="mb-1 font-weight-bold" style={{ fontSize: '14px' }}>
              {notification.title}
            </h6>
          )}
          <div style={{ fontSize: '13px', color: '#6c757d' }}>
            {notification.message}
          </div>
          {notification.actions && (
            <div className="mt-2">
              {notification.actions.map((action, index) => (
                <button
                  key={index}
                  type="button"
                  className={`btn btn-sm ${action.variant || 'btn-outline-secondary'} mr-2`}
                  onClick={() => {
                    action.onClick && action.onClick()
                    if (action.closeOnClick !== false) {
                      handleClose()
                    }
                  }}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
        <button
          type="button"
          className="btn btn-sm btn-link p-1"
          onClick={handleClose}
          aria-label="Cerrar"
          style={{ color: '#6c757d' }}
        >
          <X size={14} />
        </button>
      </div>
    </div>
  )
}

/**
 * Notification Container Component
 * Renders all active notifications
 */
const NotificationContainer = () => {
  const { notifications, removeNotification } = useNotifications()

  if (notifications.length === 0) {
    return null
  }

  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onClose={removeNotification}
        />
      ))}
    </div>
  )
}

/**
 * Toast Notification Component
 * For simple toast-style notifications
 */
export const Toast = ({ 
  show = false, 
  onClose, 
  type = 'info', 
  title, 
  message, 
  duration = 3000,
  position = 'top-right'
}) => {
  const [isVisible, setIsVisible] = useState(show)

  useEffect(() => {
    setIsVisible(show)
    
    if (show && duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(() => onClose && onClose(), 300)
      }, duration)
      
      return () => clearTimeout(timer)
    }
  }, [show, duration, onClose])

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'toast-top-left'
      case 'top-right':
        return 'toast-top-right'
      case 'bottom-left':
        return 'toast-bottom-left'
      case 'bottom-right':
        return 'toast-bottom-right'
      case 'top-center':
        return 'toast-top-center'
      case 'bottom-center':
        return 'toast-bottom-center'
      default:
        return 'toast-top-right'
    }
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle size={16} className="text-success" />
      case 'error':
        return <AlertCircle size={16} className="text-danger" />
      case 'warning':
        return <AlertTriangle size={16} className="text-warning" />
      case 'info':
      default:
        return <Info size={16} className="text-info" />
    }
  }

  if (!show && !isVisible) {
    return null
  }

  return (
    <div className={`toast-wrapper ${getPositionClasses()}`}>
      <div 
        className={`toast ${isVisible ? 'show' : ''}`} 
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
      >
        <div className="toast-header">
          {getIcon()}
          <strong className="mr-auto ml-2">{title}</strong>
          <button 
            type="button" 
            className="ml-2 mb-1 close" 
            onClick={() => {
              setIsVisible(false)
              setTimeout(() => onClose && onClose(), 300)
            }}
            aria-label="Cerrar"
          >
            <X size={14} />
          </button>
        </div>
        {message && (
          <div className="toast-body">
            {message}
          </div>
        )}
      </div>
    </div>
  )
}

// Additional CSS for notifications
const notificationStyles = `
.notification-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 1055;
  max-width: 380px;
  width: 100%;
  pointer-events: none;
}

.notification-card {
  pointer-events: auto;
  transform: translateX(100%);
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.notification-card.show {
  transform: translateX(0);
  opacity: 1;
}

.notification-card:hover {
  transform: translateX(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.toast-wrapper {
  position: fixed;
  z-index: 1055;
  pointer-events: none;
}

.toast-wrapper .toast {
  pointer-events: auto;
}

.toast-top-right {
  top: 80px;
  right: 20px;
}

.toast-top-left {
  top: 80px;
  left: 20px;
}

.toast-bottom-right {
  bottom: 20px;
  right: 20px;
}

.toast-bottom-left {
  bottom: 20px;
  left: 20px;
}

.toast-top-center {
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
}

.toast-bottom-center {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.toast {
  min-width: 320px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  border: none;
}

.toast-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  border-radius: 8px 8px 0 0;
}

.toast-body {
  padding: 12px 16px;
}

/* Responsive design */
@media (max-width: 768px) {
  .notification-container {
    left: 10px;
    right: 10px;
    top: 70px;
    max-width: none;
  }
  
  .toast-wrapper {
    left: 10px;
    right: 10px;
  }
  
  .toast-top-right,
  .toast-top-left,
  .toast-top-center {
    top: 70px;
    left: 10px;
    right: 10px;
    transform: none;
  }
  
  .toast {
    min-width: auto;
    width: 100%;
  }
}

/* Animation keyframes */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOutRight {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

.notification-card {
  animation: slideInRight 0.4s ease-out;
}

.notification-card.removing {
  animation: slideOutRight 0.3s ease-in;
}
`

// Inject styles if not already present
if (!document.querySelector('#adminlte-notification-styles')) {
  const styleSheet = document.createElement('style')
  styleSheet.id = 'adminlte-notification-styles'
  styleSheet.textContent = notificationStyles
  document.head.appendChild(styleSheet)
}

export default NotificationItem