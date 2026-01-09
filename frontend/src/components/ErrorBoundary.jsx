import React from 'react'

/**
 * Error Boundary Component
 * Captura errores de JavaScript en cualquier parte del árbol de componentes hijo
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null, errorInfo: null }
    }

    static getDerivedStateFromError(error) {
        // Actualiza el estado para mostrar la UI de fallback en el próximo render
        return { hasError: true }
    }

    componentDidCatch(error, errorInfo) {
        // También puedes enviar el error a un servicio de logging como Sentry
        console.error('Error capturado por ErrorBoundary:', error, errorInfo)
        this.setState({
            error: error,
            errorInfo: errorInfo
        })
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null })
        // Recargar la página para reiniciar la aplicación
        window.location.href = '/'
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
                    <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
                        <div className="text-center">
                            {/* Icon */}
                            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>

                            {/* Title */}
                            <h1 className="text-2xl font-bold text-gray-900 mb-2">
                                ¡Ups! Algo salió mal
                            </h1>

                            {/* Description */}
                            <p className="text-gray-600 mb-6">
                                Ha ocurrido un error inesperado. Por favor, intenta recargar la página.
                            </p>

                            {/* Error details (only in development) */}
                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <details className="mb-6 text-left">
                                    <summary className="cursor-pointer text-sm text-gray-700 font-medium mb-2">
                                        Ver detalles del error
                                    </summary>
                                    <div className="bg-gray-100 rounded p-4 text-xs text-gray-800 overflow-auto max-h-64">
                                        <p className="font-semibold mb-2">{this.state.error.toString()}</p>
                                        <pre className="whitespace-pre-wrap">
                                            {this.state.errorInfo?.componentStack}
                                        </pre>
                                    </div>
                                </details>
                            )}

                            {/* Actions */}
                            <div className="space-y-3">
                                <button
                                    onClick={this.handleReset}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                                >
                                    Volver al inicio
                                </button>
                                <button
                                    onClick={() => window.location.reload()}
                                    className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors"
                                >
                                    Recargar página
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
