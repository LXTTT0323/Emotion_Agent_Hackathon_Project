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

:: Check if the virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Install requirements
echo Installing required packages...
pip install -r backend\requirements.txt

:: Run the server
echo Starting backend server...
cd backend
python main.py

:: Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat 