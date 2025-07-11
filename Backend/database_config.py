import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/chatbot")

# For development with Docker
DEV_DATABASE_URL = "postgresql://postgres:password@localhost:5432/chatbot"

# For production (will be set via environment variables)
PROD_DATABASE_URL = os.getenv("DATABASE_URL")

# Use appropriate URL based on environment
if os.getenv("ENVIRONMENT") == "production":
    DB_URL = PROD_DATABASE_URL or DATABASE_URL
else:
    DB_URL = DEV_DATABASE_URL

# Create engine
engine = create_engine(
    DB_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check function
def check_database_connection():
    """Check if database connection is healthy"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Drop all tables (use with caution!)
def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine) 