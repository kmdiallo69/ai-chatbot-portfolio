#!/bin/bash

# Deploy Database to Azure Container Apps
# This script creates a PostgreSQL database container app

set -e

# Configuration
ACR_NAME="chatbotacr1752261237"
RESOURCE_GROUP="1-1b154f73-playground-sandbox"
LOCATION="eastus"
CONTAINER_APP_NAME="chatbot-database"
CONTAINER_APP_ENV="chatbot-env"

echo "🚀 Deploying Database Container to Azure Container Apps..."

# Check if Container Apps environment exists
if ! az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📝 Creating Container Apps environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
fi

# Deploy the database container
echo "📝 Deploying database container..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $ACR_NAME.azurecr.io/chatbot-postgres:latest \
    --target-port 5432 \
    --ingress external \
    --registry-server $ACR_NAME.azurecr.io \
    --query properties.configuration.ingress.fqdn \
    --cpu 1 \
    --memory 2Gi \
    --min-replicas 1 \
    --max-replicas 1 \
    --env-vars \
        POSTGRES_DB=chatbot \
        POSTGRES_USER=postgres \
        POSTGRES_PASSWORD=password \
        POSTGRES_HOST_AUTH_METHOD=trust

echo "✅ Database deployment completed!"
echo "📝 Database URL: Use the FQDN returned above with port 5432"
echo "📝 Connection details:"
echo "   - Database: chatbot"
echo "   - Username: postgres"
echo "   - Password: password"
echo "   - Port: 5432" 