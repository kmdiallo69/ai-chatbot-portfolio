import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../../styles/Auth.module.css';

const Verify = () => {
    const [token, setToken] = useState('');
    const [status, setStatus] = useState('idle'); // idle, loading, success, error
    const [message, setMessage] = useState('');
    const router = useRouter();

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend-1752261683.purplesmoke-82a64915.eastus.azurecontainerapps.io';

    useEffect(() => {
        // Check if there's a token in the URL query params
        const { token: queryToken } = router.query;
        if (queryToken) {
            setToken(queryToken);
            verifyEmail(queryToken);
        }
    }, [router.query]); // verifyEmail is defined inside component, this is acceptable

    const verifyEmail = async (verificationToken) => {
        setStatus('loading');
        setMessage('Verifying your email...');

        try {
            const response = await fetch(`${API_URL}/auth/verify-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    verification_token: verificationToken
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Verification failed');
            }

            setStatus('success');
            setMessage('Email verified successfully! You can now log in to your account.');
            
            // Redirect to login after 3 seconds
            setTimeout(() => {
                router.push('/auth/login');
            }, 3000);
        } catch (err) {
            setStatus('error');
            setMessage(err.message);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!token.trim()) {
            setMessage('Please enter your verification token');
            return;
        }
        await verifyEmail(token);
    };

    const handleChange = (e) => {
        setToken(e.target.value);
    };

    return (
        <div className={styles.container}>
            <div className={styles.authCard}>
                <div className={styles.authHeader}>
                    <h1 className={styles.title}>Verify Your Email</h1>
                    <p className={styles.subtitle}>
                        Enter the verification token sent to your email
                    </p>
                </div>

                {status === 'idle' && (
                    <form onSubmit={handleSubmit} className={styles.form}>
                        <div className={styles.formGroup}>
                            <label htmlFor="token" className={styles.label}>
                                Verification Token
                            </label>
                            <input
                                type="text"
                                id="token"
                                name="token"
                                value={token}
                                onChange={handleChange}
                                className={styles.input}
                                required
                                placeholder="Enter your verification token"
                            />
                        </div>

                        <button
                            type="submit"
                            className={styles.submitButton}
                            disabled={!token.trim()}
                        >
                            Verify Email
                        </button>
                    </form>
                )}

                {status === 'loading' && (
                    <div className={styles.statusContainer}>
                        <div className={styles.spinner}></div>
                        <p className={styles.statusMessage}>{message}</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className={styles.statusContainer}>
                        <div className={styles.successIcon}>✅</div>
                        <p className={styles.successMessage}>{message}</p>
                        <p className={styles.redirectMessage}>
                            Redirecting to login page...
                        </p>
                    </div>
                )}

                {status === 'error' && (
                    <div className={styles.statusContainer}>
                        <div className={styles.errorIcon}>❌</div>
                        <p className={styles.errorMessage}>{message}</p>
                        <button
                            onClick={() => {
                                setStatus('idle');
                                setMessage('');
                                setToken('');
                            }}
                            className={styles.retryButton}
                        >
                            Try Again
                        </button>
                    </div>
                )}

                <div className={styles.authFooter}>
                    <p className={styles.footerText}>
                        Already verified?{' '}
                        <Link href="/auth/login" className={styles.authLink}>
                            Sign in here
                        </Link>
                    </p>
                    <p className={styles.footerText}>
                        Need a new account?{' '}
                        <Link href="/auth/register" className={styles.authLink}>
                            Sign up here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Verify; 