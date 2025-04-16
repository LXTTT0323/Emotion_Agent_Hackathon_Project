@echo off
echo Starting Emotion Agent Backend...

:: Go to the project root directory
cd /d "%~dp0"

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python could not be found. Please install Python 3 and try again.
    exit /b 1
)

:: Set MOCK_MODE to 1 to use mock data without Semantic Kernel
set MOCK_MODE=1

:: Check if the virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Install basic requirements without semantic kernel if in mock mode
if %MOCK_MODE% EQU 1 (
    echo Running in MOCK MODE - using simulated responses without Semantic Kernel
    echo Installing basic requirements...
    pip install fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 jinja2==3.1.2 python-multipart==0.0.6
) else (
    :: Install full requirements
    echo Installing all required packages...
    pip install -r backend\requirements.txt
)

:: Set environment variables for mock mode
if %MOCK_MODE% EQU 1 (
    echo Setting up mock environment...
    set USE_MOCK_RESPONSES=1
    echo USE_MOCK_RESPONSES=1 > backend\.env
)

:: Run the server
echo Starting backend server...
cd backend
python main.py

:: Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat 