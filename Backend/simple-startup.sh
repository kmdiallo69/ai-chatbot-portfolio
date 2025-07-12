#!/bin/bash
set -e

echo "Starting Simple AI Chatbot API..."
echo "Environment: $ENVIRONMENT"
echo "OpenAI API Key configured: $([ -n "$OPENAI_API_KEY" ] && echo "Yes" || echo "No")"

# Start the simple FastAPI application
exec python -m uvicorn simple_app:app --host 0.0.0.0 --port 8000 --workers 1 