import React from 'react';
import { useNavigate } from 'react-router-dom';

const ErrorPage = ({ code, title, message, showHomeButton = true }) => {
    const navigate = useNavigate();

    const errorConfig = {
        400: {
            title: 'Solicitud Incorrecta',
            message: 'La solicitud no pudo ser procesada debido a un error del cliente.',
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-50',
            borderColor: 'border-yellow-200'
        },
        401: {
            title: 'No Autorizado',
            message: 'Necesitas iniciar sesión para acceder a este recurso.',
            color: 'text-orange-600',
            bgColor: 'bg-orange-50',
            borderColor: 'border-orange-200'
        },
        403: {
            title: 'Acceso Prohibido',
            message: 'No tienes permisos para acceder a este recurso.',
            color: 'text-red-600',
            bgColor: 'bg-red-50',
            borderColor: 'border-red-200'
        },
        404: {
            title: 'Página No Encontrada',
            message: 'La página que buscas no existe o ha sido movida.',
            color: 'text-blue-600',
            bgColor: 'bg-blue-50',
            borderColor: 'border-blue-200'
        },
        500: {
            title: 'Error del Servidor',
            message: 'Ocurrió un error en el servidor. Por favor, intenta de nuevo más tarde.',
            color: 'text-purple-600',
            bgColor: 'bg-purple-50',
            borderColor: 'border-purple-200'
        }
    };

    const config = errorConfig[code] || errorConfig[500];
    const displayTitle = title || config.title;
    const displayMessage = message || config.message;

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <div className="max-w-md w-full">
                <div className={`${config.bgColor} ${config.borderColor} border-2 rounded-lg p-8 shadow-lg`}>
                    <div className="text-center">
                        <h1 className={`text-6xl font-bold ${config.color} mb-4`}>
                            {code}
                        </h1>
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                            {displayTitle}
                        </h2>
                        <p className="text-gray-600 mb-8">
                            {displayMessage}
                        </p>

                        <div className="space-y-3">
                            {showHomeButton && (
                                <button
                                    onClick={() => navigate('/')}
                                    className={`w-full ${config.color} border-2 ${config.borderColor} hover:${config.bgColor} font-semibold py-3 px-6 rounded-lg transition duration-200`}
                                >
                                    Volver al Inicio
                                </button>
                            )}

                            <button
                                onClick={() => navigate(-1)}
                                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                            >
                                Volver Atrás
                            </button>
                        </div>
                    </div>
                </div>

                <div className="mt-6 text-center text-sm text-gray-500">
                    <p>Sistema de Gestión de Inventario - HIDROVEN</p>
                    <p className="mt-1">Si el problema persiste, contacta al administrador del sistema.</p>
                </div>
            </div>
        </div>
    );
};

// Componentes específicos para cada error
export const Error400 = () => <ErrorPage code={400} />;
export const Error401 = () => <ErrorPage code={401} />;
export const Error403 = () => <ErrorPage code={403} />;
export const Error404 = () => <ErrorPage code={404} />;
export const Error500 = () => <ErrorPage code={500} />;

export default ErrorPage;
