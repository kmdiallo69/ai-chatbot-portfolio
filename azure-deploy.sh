#!/bin/bash
set -e

# Configuration
RESOURCE_GROUP="chatbot-rg"
LOCATION="eastus"
ACR_NAME="chatbotacr"
BACKEND_APP_NAME="chatbot-backend"
FRONTEND_APP_NAME="chatbot-frontend"
CONTAINER_ENV_NAME="chatbot-env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Azure Deployment Script${NC}"
echo -e "${GREEN}===============================${NC}"

# Check if required variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY environment variable is not set${NC}"
    echo "Please set it with: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

if [ -z "$GITHUB_REPO" ]; then
    echo -e "${RED}❌ Error: GITHUB_REPO environment variable is not set${NC}"
    echo "Please set it with: export GITHUB_REPO='https://github.com/username/repo'"
    exit 1
fi

echo -e "${YELLOW}📋 Prerequisites Check${NC}"
echo "✅ OpenAI API Key: Set"
echo "✅ GitHub Repository: $GITHUB_REPO"

# Login to Azure
echo -e "${YELLOW}🔐 Checking Azure Login${NC}"
if ! az account show &> /dev/null; then
    echo "Please login to Azure first..."
    az login
fi

echo -e "${GREEN}✅ Azure login successful${NC}"

# Create Resource Group
echo -e "${YELLOW}📦 Creating Resource Group${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✅ Resource Group created${NC}"

# Create Container Registry
echo -e "${YELLOW}🏗️ Creating Container Registry${NC}"
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
echo -e "${GREEN}✅ Container Registry created${NC}"

# Login to Container Registry
echo -e "${YELLOW}🔑 Logging into Container Registry${NC}"
az acr login --name $ACR_NAME
echo -e "${GREEN}✅ Container Registry login successful${NC}"

# Create Container Apps Environment
echo -e "${YELLOW}🌐 Creating Container Apps Environment${NC}"
az containerapp env create \
  --name $CONTAINER_ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
echo -e "${GREEN}✅ Container Apps Environment created${NC}"

# Build and push backend image
echo -e "${YELLOW}🔨 Building Backend Docker Image${NC}"
docker build -t $ACR_NAME.azurecr.io/chatbot-backend:latest -f Backend/Dockerfile.azure ./Backend
echo -e "${GREEN}✅ Backend image built${NC}"

echo -e "${YELLOW}📤 Pushing Backend Image${NC}"
docker push $ACR_NAME.azurecr.io/chatbot-backend:latest
echo -e "${GREEN}✅ Backend image pushed${NC}"

# Deploy backend to Container Apps
echo -e "${YELLOW}🚀 Deploying Backend to Container Apps${NC}"
az containerapp create \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV_NAME \
  --image $ACR_NAME.azurecr.io/chatbot-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --env-vars OPENAI_API_KEY="$OPENAI_API_KEY" \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.25 \
  --memory 0.5Gi
echo -e "${GREEN}✅ Backend deployed to Container Apps${NC}"

# Get backend URL
echo -e "${YELLOW}🔍 Getting Backend URL${NC}"
BACKEND_URL=$(az containerapp show \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv)
BACKEND_URL="https://$BACKEND_URL"
echo -e "${GREEN}✅ Backend URL: $BACKEND_URL${NC}"

# Deploy frontend to Static Web Apps
echo -e "${YELLOW}🌐 Deploying Frontend to Static Web Apps${NC}"
az staticwebapp create \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --source $GITHUB_REPO \
  --branch main \
  --app-location "/Frontend" \
  --api-location "" \
  --output-location ".next" \
  --login-with-github
echo -e "${GREEN}✅ Frontend deployed to Static Web Apps${NC}"

# Configure frontend environment variables
echo -e "${YELLOW}⚙️ Configuring Frontend Environment Variables${NC}"
az staticwebapp appsettings set \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --setting-names NEXT_PUBLIC_API_URL="$BACKEND_URL"
echo -e "${GREEN}✅ Frontend environment variables configured${NC}"

# Get frontend URL
echo -e "${YELLOW}🔍 Getting Frontend URL${NC}"
FRONTEND_URL=$(az staticwebapp show \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "defaultHostname" \
  --output tsv)
FRONTEND_URL="https://$FRONTEND_URL"
echo -e "${GREEN}✅ Frontend URL: $FRONTEND_URL${NC}"

# Update backend CORS settings
echo -e "${YELLOW}🔐 Updating Backend CORS Settings${NC}"
az containerapp update \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars CORS_ORIGINS="$FRONTEND_URL"
echo -e "${GREEN}✅ Backend CORS settings updated${NC}"

# Final summary
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}========================${NC}"
echo -e "🌐 Frontend URL: ${YELLOW}$FRONTEND_URL${NC}"
echo -e "⚙️ Backend URL: ${YELLOW}$BACKEND_URL${NC}"
echo -e "📊 Resource Group: ${YELLOW}$RESOURCE_GROUP${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Visit your frontend URL to test the application"
echo "2. Monitor logs with: az containerapp logs show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "3. Set up custom domain (optional)"
echo "4. Configure monitoring and alerts"
echo ""
echo -e "${GREEN}🚀 Your chatbot is now live on the internet!${NC}" 