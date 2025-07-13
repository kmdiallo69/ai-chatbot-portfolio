import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend.kindmushroom-11a9e276.westus.azurecontainerapps.io';

    // Check if user is authenticated on mount
    useEffect(() => {
        checkAuthStatus();
    }, [checkAuthStatus]);

    const checkAuthStatus = async () => {
        try {
            console.log('API_URL:', API_URL); // Debug log
            const token = Cookies.get('access_token');
            console.log('Token found:', !!token); // Debug log
            if (!token) {
                console.log('No token, showing auth pages'); // Debug log
                setLoading(false);
                return;
            }

            const response = await fetch(`${API_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
            } else {
                // Token is invalid, remove it
                Cookies.remove('access_token');
                setUser(null);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            Cookies.remove('access_token');
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (usernameOrEmail, password) => {
        try {
            setError(null);
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username_or_email: usernameOrEmail,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                Cookies.set('access_token', data.access_token, { expires: 7 }); // 7 days
                setUser(data.user);
                return { success: true, message: data.message };
            } else {
                setError(data.message || 'Login failed');
                return { success: false, message: data.message || 'Login failed' };
            }
        } catch (error) {
            const errorMessage = 'Network error. Please try again.';
            setError(errorMessage);
            return { success: false, message: errorMessage };
        }
    };

    const register = async (username, email, password) => {
        try {
            setError(null);
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                return { success: true, message: data.message };
            } else {
                setError(data.message || 'Registration failed');
                return { success: false, message: data.message || 'Registration failed' };
            }
        } catch (error) {
            const errorMessage = 'Network error. Please try again.';
            setError(errorMessage);
            return { success: false, message: errorMessage };
        }
    };

    const verifyEmail = async (token) => {
        try {
            setError(null);
            const response = await fetch(`${API_URL}/auth/verify-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                return { success: true, message: data.message };
            } else {
                setError(data.message || 'Email verification failed');
                return { success: false, message: data.message || 'Email verification failed' };
            }
        } catch (error) {
            const errorMessage = 'Network error. Please try again.';
            setError(errorMessage);
            return { success: false, message: errorMessage };
        }
    };

    const logout = async () => {
        try {
            const token = Cookies.get('access_token');
            if (token) {
                await fetch(`${API_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Logout request failed:', error);
        } finally {
            Cookies.remove('access_token');
            setUser(null);
        }
    };

    const value = {
        user,
        loading,
        error,
        login,
        register,
        verifyEmail,
        logout,
        checkAuthStatus
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}; 