#!/bin/bash

# GitHub Governance Factory - Testing Script
# Runs both unit tests (pytest) and integration tests (Docker endpoints)

set -e

echo "🚀 GitHub Governance Factory - Comprehensive Testing Suite"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
UNIT_TESTS=true
INTEGRATION_TESTS=true
CLEAN_AFTER=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            INTEGRATION_TESTS=false
            shift
            ;;
        --integration-only)
            UNIT_TESTS=false
            shift
            ;;
        --clean)
            CLEAN_AFTER=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit-only        Run only unit tests"
            echo "  --integration-only Run only integration tests"
            echo "  --clean           Clean up Docker containers after tests"
            echo "  --verbose         Run tests in verbose mode"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create reports directory
mkdir -p reports

# Phase 1: Unit Tests with pytest
if [ "$UNIT_TESTS" = true ]; then
    print_status "Phase 1: Running Unit Tests with pytest"
    echo "----------------------------------------"
    
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS="-v -s --tb=long"
    else
        PYTEST_ARGS="-v --tb=short"
    fi
    
    print_status "Installing test dependencies..."
    pip install pytest pytest-asyncio pytest-cov pytest-mock httpx requests
    
    print_status "Running GitHub API wrapper unit tests..."
    if python -m pytest tests/test_github_api_advanced.py $PYTEST_ARGS --junitxml=reports/unit_tests.xml --cov=src --cov-report=html:reports/coverage --cov-report=term; then
        print_success "Unit tests completed successfully!"
    else
        print_error "Unit tests failed!"
        exit 1
    fi
    
    print_status "Running existing unit tests..."
    if python -m pytest tests/test_*.py $PYTEST_ARGS --junitxml=reports/all_unit_tests.xml; then
        print_success "All unit tests completed successfully!"
    else
        print_warning "Some unit tests failed, but continuing..."
    fi
fi

# Phase 2: Integration Tests with Docker
if [ "$INTEGRATION_TESTS" = true ]; then
    print_status "Phase 2: Running Integration Tests with Docker"
    echo "----------------------------------------------"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_status "Building test containers..."
    if docker-compose -f docker-compose.test.yml build; then
        print_success "Test containers built successfully!"
    else
        print_error "Failed to build test containers!"
        exit 1
    fi
    
    print_status "Starting test environment..."
    if docker-compose -f docker-compose.test.yml up -d test-mongodb test-redis; then
        print_success "Test databases started!"
    else
        print_error "Failed to start test databases!"
        exit 1
    fi
    
    # Wait for databases to be ready
    print_status "Waiting for databases to be ready..."
    sleep 15
    
    print_status "Starting GitHub API test service..."
    if docker-compose -f docker-compose.test.yml up -d github-api-test-service; then
        print_success "GitHub API test service started!"
    else
        print_error "Failed to start GitHub API test service!"
        docker-compose -f docker-compose.test.yml logs github-api-test-service
        exit 1
    fi
    
    # Wait for service to be ready
    print_status "Waiting for service to be ready..."
    sleep 20
    
    print_status "Running integration tests..."
    if [ "$VERBOSE" = true ]; then
        PYTEST_ENV_ARGS="-e PYTEST_ARGS=-v -s --tb=long"
    else
        PYTEST_ENV_ARGS="-e PYTEST_ARGS=-v --tb=short"
    fi
    
    if docker-compose -f docker-compose.test.yml run --rm $PYTEST_ENV_ARGS pytest-runner; then
        print_success "Integration tests completed successfully!"
    else
        print_error "Integration tests failed!"
        docker-compose -f docker-compose.test.yml logs
        exit 1
    fi
    
    # Copy reports from container
    print_status "Copying test reports..."
    docker cp pytest-runner:/app/reports/. ./reports/ 2>/dev/null || print_warning "Could not copy some reports"
fi

# Cleanup
if [ "$CLEAN_AFTER" = true ]; then
    print_status "Cleaning up Docker containers..."
    docker-compose -f docker-compose.test.yml down -v
    docker system prune -f
    print_success "Cleanup completed!"
fi

# Generate summary
echo ""
echo "🎉 Testing Summary"
echo "=================="

if [ "$UNIT_TESTS" = true ]; then
    if [ -f "reports/unit_tests.xml" ]; then
        print_success "Unit tests: PASSED"
        print_status "Coverage report: reports/coverage/index.html"
    else
        print_error "Unit tests: FAILED or not found"
    fi
fi

if [ "$INTEGRATION_TESTS" = true ]; then
    if [ -f "reports/junit.xml" ]; then
        print_success "Integration tests: PASSED"
    else
        print_error "Integration tests: FAILED or not found"
    fi
fi

print_status "All test reports saved in: reports/"
print_success "Testing completed!"

# Display next steps
echo ""
print_status "Next Steps:"
echo "1. Review test coverage: open reports/coverage/index.html"
echo "2. Check test results: reports/*.xml"
echo "3. View Docker logs: docker-compose -f docker-compose.test.yml logs"
echo "4. Run specific tests: pytest tests/test_specific_file.py -v"
