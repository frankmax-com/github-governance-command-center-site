@echo off
REM GitHub Governance Factory - Startup Script
REM Starts all microservices for development

echo Starting GitHub Governance Factory...
echo =====================================

REM Check if Python virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables if .env file exists
if exist ".env" (
    echo Loading environment variables from .env file...
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Start all microservices
echo Starting all microservices...
python cli.py serve --service all

pause
