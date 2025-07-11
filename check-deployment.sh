#!/bin/bash

# Check deployment status script
echo "==============================="
echo "Checking Deployment Status"
echo "==============================="

# Backend URL
BACKEND_URL="https://chatbot-backend-1752247339.livelyplant-d44fb3c4.eastus.azurecontainerapps.io"

# Frontend URL
FRONTEND_URL="https://proud-moss-066b9b810.1.azurestaticapps.net"

echo ""
echo "1. Testing Backend Health..."
echo "URL: $BACKEND_URL/health"
curl -s "$BACKEND_URL/health" || echo "Backend health check failed"

echo ""
echo ""
echo "2. Testing Backend Chat API..."
echo "URL: $BACKEND_URL/chat"
response=$(curl -s -X POST "$BACKEND_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{"message": "Test deployment"}' | jq -r '.response // "No response"')
echo "Response: $response"

echo ""
echo ""
echo "3. Testing Frontend..."
echo "URL: $FRONTEND_URL"
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
echo "Frontend Status Code: $frontend_status"

if [ "$frontend_status" = "200" ]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
fi

echo ""
echo ""
echo "4. Checking if deployment is complete..."
echo "Please visit: $FRONTEND_URL"
echo "Look for the build information (ℹ️ button) to verify the new deployment"
echo ""
echo "Expected version: 2025-01-11-v2"
echo "Expected API URL: $BACKEND_URL"
echo ""
echo "If the version doesn't match, wait a few more minutes for deployment to complete." 