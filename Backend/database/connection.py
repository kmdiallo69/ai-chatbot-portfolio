import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from .models import Base

logger = logging.getLogger(__name__)

# Database configuration from centralized settings
from config import settings
DATABASE_URL = settings.DATABASE_URL
ENVIRONMENT = settings.ENVIRONMENT

# Database engine configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for fallback/testing only
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=ENVIRONMENT == "development"
    )
else:
    # PostgreSQL configuration (default)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        echo=ENVIRONMENT == "development"
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def drop_tables():
    """Drop all database tables - use with caution!"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise

@contextmanager
def get_db_session() -> Generator:
    """
    Context manager for database sessions
    Ensures proper cleanup of database connections
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()

def get_db():
    """
    Dependency for FastAPI endpoints
    Returns a database session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def health_check():
    """
    Check database connectivity
    Returns True if database is accessible, False otherwise
    """
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False 