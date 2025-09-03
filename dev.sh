#!/bin/bash

# GitHub Governance Factory - Development Startup Script
# Quick commands for common development tasks

set -e

echo "🏭 GitHub Governance Factory - Development Tools"
echo "================================================"

show_help() {
    echo "Available commands:"
    echo ""
    echo "  start         - Start the development server"
    echo "  test          - Run the test suite"
    echo "  test-docker   - Run Docker-based testing"
    echo "  build         - Build Docker containers"
    echo "  production    - Start production environment"
    echo "  clean         - Clean up containers and cache"
    echo "  help          - Show this help message"
    echo ""
}

case "${1:-help}" in
    start)
        echo "🚀 Starting development server..."
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    test)
        echo "🧪 Running test suite..."
        python -m pytest tests/ -v --tb=short
        ;;
    test-docker)
        echo "🐳 Running Docker-based tests..."
        ./run_tests.sh
        ;;
    build)
        echo "🏗️ Building Docker containers..."
        docker-compose build
        ;;
    production)
        echo "🚀 Starting production environment..."
        docker-compose -f docker-compose.production.yml up -d
        ;;
    clean)
        echo "🧹 Cleaning up..."
        docker-compose down -v
        docker system prune -f
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        ;;
    help)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
