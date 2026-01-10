import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    // Axios interceptor para manejar errores 401/403
    useEffect(() => {
        const interceptor = api.interceptors.response.use(
            response => response,
            error => {
                if (error.response?.status === 401 || error.response?.status === 403) {
                    // Token inválido o expirado
                    logout();
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );

        return () => api.interceptors.response.eject(interceptor);
    }, []);

    useEffect(() => {
        // Verificar token al cargar la app
        const verifyToken = async () => {
            if (token) {
                try {
                    const response = await api.get('accounts/me/');
                    setUser(response.data);
                } catch (error) {
                    console.error("Token verification failed", error);
                    logout();
                }
            }
            setLoading(false);
        };

        verifyToken();
    }, [token]);

    const login = async (username, password) => {
        try {
            const res = await api.post('accounts/api-token-auth/', { username, password });

            const { token: newToken } = res.data;

            localStorage.setItem('token', newToken);
            setToken(newToken);

            // Obtener datos del usuario
            const userRes = await api.get('accounts/me/');
            setUser(userRes.data);

            return true;
        } catch (error) {
            console.error("Login failed", error);
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
