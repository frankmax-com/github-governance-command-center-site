@echo off
REM GitHub Governance Factory - Development Testing Script
REM Tests microservices implementation

echo Testing GitHub Governance Factory Implementation...
echo =================================================

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Run start.bat first.
    pause
    exit /b 1
)

REM Run configuration validation
echo.
echo [1/4] Validating Configuration...
python cli.py validate-config

if %errorlevel% neq 0 (
    echo Configuration validation failed!
    pause
    exit /b 1
)

REM Run health check
echo.
echo [2/4] Running Health Check...
python cli.py health-check --format table

if %errorlevel% neq 0 (
    echo Health check failed!
    pause
    exit /b 1
)

REM Run unit tests
echo.
echo [3/4] Running Unit Tests...
python -m pytest tests/ -v

if %errorlevel% neq 0 (
    echo Unit tests failed!
    pause
    exit /b 1
)

REM Test governance generation (sample)
echo.
echo [4/4] Testing Governance Generation...
python cli.py generate-governance ^
    --name "Test Project" ^
    --description "Sample project for testing microservices implementation" ^
    --requirements "Authentication system" ^
    --requirements "Database integration" ^
    --requirements "API endpoints" ^
    --stakeholders "developer@company.com" ^
    --priority "high" ^
    --output test_governance_output.json

if %errorlevel% neq 0 (
    echo Governance generation test failed!
    pause
    exit /b 1
)

echo.
echo ================================
echo All tests completed successfully!
echo ================================
echo.
echo Generated governance structure saved to: test_governance_output.json
echo.
echo Next steps:
echo 1. Review the generated governance structure
echo 2. Configure GitHub repository settings
echo 3. Run: python cli.py generate-issues --help for GitHub issue generation
echo.

pause
