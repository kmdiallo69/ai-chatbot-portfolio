#!/bin/bash

# Build and Push Database Image to Azure Container Registry
# This script builds the custom PostgreSQL image and pushes it to ACR

set -e

# Configuration
ACR_NAME="chatbotacr1752261237"
IMAGE_NAME="chatbot-postgres"
TAG="latest"

echo "🔨 Building database image..."
docker build -t $IMAGE_NAME:$TAG .

echo "🏷️  Tagging image for ACR..."
docker tag $IMAGE_NAME:$TAG $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

echo "🔑 Logging into ACR..."
az acr login --name $ACR_NAME

echo "📤 Pushing image to ACR..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

echo "✅ Build and push completed!"
echo "📝 Image: $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"
echo "📝 To deploy: Run ./deploy-database.sh" 