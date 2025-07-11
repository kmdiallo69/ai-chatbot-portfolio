#!/bin/bash

# Database startup script for AI Chatbot
# This script sets up the PostgreSQL database for development

echo "🚀 Starting AI Chatbot Database Setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Navigate to database directory
cd "$(dirname "$0")"

echo "📦 Pulling PostgreSQL and pgAdmin Docker images..."
docker-compose pull

echo "🔧 Starting PostgreSQL and pgAdmin containers..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is running and healthy
echo "🔍 Checking PostgreSQL health..."
for i in {1..10}; do
    if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
        echo "✅ PostgreSQL is running successfully!"
        echo "   - Host: localhost"
        echo "   - Port: 5432"
        echo "   - Database: chatbot"
        echo "   - Username: postgres"
        echo "   - Password: password"
        break
    else
        echo "   Attempt $i/10: PostgreSQL not ready yet..."
        sleep 2
    fi
    
    if [ $i -eq 10 ]; then
        echo "❌ PostgreSQL failed to become ready. Check Docker logs:"
        docker-compose logs postgres
        exit 1
    fi
done

# Check if pgAdmin is running
if docker-compose ps | grep -q "pgadmin.*Up"; then
    echo "✅ pgAdmin is running successfully!"
    echo "   - URL: http://localhost:5050"
    echo "   - Email: admin@chatbot.com"
    echo "   - Password: admin"
else
    echo "⚠️  pgAdmin failed to start. Check Docker logs:"
    docker-compose logs pgadmin
fi

echo ""
echo "🎉 Database setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Install Python dependencies:"
echo "      cd ../Backend && pip install -r requirements.txt"
echo ""
echo "   2. Run database migrations:"
echo "      cd ../Backend && python -c \"from database_config import create_tables; create_tables()\""
echo ""
echo "   3. Start the backend server:"
echo "      cd ../Backend && uvicorn app:app --reload"
echo ""
echo "   4. Access pgAdmin at: http://localhost:5050"
echo ""
echo "🛠️  Useful commands:"
echo "   - Stop database: docker-compose down"
echo "   - View logs: docker-compose logs"
echo "   - Restart: docker-compose restart"
echo "   - Remove all data: docker-compose down -v"
echo "" 