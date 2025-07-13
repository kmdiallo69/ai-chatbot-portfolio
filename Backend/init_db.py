#!/usr/bin/env python3
"""
Database initialization script
Run this script to create database tables and perform initial setup
"""

import os
import logging
from database import create_tables, drop_tables, health_check

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main initialization function"""
    try:
        logger.info("Starting database initialization...")
        
        # Check if we should drop existing tables
        if os.getenv("DROP_TABLES", "false").lower() == "true":
            logger.warning("Dropping existing tables...")
            drop_tables()
        
        # Create tables
        logger.info("Creating database tables...")
        create_tables()
        
        # Health check
        logger.info("Performing database health check...")
        if health_check():
            logger.info("✅ Database initialization completed successfully!")
        else:
            logger.error("❌ Database health check failed!")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 