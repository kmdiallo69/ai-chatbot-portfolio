import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import styles from '../styles/Auth.module.css';

const Login = ({ onSwitchToRegister, onLoginSuccess }) => {
    const [formData, setFormData] = useState({
        usernameOrEmail: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const { login } = useAuth();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error when user starts typing
        if (error) setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.usernameOrEmail.trim() || !formData.password.trim()) {
            setError('Please fill in all fields');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const result = await login(formData.usernameOrEmail, formData.password);
            
            if (result.success) {
                onLoginSuccess && onLoginSuccess();
            } else {
                setError(result.message);
            }
        } catch (error) {
            setError('Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.authContainer}>
            <div className={styles.authCard}>
                <h2 className={styles.authTitle}>Welcome Back</h2>
                <p className={styles.welcomeMessage}>
                    Sign in to access your AI chatbot
                </p>
                
                {error && (
                    <div className={styles.errorMessage}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className={styles.authForm}>
                    <div className={styles.formGroup}>
                        <label htmlFor="usernameOrEmail" className={styles.formLabel}>
                            Username or Email
                        </label>
                        <input
                            type="text"
                            id="usernameOrEmail"
                            name="usernameOrEmail"
                            value={formData.usernameOrEmail}
                            onChange={handleChange}
                            className={`${styles.formInput} ${error ? styles.error : ''}`}
                            placeholder="Enter your username or email"
                            disabled={loading}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="password" className={styles.formLabel}>
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className={`${styles.formInput} ${error ? styles.error : ''}`}
                            placeholder="Enter your password"
                            disabled={loading}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={styles.submitButton}
                    >
                        {loading ? (
                            <>
                                <span className={styles.loadingSpinner}></span>
                                Signing In...
                            </>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>

                <div className={styles.authLinks}>
                    <p>
                        Don&apos;t have an account?{' '}
                        <button
                            type="button"
                            onClick={onSwitchToRegister}
                            className={styles.authLink}
                            style={{ background: 'none', border: 'none', padding: 0 }}
                        >
                            Sign up here
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login; 