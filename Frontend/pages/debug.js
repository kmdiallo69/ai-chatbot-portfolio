import React from 'react';
import Link from 'next/link';

const DebugPage = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const buildTime = process.env.BUILD_TIME || 'Unknown';
    
    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Debug Information</h1>
            <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                <h2>Environment Variables</h2>
                <p><strong>NEXT_PUBLIC_API_URL:</strong> {apiUrl}</p>
                <p><strong>BUILD_TIME:</strong> {buildTime}</p>
                <p><strong>Node Environment:</strong> {process.env.NODE_ENV || 'development'}</p>
            </div>
            
            <div style={{ background: '#e8f4f8', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                <h2>Expected Values</h2>
                <p><strong>Expected API URL:</strong> https://chatbot-backend-1752261683.purplesmoke-82a64915.eastus.azurecontainerapps.io</p>
                <p><strong>Current API URL:</strong> {apiUrl}</p>
                <p><strong>Status:</strong> {apiUrl.includes('azurecontainerapps.io') ? '✅ Correct' : '❌ Using fallback'}</p>
            </div>
            
            <div style={{ background: '#f0f8ff', padding: '15px', borderRadius: '8px' }}>
                <h2>Test API Connection</h2>
                <button 
                    onClick={async () => {
                        try {
                            const response = await fetch(`${apiUrl}/health`);
                            const data = await response.json();
                            alert(`API Response: ${JSON.stringify(data)}`);
                        } catch (error) {
                            alert(`API Error: ${error.message}`);
                        }
                    }}
                    style={{ 
                        padding: '10px 20px', 
                        backgroundColor: '#007bff', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '5px', 
                        cursor: 'pointer' 
                    }}
                >
                    Test API Connection
                </button>
            </div>
            
            <div style={{ marginTop: '20px' }}>
                <Link href="/" style={{ color: '#007bff', textDecoration: 'none' }}>← Back to Chatbot</Link>
            </div>
        </div>
    );
};

export default DebugPage; 