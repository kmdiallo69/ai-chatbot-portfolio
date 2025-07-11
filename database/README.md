# Database Setup for AI Chatbot

This directory contains the database configuration and setup files for the AI Chatbot application.

## Database Technology

We use **PostgreSQL** as the primary database for this application, which provides:
- Better performance and scalability than SQLite
- ACID compliance
- Advanced features like JSON support, full-text search
- Better concurrent access handling
- Production-ready reliability

## Quick Start

### 1. Using Docker (Recommended)

```bash
# Start PostgreSQL and pgAdmin
cd database
docker-compose up -d

# Check if containers are running
docker-compose ps
```

### 2. Manual PostgreSQL Installation

If you prefer to install PostgreSQL manually:

```bash
# On macOS
brew install postgresql
brew services start postgresql

# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# On Windows
# Download and install from https://www.postgresql.org/download/windows/
```

### 3. Database Configuration

The application uses the following default connection settings:

```
Host: localhost
Port: 5432
Database: chatbot
Username: postgres
Password: password
```

### 4. Environment Variables

Set these environment variables for production:

```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
export ENVIRONMENT="production"
export DEBUG="false"
```

## Database Schema

### Users Table
- `id`: Primary key (auto-increment)
- `username`: Unique username (3+ characters, alphanumeric + underscore)
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `is_active`: Boolean flag for account status
- `is_verified`: Boolean flag for email verification
- `verification_token`: Token for email verification
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Chat History Table
- `id`: Primary key (auto-increment)
- `user_id`: Foreign key to users table
- `message`: User's message
- `response`: AI's response
- `model_used`: AI model used (e.g., gpt-4o-mini)
- `created_at`: Chat timestamp

### User Sessions Table
- `id`: Primary key (auto-increment)
- `user_id`: Foreign key to users table
- `session_token`: Unique session token
- `expires_at`: Session expiration timestamp
- `created_at`: Session creation timestamp
- `updated_at`: Last session update timestamp

## Database Migration

We use **Alembic** for database migrations:

```bash
# Initialize migrations (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Administration

### Using pgAdmin (Web Interface)

1. Open http://localhost:5050 in your browser
2. Login with:
   - Email: admin@chatbot.com
   - Password: admin
3. Add server connection:
   - Name: Chatbot Database
   - Host: postgres (or localhost if not using Docker)
   - Port: 5432
   - Username: postgres
   - Password: password

### Using Command Line

```bash
# Connect to database
psql -h localhost -U postgres -d chatbot

# Common commands
\l              # List databases
\c chatbot      # Connect to chatbot database
\dt             # List tables
\d users        # Describe users table
\q              # Quit
```

## Security Notes

### Development vs Production

- The default password is for development only
- In production, use strong passwords and proper authentication
- Consider using connection pooling for better performance
- Enable SSL/TLS for production connections

### Password Security

- All passwords are hashed using bcrypt
- Minimum password requirements: 8 characters, alphanumeric
- Email verification required before login
- JWT tokens expire after 30 days

## Backup and Restore

### Backup Database

```bash
# Full backup
pg_dump -h localhost -U postgres chatbot > backup.sql

# Schema only
pg_dump -h localhost -U postgres -s chatbot > schema.sql

# Data only
pg_dump -h localhost -U postgres -a chatbot > data.sql
```

### Restore Database

```bash
# Restore from backup
psql -h localhost -U postgres chatbot < backup.sql
```

## Monitoring

### Health Checks

The application includes database health checks:

```bash
# Check database connection
curl http://localhost:8000/health
```

### Performance Monitoring

Monitor these metrics:
- Connection pool usage
- Query execution time
- Active connections
- Lock contention
- Index usage

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if PostgreSQL is running
   - Verify connection settings
   - Check firewall settings

2. **Authentication Failed**
   - Verify username/password
   - Check pg_hba.conf configuration
   - Ensure user has proper permissions

3. **Database Does Not Exist**
   - Create database manually: `createdb chatbot`
   - Run initialization script: `psql -f init.sql`

4. **Migration Errors**
   - Check alembic version table
   - Verify migration files
   - Manual cleanup if needed

### Logs

Check PostgreSQL logs:
```bash
# Docker logs
docker-compose logs postgres

# System logs (varies by installation)
tail -f /var/log/postgresql/postgresql.log
```

## Development Tools

### Recommended Extensions

- **pgAdmin**: Web-based administration
- **DBeaver**: Universal database tool
- **DataGrip**: JetBrains database IDE
- **VS Code PostgreSQL**: Extension for VS Code

### Useful SQL Queries

```sql
-- Check active connections
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity 
WHERE datname = 'chatbot';

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Recent user registrations
SELECT username, email, created_at, is_verified 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;
``` 