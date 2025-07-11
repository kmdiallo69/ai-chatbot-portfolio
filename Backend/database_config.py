import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

# For development with Docker (PostgreSQL)
DEV_DATABASE_URL = "postgresql://postgres:password@localhost:5432/chatbot"

# For production - use SQLite by default, PostgreSQL if DATABASE_URL is set
PROD_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

# Use appropriate URL based on environment
if os.getenv("ENVIRONMENT") == "production":
    DB_URL = PROD_DATABASE_URL
else:
    # Use PostgreSQL for local development if available, SQLite as fallback
    DB_URL = DEV_DATABASE_URL if os.getenv("USE_POSTGRES") else "sqlite:///./chatbot.db"

# Create engine with appropriate settings for SQLite vs PostgreSQL
if DB_URL.startswith("sqlite:"):
    engine = create_engine(
        DB_URL,
        echo=os.getenv("DEBUG", "False").lower() == "true",
        future=True,
        connect_args={"check_same_thread": False},  # SQLite specific
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        DB_URL,
        echo=os.getenv("DEBUG", "False").lower() == "true",
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
            conn.execute(text("SELECT 1"))
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