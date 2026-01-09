import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    // Configure axios defaults
    if (token) {
        axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    }

    // Axios interceptor para manejar errores 401/403
    useEffect(() => {
        const interceptor = axios.interceptors.response.use(
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

        return () => axios.interceptors.response.eject(interceptor);
    }, []);

    useEffect(() => {
        // Verificar token al cargar la app
        const verifyToken = async () => {
            if (token) {
                try {
                    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                    const response = await axios.get(`${API_URL}/api/accounts/me/`, {
                        headers: { Authorization: `Token ${token}` }
                    });
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
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await axios.post(`${API_URL}/api/accounts/api-token-auth/`, { username, password });

            const { token: newToken } = res.data;

            localStorage.setItem('token', newToken);
            setToken(newToken);
            axios.defaults.headers.common['Authorization'] = `Token ${newToken}`;

            // Obtener datos del usuario
            const userRes = await axios.get(`${API_URL}/api/accounts/me/`, {
                headers: { Authorization: `Token ${newToken}` }
            });
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
        delete axios.defaults.headers.common['Authorization'];
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
