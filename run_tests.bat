@echo off
REM GitHub Governance Factory - Testing Script for Windows
REM Runs both unit tests (pytest) and integration tests (Docker endpoints)

setlocal enabledelayedexpansion

echo.
echo 🚀 GitHub Governance Factory - Comprehensive Testing Suite
echo ==========================================================

REM Parse command line arguments
set UNIT_TESTS=true
set INTEGRATION_TESTS=true
set CLEAN_AFTER=false
set VERBOSE=false

:parse_args
if "%~1"=="--unit-only" (
    set INTEGRATION_TESTS=false
    shift
    goto parse_args
)
if "%~1"=="--integration-only" (
    set UNIT_TESTS=false
    shift
    goto parse_args
)
if "%~1"=="--clean" (
    set CLEAN_AFTER=true
    shift
    goto parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%~1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo.
    echo Options:
    echo   --unit-only        Run only unit tests
    echo   --integration-only Run only integration tests
    echo   --clean           Clean up Docker containers after tests
    echo   --verbose         Run tests in verbose mode
    echo   --help            Show this help message
    exit /b 0
)
if not "%~1"=="" (
    echo [ERROR] Unknown option: %1
    exit /b 1
)

REM Create reports directory
if not exist reports mkdir reports

REM Phase 1: Unit Tests with pytest
if "%UNIT_TESTS%"=="true" (
    echo.
    echo [INFO] Phase 1: Running Unit Tests with pytest
    echo ----------------------------------------
    
    if "%VERBOSE%"=="true" (
        set PYTEST_ARGS=-v -s --tb=long
    ) else (
        set PYTEST_ARGS=-v --tb=short
    )
    
    echo [INFO] Installing test dependencies...
    pip install pytest pytest-asyncio pytest-cov pytest-mock httpx requests
    
    echo [INFO] Running GitHub API wrapper unit tests...
    python -m pytest tests/test_github_api_advanced.py !PYTEST_ARGS! --junitxml=reports/unit_tests.xml --cov=src --cov-report=html:reports/coverage --cov-report=term
    if errorlevel 1 (
        echo [ERROR] Unit tests failed!
        exit /b 1
    )
    echo [SUCCESS] Unit tests completed successfully!
    
    echo [INFO] Running existing unit tests...
    python -m pytest tests/test_*.py !PYTEST_ARGS! --junitxml=reports/all_unit_tests.xml
    if errorlevel 1 (
        echo [WARNING] Some unit tests failed, but continuing...
    ) else (
        echo [SUCCESS] All unit tests completed successfully!
    )
)

REM Phase 2: Integration Tests with Docker
if "%INTEGRATION_TESTS%"=="true" (
    echo.
    echo [INFO] Phase 2: Running Integration Tests with Docker
    echo ----------------------------------------------
    
    REM Check if Docker is running
    docker info >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker is not running. Please start Docker and try again.
        exit /b 1
    )
    
    echo [INFO] Building test containers...
    docker-compose -f docker-compose.test.yml build
    if errorlevel 1 (
        echo [ERROR] Failed to build test containers!
        exit /b 1
    )
    echo [SUCCESS] Test containers built successfully!
    
    echo [INFO] Starting test environment...
    docker-compose -f docker-compose.test.yml up -d test-mongodb test-redis
    if errorlevel 1 (
        echo [ERROR] Failed to start test databases!
        exit /b 1
    )
    echo [SUCCESS] Test databases started!
    
    REM Wait for databases to be ready
    echo [INFO] Waiting for databases to be ready...
    timeout /t 15 /nobreak >nul
    
    echo [INFO] Starting GitHub API test service...
    docker-compose -f docker-compose.test.yml up -d github-api-test-service
    if errorlevel 1 (
        echo [ERROR] Failed to start GitHub API test service!
        docker-compose -f docker-compose.test.yml logs github-api-test-service
        exit /b 1
    )
    echo [SUCCESS] GitHub API test service started!
    
    REM Wait for service to be ready
    echo [INFO] Waiting for service to be ready...
    timeout /t 20 /nobreak >nul
    
    echo [INFO] Running integration tests...
    if "%VERBOSE%"=="true" (
        set PYTEST_ENV_ARGS=-e PYTEST_ARGS=-v -s --tb=long
    ) else (
        set PYTEST_ENV_ARGS=-e PYTEST_ARGS=-v --tb=short
    )
    
    docker-compose -f docker-compose.test.yml run --rm !PYTEST_ENV_ARGS! pytest-runner
    if errorlevel 1 (
        echo [ERROR] Integration tests failed!
        docker-compose -f docker-compose.test.yml logs
        exit /b 1
    )
    echo [SUCCESS] Integration tests completed successfully!
    
    REM Copy reports from container
    echo [INFO] Copying test reports...
    docker cp pytest-runner:/app/reports/. ./reports/ 2>nul || echo [WARNING] Could not copy some reports
)

REM Cleanup
if "%CLEAN_AFTER%"=="true" (
    echo [INFO] Cleaning up Docker containers...
    docker-compose -f docker-compose.test.yml down -v
    docker system prune -f
    echo [SUCCESS] Cleanup completed!
)

REM Generate summary
echo.
echo 🎉 Testing Summary
echo ==================

if "%UNIT_TESTS%"=="true" (
    if exist "reports\unit_tests.xml" (
        echo [SUCCESS] Unit tests: PASSED
        echo [INFO] Coverage report: reports\coverage\index.html
    ) else (
        echo [ERROR] Unit tests: FAILED or not found
    )
)

if "%INTEGRATION_TESTS%"=="true" (
    if exist "reports\junit.xml" (
        echo [SUCCESS] Integration tests: PASSED
    ) else (
        echo [ERROR] Integration tests: FAILED or not found
    )
)

echo [INFO] All test reports saved in: reports\
echo [SUCCESS] Testing completed!

REM Display next steps
echo.
echo [INFO] Next Steps:
echo 1. Review test coverage: open reports\coverage\index.html
echo 2. Check test results: reports\*.xml
echo 3. View Docker logs: docker-compose -f docker-compose.test.yml logs
echo 4. Run specific tests: pytest tests\test_specific_file.py -v

endlocal
