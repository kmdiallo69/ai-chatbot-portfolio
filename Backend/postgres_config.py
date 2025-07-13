#!/usr/bin/env python3
"""
PostgreSQL Configuration
Simple configuration helper for PostgreSQL database setup
"""

import os

# Default PostgreSQL configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'chatbot_db',
    'user': 'chatbot_user',
    'password': 'chatbot_password',
    'admin_user': 'postgres',
    'admin_password': 'password'
}

def get_postgres_config():
    """Get PostgreSQL configuration from environment or defaults"""
    return {
        'host': os.getenv('POSTGRES_HOST', DEFAULT_CONFIG['host']),
        'port': int(os.getenv('POSTGRES_PORT', DEFAULT_CONFIG['port'])),
        'database': os.getenv('POSTGRES_DB', DEFAULT_CONFIG['database']),
        'user': os.getenv('POSTGRES_USER', DEFAULT_CONFIG['user']),
        'password': os.getenv('POSTGRES_PASSWORD', DEFAULT_CONFIG['password']),
        'admin_user': os.getenv('POSTGRES_ADMIN_USER', DEFAULT_CONFIG['admin_user']),
        'admin_password': os.getenv('POSTGRES_ADMIN_PASSWORD', DEFAULT_CONFIG['admin_password'])
    }

def get_database_url():
    """Get the database URL for SQLAlchemy"""
    config = get_postgres_config()
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def get_admin_database_url():
    """Get the admin database URL for setup"""
    config = get_postgres_config()
    return f"postgresql://{config['admin_user']}:{config['admin_password']}@{config['host']}:{config['port']}/postgres"

def print_config():
    """Print current PostgreSQL configuration"""
    config = get_postgres_config()
    print("PostgreSQL Configuration:")
    print("=" * 40)
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Password: {'*' * len(config['password'])}")
    print("=" * 40)
    print(f"Database URL: {get_database_url()}")
    print("=" * 40)

if __name__ == "__main__":
    print_config() 