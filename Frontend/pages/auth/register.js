import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../../styles/Auth.module.css';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend-1752261683.purplesmoke-82a64915.eastus.azurecontainerapps.io';

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const validateForm = () => {
        if (formData.username.length < 3) {
            return 'Username must be at least 3 characters long';
        }
        
        if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
            return 'Username can only contain letters, numbers, and underscores';
        }

        if (formData.password.length < 8) {
            return 'Password must be at least 8 characters long';
        }

        if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
            return 'Password must contain at least one letter and one number';
        }

        if (formData.password !== formData.confirmPassword) {
            return 'Passwords do not match';
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            return 'Please enter a valid email address';
        }

        return null;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        const validationError = validateForm();
        if (validationError) {
            setError(validationError);
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }

            setSuccess('Registration successful! Please check your email to verify your account.');
            
            // Redirect to login after 3 seconds
            setTimeout(() => {
                router.push('/auth/login');
            }, 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.authCard}>
                <div className={styles.authHeader}>
                    <h1 className={styles.title}>Create Account</h1>
                    <p className={styles.subtitle}>Join the AI Chatbot community</p>
                </div>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username" className={styles.label}>
                            Username
                        </label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            className={styles.input}
                            required
                            placeholder="Choose a username (3+ characters)"
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="email" className={styles.label}>
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className={styles.input}
                            required
                            placeholder="Enter your email address"
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="password" className={styles.label}>
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className={styles.input}
                            required
                            placeholder="8+ characters, letters & numbers"
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="confirmPassword" className={styles.label}>
                            Confirm Password
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className={styles.input}
                            required
                            placeholder="Confirm your password"
                        />
                    </div>

                    {error && (
                        <div className={styles.errorMessage}>
                            {error}
                        </div>
                    )}

                    {success && (
                        <div className={styles.successMessage}>
                            {success}
                        </div>
                    )}

                    <div className={styles.passwordRequirements}>
                        <p className={styles.requirementsTitle}>Password Requirements:</p>
                        <ul className={styles.requirementsList}>
                            <li className={formData.password.length >= 8 ? styles.valid : styles.invalid}>
                                At least 8 characters
                            </li>
                            <li className={/[a-zA-Z]/.test(formData.password) ? styles.valid : styles.invalid}>
                                Contains letters
                            </li>
                            <li className={/\d/.test(formData.password) ? styles.valid : styles.invalid}>
                                Contains numbers
                            </li>
                        </ul>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={styles.submitButton}
                    >
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <div className={styles.authFooter}>
                    <p className={styles.footerText}>
                        Already have an account?{' '}
                        <Link href="/auth/login" className={styles.authLink}>
                            Sign in here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register; 