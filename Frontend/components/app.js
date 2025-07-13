import React, { useState } from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import MessageList from "./messageList";
import Login from './Login';
import Register from './Register';
import VerifyEmail from './VerifyEmail';

const AuthenticatedApp = () => {
    const { user, loading } = useAuth();
    const [currentView, setCurrentView] = useState('login');
    const [registrationMessage, setRegistrationMessage] = useState('');

    if (loading) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                fontSize: '18px'
            }}>
                Loading...
            </div>
        );
    }

    console.log('User state:', user); // Debug log
    console.log('Loading state:', loading); // Debug log
    
    if (user) {
        console.log('User authenticated, showing chat'); // Debug log
        return <MessageList />;
    }

    const handleSwitchToRegister = () => {
        setCurrentView('register');
        setRegistrationMessage('');
    };

    const handleSwitchToLogin = () => {
        setCurrentView('login');
        setRegistrationMessage('');
    };

    const handleSwitchToVerifyEmail = () => {
        setCurrentView('verifyEmail');
    };

    const handleRegisterSuccess = (message) => {
        setRegistrationMessage(message);
        setCurrentView('verifyEmail');
    };

    const handleLoginSuccess = () => {
        // The user state will be updated by the AuthContext
        // and the component will re-render showing the MessageList
    };

    switch (currentView) {
        case 'register':
            return (
                <Register
                    onSwitchToLogin={handleSwitchToLogin}
                    onRegisterSuccess={handleRegisterSuccess}
                />
            );
        case 'verifyEmail':
            return (
                <VerifyEmail
                    onSwitchToLogin={handleSwitchToLogin}
                    successMessage={registrationMessage}
                />
            );
        case 'login':
        default:
            return (
                <Login
                    onSwitchToRegister={handleSwitchToRegister}
                    onLoginSuccess={handleLoginSuccess}
                />
            );
    }
};

const App = () => {
    return (
        <AuthProvider>
            <AuthenticatedApp />
        </AuthProvider>
    );
};

export default App;