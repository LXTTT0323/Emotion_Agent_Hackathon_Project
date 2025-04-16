@echo off
echo Starting Emotion Agent Backend (Mock Mode)...

:: Go to the project root directory
cd /d "%~dp0"

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python could not be found. Please install Python 3 and try again.
    exit /b 1
)

:: Create a new virtual environment for mock mode
if not exist mock_venv (
    echo Creating new virtual environment for mock mode...
    python -m venv mock_venv
)

:: Activate the virtual environment
call mock_venv\Scripts\activate.bat

:: Clear any existing environment variables
set USE_MOCK_RESPONSES=
set OPENAI_API_KEY=
set OPENAI_MODEL=
set OPENAI_MAX_TOKENS=
set OPENAI_TEMPERATURE=

:: Install only necessary packages (without Semantic Kernel)
echo Installing basic requirements for mock mode...
pip install fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 jinja2==3.1.2 python-multipart==0.0.6

:: Ensure the .env file exists with mock mode enabled
echo Setting up mock environment...
echo USE_MOCK_RESPONSES=1 > backend\.env
echo PORT=8000 >> backend\.env
echo HOST=0.0.0.0 >> backend\.env
echo DEBUG=True >> backend\.env

:: Run the server
echo Starting backend server in mock mode...
cd backend
python main.py

:: Deactivate virtual environment on exit
call mock_venv\Scripts\deactivate.bat 