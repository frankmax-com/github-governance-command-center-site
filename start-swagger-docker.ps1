# GitHub Governance Factory - Swagger Documentation in Docker (PowerShell)
# Complete API documentation and testing environment

Write-Host "🐳 GitHub Governance Factory - Swagger Documentation (Docker)" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check for GitHub token
if (-not $env:GITHUB_TOKEN) {
    Write-Host "⚠️  GitHub token not set. API will run in demo mode." -ForegroundColor Yellow
    Write-Host "   Set GITHUB_TOKEN environment variable for full functionality:" -ForegroundColor Yellow
    Write-Host "   `$env:GITHUB_TOKEN = 'your_github_token_here'" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ GitHub token configured" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🏗️  Building and starting Swagger documentation services..." -ForegroundColor Blue
Write-Host ""

# Build and start the services
docker-compose -f docker-compose.swagger.yml up --build -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep 15

# Check service status
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Magenta
docker-compose -f docker-compose.swagger.yml ps

Write-Host ""
Write-Host "🎉 GitHub Governance Factory Swagger Documentation is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Access Points:" -ForegroundColor Cyan
Write-Host "   • Main API Documentation:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Alternative Documentation: http://localhost:8000/redoc" -ForegroundColor White
Write-Host "   • OpenAPI JSON Schema:       http://localhost:8000/openapi.json" -ForegroundColor White
Write-Host "   • Standalone Swagger UI:     http://localhost:8080" -ForegroundColor White
Write-Host "   • Standalone ReDoc:          http://localhost:8081" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Test Endpoints:" -ForegroundColor Yellow
Write-Host "   • Health Check:              http://localhost:8000/health" -ForegroundColor White
Write-Host "   • Platform Status:           http://localhost:8000/status" -ForegroundColor White
Write-Host "   • Root (redirects to docs):  http://localhost:8000/" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Platform Features Available:" -ForegroundColor Magenta
Write-Host "   • 91.4% GitHub API Coverage (96/105 functions)" -ForegroundColor White
Write-Host "   • Enterprise Repository Management" -ForegroundColor White
Write-Host "   • AI-Powered Issue Generation" -ForegroundColor White
Write-Host "   • Comprehensive Analytics" -ForegroundColor White
Write-Host "   • Interactive API Testing" -ForegroundColor White
Write-Host ""
Write-Host "🛠️  Management Commands:" -ForegroundColor Blue
Write-Host "   • View logs:     docker-compose -f docker-compose.swagger.yml logs -f" -ForegroundColor White
Write-Host "   • Stop services: docker-compose -f docker-compose.swagger.yml down" -ForegroundColor White
Write-Host "   • Restart:       docker-compose -f docker-compose.swagger.yml restart" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to view logs, or run 'docker-compose -f docker-compose.swagger.yml down' to stop" -ForegroundColor Yellow

# Follow logs
docker-compose -f docker-compose.swagger.yml logs -f swagger-api
