import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import styles from '../styles/Auth.module.css';

const VerifyEmail = ({ onSwitchToLogin, successMessage }) => {
    const [token, setToken] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showTokenInput, setShowTokenInput] = useState(false);

    const { verifyEmail } = useAuth();

    useEffect(() => {
        // Check if there's a token in the URL (for email links)
        const urlParams = new URLSearchParams(window.location.search);
        const urlToken = urlParams.get('token');
        
        if (urlToken) {
            setToken(urlToken);
            handleVerification(urlToken);
        } else {
            setShowTokenInput(true);
        }
    }, [handleVerification]);

    const handleVerification = async (verificationToken) => {
        if (!verificationToken) return;

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const result = await verifyEmail(verificationToken);
            
            if (result.success) {
                setSuccess(result.message);
                // Redirect to login after 3 seconds
                setTimeout(() => {
                    onSwitchToLogin();
                }, 3000);
            } else {
                setError(result.message);
            }
        } catch (error) {
            setError('Verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!token.trim()) {
            setError('Please enter the verification token');
            return;
        }

        await handleVerification(token);
    };

    const handleTokenChange = (e) => {
        setToken(e.target.value);
        if (error) setError('');
    };

    return (
        <div className={styles.authContainer}>
            <div className={styles.authCard}>
                <div className={styles.verificationIcon}>
                    {loading ? '⏳' : success ? '✅' : '📧'}
                </div>
                
                <h2 className={styles.authTitle}>Email Verification</h2>
                
                {successMessage && (
                    <div className={styles.successMessage}>
                        {successMessage}
                    </div>
                )}
                
                {!loading && !success && (
                    <div className={styles.verificationMessage}>
                        {showTokenInput ? (
                            <>
                                We&apos;ve sent a verification email to your inbox.
                                <br />
                                Please check your email and enter the verification token below.
                            </>
                        ) : (
                            'Verifying your email address...'
                        )}
                    </div>
                )}

                {loading && (
                    <div className={styles.verificationMessage}>
                        <span className={styles.loadingSpinner}></span>
                        Verifying your email...
                    </div>
                )}

                {success && (
                    <div className={styles.successMessage}>
                        <strong>{success}</strong>
                        <br />
                        <br />
                        Redirecting to login page in 3 seconds...
                    </div>
                )}

                {error && (
                    <div className={styles.errorMessage}>
                        {error}
                    </div>
                )}

                {showTokenInput && !loading && !success && (
                    <form onSubmit={handleSubmit} className={styles.authForm}>
                        <div className={styles.formGroup}>
                            <label htmlFor="token" className={styles.formLabel}>
                                Verification Token
                            </label>
                            <input
                                type="text"
                                id="token"
                                name="token"
                                value={token}
                                onChange={handleTokenChange}
                                className={`${styles.formInput} ${error ? styles.error : ''}`}
                                placeholder="Enter verification token"
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading || !token.trim()}
                            className={styles.submitButton}
                        >
                            {loading ? (
                                <>
                                    <span className={styles.loadingSpinner}></span>
                                    Verifying...
                                </>
                            ) : (
                                'Verify Email'
                            )}
                        </button>
                    </form>
                )}

                <div className={styles.authLinks}>
                    <p>
                        <button
                            type="button"
                            onClick={onSwitchToLogin}
                            className={styles.authLink}
                            style={{ background: 'none', border: 'none', padding: 0 }}
                        >
                            Back to Login
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default VerifyEmail; 