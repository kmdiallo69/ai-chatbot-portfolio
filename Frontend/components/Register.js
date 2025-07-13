import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import styles from '../styles/Auth.module.css';

const Register = ({ onSwitchToLogin, onRegisterSuccess }) => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [passwordStrength, setPasswordStrength] = useState('');

    const { register } = useAuth();

    const validatePassword = (password) => {
        if (password.length < 8) {
            return { strength: 'weak', message: 'Password must be at least 8 characters long' };
        }
        
        const hasLetter = /[a-zA-Z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        if (!hasLetter || !hasNumber) {
            return { strength: 'weak', message: 'Password must contain both letters and numbers' };
        }
        
        if (password.length >= 8 && hasLetter && hasNumber && !hasSpecial) {
            return { strength: 'medium', message: 'Good password' };
        }
        
        if (password.length >= 8 && hasLetter && hasNumber && hasSpecial) {
            return { strength: 'strong', message: 'Strong password' };
        }
        
        return { strength: 'weak', message: 'Password too weak' };
    };

    const validateUsername = (username) => {
        if (username.length < 3) {
            return 'Username must be at least 3 characters long';
        }
        if (username.length > 50) {
            return 'Username must be less than 50 characters';
        }
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            return 'Username can only contain letters, numbers, and underscores';
        }
        return '';
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear error when user starts typing
        if (error) setError('');
        
        // Check password strength
        if (name === 'password') {
            const validation = validatePassword(value);
            setPasswordStrength(validation);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validation
        if (!formData.username.trim() || !formData.email.trim() || !formData.password.trim() || !formData.confirmPassword.trim()) {
            setError('Please fill in all fields');
            return;
        }

        const usernameError = validateUsername(formData.username);
        if (usernameError) {
            setError(usernameError);
            return;
        }

        const passwordValidation = validatePassword(formData.password);
        if (passwordValidation.strength === 'weak') {
            setError(passwordValidation.message);
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const result = await register(formData.username, formData.email, formData.password);
            
            if (result.success) {
                onRegisterSuccess && onRegisterSuccess(result.message);
            } else {
                setError(result.message);
            }
        } catch (error) {
            setError('Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.authContainer}>
            <div className={styles.authCard}>
                <h2 className={styles.authTitle}>Create Account</h2>
                <p className={styles.welcomeMessage}>
                    Join us to start chatting with AI
                </p>
                
                {error && (
                    <div className={styles.errorMessage}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className={styles.authForm}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username" className={styles.formLabel}>
                            Username
                        </label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            className={`${styles.formInput} ${error && error.includes('Username') ? styles.error : ''}`}
                            placeholder="Choose a username"
                            disabled={loading}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="email" className={styles.formLabel}>
                            Email
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className={`${styles.formInput} ${error && error.includes('email') ? styles.error : ''}`}
                            placeholder="Enter your email"
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
                            className={`${styles.formInput} ${error && error.includes('Password') ? styles.error : ''}`}
                            placeholder="Create a password"
                            disabled={loading}
                        />
                        {formData.password && (
                            <div className={`${styles.passwordStrength} ${styles[passwordStrength.strength]}`}>
                                {passwordStrength.message}
                            </div>
                        )}
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="confirmPassword" className={styles.formLabel}>
                            Confirm Password
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className={`${styles.formInput} ${error && error.includes('match') ? styles.error : ''}`}
                            placeholder="Confirm your password"
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
                                Creating Account...
                            </>
                        ) : (
                            'Create Account'
                        )}
                    </button>
                </form>

                <div className={styles.authLinks}>
                    <p>
                        Already have an account?{' '}
                        <button
                            type="button"
                            onClick={onSwitchToLogin}
                            className={styles.authLink}
                            style={{ background: 'none', border: 'none', padding: 0 }}
                        >
                            Sign in here
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register; 