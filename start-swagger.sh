#!/bin/bash

# GitHub Governance Factory - Swagger Documentation Server
# Start the API server with comprehensive OpenAPI/Swagger documentation

echo "🚀 Starting GitHub Governance Factory with Swagger Documentation"
echo "================================================================="

# Set environment variables for development
export ENVIRONMENT=development
export LOG_LEVEL=INFO

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GitHub token not set. Some endpoints will require authentication."
    echo "   Set GITHUB_TOKEN environment variable for full functionality."
    echo ""
fi

echo "📚 API Documentation will be available at:"
echo "   • Swagger UI: http://localhost:8000/docs"
echo "   • ReDoc:      http://localhost:8000/redoc"
echo "   • OpenAPI:    http://localhost:8000/openapi.json"
echo ""

echo "🔍 Quick Test Endpoints:"
echo "   • Health Check: http://localhost:8000/health"
echo "   • Status:       http://localhost:8000/status"
echo "   • Root:         http://localhost:8000/"
echo ""

echo "🎯 Platform Features:"
echo "   • 91.4% GitHub API Coverage (96/105 functions)"
echo "   • Enterprise Repository Management"
echo "   • AI-Powered Issue Generation"
echo "   • Comprehensive Analytics"
echo "   • Production Docker Infrastructure"
echo ""

# Start the server
echo "Starting FastAPI server with uvicorn..."
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000 --log-level info
