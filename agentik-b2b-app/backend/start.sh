#!/bin/bash

# Agentik B2B Backend Startup Script

echo "🚀 Starting Agentik B2B Backend..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt .last_install ] || [ ! -f .last_install ]; then
    echo "📦 Installing/updating dependencies..."
    pip install -r requirements.txt
    touch .last_install
fi

# Check environment variables
echo "🔍 Checking environment variables..."
source .env

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL not set in .env file"
    exit 1
fi

if [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ SUPABASE_ANON_KEY not set in .env file"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo "⚠️  REDIS_URL not set, using default: redis://localhost:6379/0"
    export REDIS_URL="redis://localhost:6379/0"
fi

echo "✅ Environment variables check completed"

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "🏥 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"

# Run with uvicorn
exec python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
