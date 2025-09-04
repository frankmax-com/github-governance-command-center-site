#!/bin/bash

# GitHub Governance Factory - Swagger Documentation in Docker
# Complete API documentation and testing environment

echo "🐳 GitHub Governance Factory - Swagger Documentation (Docker)"
echo "=============================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GitHub token not set. API will run in demo mode."
    echo "   Set GITHUB_TOKEN environment variable for full functionality:"
    echo "   export GITHUB_TOKEN=your_github_token_here"
    echo ""
else
    echo "✅ GitHub token configured"
    echo ""
fi

echo "🏗️  Building and starting Swagger documentation services..."
echo ""

# Build and start the services
docker-compose -f docker-compose.swagger.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.swagger.yml ps

echo ""
echo "🎉 GitHub Governance Factory Swagger Documentation is ready!"
echo ""
echo "📚 Access Points:"
echo "   • Main API Documentation:    http://localhost:8000/docs"
echo "   • Alternative Documentation: http://localhost:8000/redoc"
echo "   • OpenAPI JSON Schema:       http://localhost:8000/openapi.json"
echo "   • Standalone Swagger UI:     http://localhost:8080"
echo "   • Standalone ReDoc:          http://localhost:8081"
echo ""
echo "🔍 Test Endpoints:"
echo "   • Health Check:              http://localhost:8000/health"
echo "   • Platform Status:           http://localhost:8000/status"
echo "   • Root (redirects to docs):  http://localhost:8000/"
echo ""
echo "🎯 Platform Features Available:"
echo "   • 91.4% GitHub API Coverage (96/105 functions)"
echo "   • Enterprise Repository Management"
echo "   • AI-Powered Issue Generation"
echo "   • Comprehensive Analytics"
echo "   • Interactive API Testing"
echo ""
echo "🛠️  Management Commands:"
echo "   • View logs:    docker-compose -f docker-compose.swagger.yml logs -f"
echo "   • Stop services: docker-compose -f docker-compose.swagger.yml down"
echo "   • Restart:      docker-compose -f docker-compose.swagger.yml restart"
echo ""
echo "Press Ctrl+C to view logs, or run 'docker-compose -f docker-compose.swagger.yml down' to stop"

# Follow logs
docker-compose -f docker-compose.swagger.yml logs -f swagger-api
