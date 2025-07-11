-- Initialize the chatbot database
-- Note: Database 'chatbot' is created automatically by Docker environment
-- Connect to the chatbot database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: The main tables (users, etc.) will be created by SQLAlchemy when the application starts
-- This init script only sets up additional database configuration

-- Function to create indexes after tables are created
-- This will be called after SQLAlchemy creates the tables
CREATE OR REPLACE FUNCTION create_chatbot_indexes() RETURNS VOID AS $$
BEGIN
    -- Create indexes for users table (if it exists)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_verification_token ON users(verification_token);
    END IF;

    -- Create indexes for chat history (if it exists)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chat_history') THEN
        CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Additional tables (these can be created immediately)
-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    model_used VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create basic indexes for the tables we just created
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at); 