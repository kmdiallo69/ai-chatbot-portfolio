import styles from "./messageList.module.css";
import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useRouter } from 'next/router';

const MessageList = () => {
    // State management
    const [userMessage, setUserMessage] = useState("");
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [imageFile, setImageFile] = useState(null);
    const [error, setError] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [showBuildInfo, setShowBuildInfo] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [authLoading, setAuthLoading] = useState(true);
    
    // Refs for auto-scroll
    const chatBoxRef = useRef(null);
    const fileInputRef = useRef(null);
    const router = useRouter();
    
    // Configuration
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://chatbot-backend.kindwater-a13bf119.westus.azurecontainerapps.io';
    const BUILD_TIME = process.env.BUILD_TIME || 'Unknown';
    
    // Check authentication on component mount
    useEffect(() => {
        checkAuth();
    }, []); // checkAuth is defined inside component, this is acceptable

    // Auto-scroll to bottom when new messages are added
    useEffect(() => {
        if (chatBoxRef.current) {
            chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
        }
    }, [chatHistory]);
    
    // Clear error after 5 seconds
    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(null), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    // Authentication functions
    const checkAuth = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setAuthLoading(false);
            router.push('/auth/login');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
                setIsAuthenticated(true);
            } else {
                localStorage.removeItem('access_token');
                localStorage.removeItem('token_type');
                router.push('/auth/login');
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('token_type');
            router.push('/auth/login');
        } finally {
            setAuthLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_type');
        setIsAuthenticated(false);
        setUser(null);
        router.push('/auth/login');
    };

    const getAuthHeaders = () => {
        const token = localStorage.getItem('access_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    };
    
    const sendMessage = async () => {
        if (!userMessage.trim() && !imageFile) {
            setError("Please enter a message or select an image");
            return;
        }
        
        setLoading(true);
        setError(null);
        
        const userMessageText = userMessage.trim();
        const currentImageFile = imageFile;
        const currentImagePreview = imagePreview;
        
        // Add user message to chat immediately
        const newUserMessage = { 
            sender: "user", 
            message: userMessageText, 
            isImage: false,
            timestamp: new Date().toLocaleTimeString()
        };
        
        let messages = [newUserMessage];
        
        if (currentImageFile) {
            messages.push({
                sender: "user",
                message: currentImageFile,
                isImage: true,
                imagePreview: currentImagePreview,
                timestamp: new Date().toLocaleTimeString()
            });
        }
        
        setChatHistory(prev => [...prev, ...messages]);
        
        // Clear input
        setUserMessage("");
        setImageFile(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
        
        try {
            let response;
            
            if (currentImageFile) {
                // For image requests, use FormData and /chat/image endpoint
                const formData = new FormData();
                formData.append("prompt", userMessageText);
                formData.append("file", currentImageFile);
                
                response = await fetch(`${API_URL}/chat/image`, {
                    method: "POST",
                    headers: {
                        ...getAuthHeaders()
                    },
                    body: formData, 
                });
            } else {
                // For text-only requests, use JSON and /chat endpoint
                response = await fetch(`${API_URL}/chat`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify({
                        message: userMessageText
                    }),
                });
            }
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    logout();
                    return;
                }
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Add bot response to chat
            const botMessage = {
                sender: "bot",
                message: data.response,
                isImage: false,
                timestamp: new Date().toLocaleTimeString(),
                modelUsed: data.model_used
            };
            
            setChatHistory(prev => [...prev, botMessage]);
            
        } catch (error) {
            console.error("Error sending message:", error);
            setError(error.message || "Failed to send message. Please try again.");
            
            // Add error message to chat
            const errorMessage = {
                sender: "system",
                message: "Sorry, I'm having trouble connecting. Please try again.",
                isImage: false,
                isError: true,
                timestamp: new Date().toLocaleTimeString()
            };
            
            setChatHistory(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };
    
    const handleImageUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            setError("Please select a valid image file");
            return;
        }
        
        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            setError("Image size must be less than 10MB");
            return;
        }
        
        setImageFile(file);
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
    };
    
    const removeImage = () => {
        setImageFile(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };
    
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };
    
    const clearChat = () => {
        setChatHistory([]);
        setError(null);
    };

    // Show loading screen while checking authentication
    if (authLoading) {
        return (
            <div className={styles.container}>
                <div className={styles.loadingContainer}>
                    <div className={styles.spinner}></div>
                    <span>Loading...</span>
                </div>
            </div>
        );
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        return null;
    }
    
    return (
        <div className={styles.container}>
            <div className={styles.headerContainer}>
                <h1 className={styles.header}>AI Chatbot</h1>
                <div className={styles.headerButtons}>
                    <span className={styles.userInfo}>
                        Welcome, {user?.username}!
                    </span>
                    <button 
                        onClick={() => setShowBuildInfo(!showBuildInfo)}
                        className={styles.infoButton}
                        title="Build Information"
                    >
                        ℹ️
                    </button>
                    <button 
                        onClick={clearChat} 
                        className={styles.clearButton}
                        disabled={loading || chatHistory.length === 0}
                    >
                        Clear Chat
                    </button>
                    <button 
                        onClick={logout} 
                        className={styles.logoutButton}
                        title="Logout"
                    >
                        Logout
                    </button>
                </div>
            </div>
            
            {showBuildInfo && (
                <div className={styles.buildInfo}>
                    <h4>Build Information</h4>
                    <p><strong>API URL:</strong> {API_URL}</p>
                    <p><strong>Build Time:</strong> {BUILD_TIME}</p>
                    <p><strong>Version:</strong> 2025-01-11-v6-auth-system</p>
                    <p><strong>Deployment:</strong> Azure Static Web Apps</p>
                </div>
            )}
            
            {error && (
                <div className={styles.errorMessage}>
                    {error}
                </div>
            )}
            
            <div className={styles.chatBox} ref={chatBoxRef}>
                {chatHistory.length === 0 ? (
                    <div className={styles.welcomeMessage}>
                        <h2>Welcome to AI Chatbot! 🤖</h2>
                        <p>I can help you with text conversations and image analysis.</p>
                        <p>Type a message or upload an image to get started.</p>
                    </div>
                ) : (
                    chatHistory.map((chat, index) => (
                        <div
                            key={index}
                            className={`${styles.message} ${
                                chat.sender === "user" 
                                    ? styles.userMessage 
                                    : chat.sender === "bot" 
                                    ? styles.botMessage 
                                    : styles.systemMessage
                            } ${chat.isError ? styles.errorMessage : ''}`}
                        >
                            <div className={styles.messageContent}>
                                {chat.isImage ? (
                                    <img
                                        src={chat.imagePreview || URL.createObjectURL(chat.message)}
                                        alt="Uploaded"
                                        className={styles.image}
                                    />
                                ) : (
                                    <div className={styles.messageText}>
                                        {chat.sender === "bot" ? (
                                            <ReactMarkdown 
                                                remarkPlugins={[remarkGfm]}
                                                className={styles.markdownContent}
                                            >
                                                {chat.message}
                                            </ReactMarkdown>
                                        ) : (
                                            <span>{chat.message}</span>
                                        )}
                                    </div>
                                )}
                            </div>
                            <div className={styles.messageFooter}>
                                <span className={styles.timestamp}>{chat.timestamp}</span>
                                {chat.modelUsed && (
                                    <span className={styles.modelInfo}>via {chat.modelUsed}</span>
                                )}
                            </div>
                        </div>
                    ))
                )}
                
                {loading && (
                    <div className={styles.loadingContainer}>
                        <div className={styles.loadingMessage}>
                            <div className={styles.spinner}></div>
                            <span>AI is thinking...</span>
                        </div>
                    </div>
                )}
            </div>
            
            <div className={styles.inputContainer}>
                {imagePreview && (
                    <div className={styles.imagePreview}>
                        <img src={imagePreview} alt="Preview" className={styles.previewImage} />
                        <button onClick={removeImage} className={styles.removeImage}>
                            ×
                        </button>
                    </div>
                )}
                
                <div className={styles.inputRow}>
                    <textarea
                        placeholder="Type your message here... (Press Enter to send)"
                        value={userMessage}
                        onChange={(e) => setUserMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        className={styles.input}
                        disabled={loading}
                        rows="1"
                    />
                    
                    <label htmlFor="image-upload" className={styles.paperclipButton}>
                        📎
                    </label>
                    <input
                        id="image-upload"
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        className={styles.inputImage}
                        onChange={handleImageUpload}
                        disabled={loading}
                    />
                    
                    <button 
                        onClick={sendMessage} 
                        className={styles.sendButton} 
                        disabled={loading || (!userMessage.trim() && !imageFile)}
                    >
                        {loading ? "Sending..." : "Send"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MessageList;