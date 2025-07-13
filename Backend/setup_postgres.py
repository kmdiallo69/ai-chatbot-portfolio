#!/usr/bin/env python3
"""
PostgreSQL setup script
This script helps set up PostgreSQL database and user for the chatbot application
"""

import os
import logging
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_and_user():
    """Create PostgreSQL database and user if they don't exist"""
    
    # Default PostgreSQL connection for admin tasks
    admin_db_url = os.getenv("POSTGRES_ADMIN_URL", "postgresql://postgres:password@localhost:5432/postgres")
    
    # Parse the admin URL
    parsed_admin = urlparse(admin_db_url)
    
    # Target database configuration
    target_db_name = os.getenv("POSTGRES_DB", "chatbot_db")
    target_user = os.getenv("POSTGRES_USER", "chatbot_user")
    target_password = os.getenv("POSTGRES_PASSWORD", "chatbot_password")
    
    try:
        # Connect to PostgreSQL as admin
        logger.info("Connecting to PostgreSQL as admin...")
        # Extract database name from path
        db_name = "postgres"
        if parsed_admin.path and parsed_admin.path != "/":
            db_name = parsed_admin.path[1:]
        
        conn = psycopg2.connect(
            host=parsed_admin.hostname,
            port=parsed_admin.port or 5432,
            user=parsed_admin.username,
            password=parsed_admin.password,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if it doesn't exist
        logger.info(f"Creating user '{target_user}'...")
        try:
            cursor.execute(f"""
                CREATE USER {target_user} WITH PASSWORD '{target_password}';
            """)
            logger.info(f"✅ User '{target_user}' created successfully")
        except psycopg2.errors.DuplicateObject:
            logger.info(f"ℹ️  User '{target_user}' already exists")
        
        # Create database if it doesn't exist
        logger.info(f"Creating database '{target_db_name}'...")
        try:
            cursor.execute(f"""
                CREATE DATABASE {target_db_name} OWNER {target_user};
            """)
            logger.info(f"✅ Database '{target_db_name}' created successfully")
        except psycopg2.errors.DuplicateDatabase:
            logger.info(f"ℹ️  Database '{target_db_name}' already exists")
        
        # Grant privileges
        logger.info(f"Granting privileges to user '{target_user}'...")
        cursor.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {target_db_name} TO {target_user};
        """)
        
        # Close admin connection
        cursor.close()
        conn.close()
        
        # Test connection to target database
        logger.info("Testing connection to target database...")
        host = parsed_admin.hostname or "localhost"
        port = parsed_admin.port or 5432
        target_db_url = f"postgresql://{target_user}:{target_password}@{host}:{port}/{target_db_name}"
        
        test_conn = psycopg2.connect(target_db_url)
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT version();")
        version = test_cursor.fetchone()
        logger.info(f"✅ Connected to PostgreSQL: {version[0]}")
        
        test_cursor.close()
        test_conn.close()
        
        # Output the connection string for the application
        logger.info("=" * 60)
        logger.info("DATABASE SETUP COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Database Name: {target_db_name}")
        logger.info(f"Database User: {target_user}")
        logger.info(f"Database URL: {target_db_url}")
        logger.info("=" * 60)
        logger.info("Add this to your environment variables:")
        logger.info(f"DATABASE_URL={target_db_url}")
        logger.info("=" * 60)
        
        return target_db_url
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL setup failed: {str(e)}")
        raise

def main():
    """Main setup function"""
    try:
        logger.info("Starting PostgreSQL setup...")
        
        # Check if PostgreSQL is running
        try:
            import subprocess
            result = subprocess.run(['pg_isready'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ PostgreSQL server is not running!")
                logger.info("Please start PostgreSQL server first:")
                logger.info("  macOS: brew services start postgresql")
                logger.info("  Linux: sudo systemctl start postgresql")
                logger.info("  Windows: net start postgresql")
                return 1
        except FileNotFoundError:
            logger.warning("⚠️  pg_isready not found. Assuming PostgreSQL is running...")
        
        # Create database and user
        db_url = create_database_and_user()
        
        logger.info("✅ PostgreSQL setup completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Set DATABASE_URL environment variable")
        logger.info("2. Run: python init_db.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL setup failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 