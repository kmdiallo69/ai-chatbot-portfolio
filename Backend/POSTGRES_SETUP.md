# PostgreSQL Database Setup

This guide will help you set up PostgreSQL for the chatbot application.

## Option 1: Using Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Steps

1. **Start PostgreSQL with Docker:**
   ```bash
   docker-compose -f docker-compose.postgres.yml up -d
   ```

2. **Verify PostgreSQL is running:**
   ```bash
   docker-compose -f docker-compose.postgres.yml ps
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python init_db.py
   ```

5. **Set environment variable:**
   ```bash
   export DATABASE_URL="postgresql://chatbot_user:chatbot_password@localhost:5432/chatbot_db"
   ```

### Access PgAdmin (Optional)
- URL: http://localhost:5050
- Email: admin@chatbot.com
- Password: admin

## Option 2: Local PostgreSQL Installation

### Prerequisites
- PostgreSQL installed locally

### macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Windows:
Download and install from https://www.postgresql.org/download/windows/

### Setup Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the PostgreSQL setup script:**
   ```bash
   python setup_postgres.py
   ```

3. **Initialize the database:**
   ```bash
   python init_db.py
   ```

4. **Set the DATABASE_URL environment variable** (shown in setup_postgres.py output)

## Configuration

The database uses these default settings:
- Database: `chatbot_db`
- User: `chatbot_user`
- Password: `chatbot_password`
- Host: `localhost`
- Port: `5432`

You can override these with environment variables:
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=chatbot_db
export POSTGRES_USER=chatbot_user
export POSTGRES_PASSWORD=chatbot_password
```

## Database Schema

The database includes these tables:
- `users` - User sessions and profiles
- `conversations` - Chat conversations
- `messages` - Individual chat messages
- `api_usage` - API usage tracking for analytics

## Troubleshooting

### Connection Issues
1. Verify PostgreSQL is running:
   ```bash
   pg_isready -h localhost -p 5432
   ```

2. Check configuration:
   ```bash
   python postgres_config.py
   ```

3. Test database connection:
   ```bash
   python -c "from database import health_check; print('✅ OK' if health_check() else '❌ Failed')"
   ```

### Common Errors
- **Connection refused**: PostgreSQL is not running
- **Authentication failed**: Check username/password
- **Database does not exist**: Run `python setup_postgres.py` first

## Production Deployment

For production, use a managed PostgreSQL service:
- **Azure**: Azure Database for PostgreSQL
- **AWS**: RDS PostgreSQL
- **Google Cloud**: Cloud SQL for PostgreSQL

Set the `DATABASE_URL` environment variable to your production database connection string.

## Database Migrations

For schema changes, we use Alembic:
```bash
# Initialize migrations (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head
``` 