@echo off
echo 初始化 Azure Cosmos DB...

:: Go to the project root directory
cd /d "%~dp0"

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python could not be found. Please install Python 3 and try again.
    exit /b 1
)

:: Check if the virtual environment exists, if not create it
if not exist mock_venv (
    echo Creating virtual environment...
    python -m venv mock_venv
)

:: Activate the virtual environment
call mock_venv\Scripts\activate.bat

:: Install requirements
echo Installing required packages...
pip install -r backend\requirements.txt

:: Run the initialization script
echo Running Cosmos DB initialization script...
python -m backend.scripts.init_cosmos_db

:: Deactivate virtual environment on exit
call mock_venv\Scripts\deactivate.bat

echo 完成！可能出现的警告通常表示数据已存在，可以忽略。
pause 