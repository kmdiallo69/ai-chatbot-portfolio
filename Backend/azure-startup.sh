#!/bin/bash
set -e

echo "Starting Azure Container Apps deployment..."
echo "Environment: $NODE_ENV"
echo "OpenAI API Key configured: $([ -n "$OPENAI_API_KEY" ] && echo "Yes" || echo "No")"

# Start the FastAPI application
exec python -m uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1 