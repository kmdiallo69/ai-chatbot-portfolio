import os
from typing import List
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

class Settings:
    """Centralized application configuration"""
    
    # Application
    APP_NAME: str = "AI Chatbot API"
    APP_DESCRIPTION: str = "An AI chatbot with secure authentication and AI capabilities"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://chatbot_user:chatbot_password@localhost:5432/chatbot_db")
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://lemon-ocean-0b1783f10.1.azurestaticapps.net").split(",")
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: set = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@chatbot.com")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Rate Limiting
    RATE_LIMITS = {
        'login': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
        'register': {'requests': 3, 'window': 3600},  # 3 attempts per hour
        'verify_email': {'requests': 10, 'window': 3600},  # 10 attempts per hour
        'reset_password': {'requests': 3, 'window': 3600},  # 3 attempts per hour
        'general': {'requests': 20, 'window': 60},  # 20 requests per minute
        'chat': {'requests': 60, 'window': 60},  # 60 chat requests per minute
    }
    
    # Account Security
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 3600  # 1 hour in seconds
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 1
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if cls.ENVIRONMENT == "production":
            if cls.JWT_SECRET_KEY == "your-secret-key-change-this-in-production":
                raise ValueError("JWT_SECRET_KEY must be changed in production")
            
            if not cls.DATABASE_URL.startswith("postgresql"):
                raise ValueError("PostgreSQL database required in production")

# Global settings instance
settings = Settings()

# Validate on import
if __name__ != "__main__":
    settings.validate() 