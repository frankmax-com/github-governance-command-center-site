# GitHub Governance Factory - Swagger Documentation Server (PowerShell)
# Start the API server with comprehensive OpenAPI/Swagger documentation

Write-Host "🚀 Starting GitHub Governance Factory with Swagger Documentation" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan

# Set environment variables for development
$env:ENVIRONMENT = "development"
$env:LOG_LEVEL = "INFO"

# Check if GitHub token is set
if (-not $env:GITHUB_TOKEN) {
    Write-Host "⚠️  GitHub token not set. Some endpoints will require authentication." -ForegroundColor Yellow
    Write-Host "   Set GITHUB_TOKEN environment variable for full functionality." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "📚 API Documentation will be available at:" -ForegroundColor Magenta
Write-Host "   • Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • ReDoc:      http://localhost:8000/redoc" -ForegroundColor White  
Write-Host "   • OpenAPI:    http://localhost:8000/openapi.json" -ForegroundColor White
Write-Host ""

Write-Host "🔍 Quick Test Endpoints:" -ForegroundColor Cyan
Write-Host "   • Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "   • Status:       http://localhost:8000/status" -ForegroundColor White
Write-Host "   • Root:         http://localhost:8000/" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Platform Features:" -ForegroundColor Yellow
Write-Host "   • 91.4% GitHub API Coverage (96/105 functions)" -ForegroundColor White
Write-Host "   • Enterprise Repository Management" -ForegroundColor White
Write-Host "   • AI-Powered Issue Generation" -ForegroundColor White
Write-Host "   • Comprehensive Analytics" -ForegroundColor White
Write-Host "   • Production Docker Infrastructure" -ForegroundColor White
Write-Host ""

# Start the server
Write-Host "Starting FastAPI server with uvicorn..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

# Start the API server
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000 --log-level info
