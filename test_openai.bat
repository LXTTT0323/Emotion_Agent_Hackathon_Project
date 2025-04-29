@echo off
echo 测试Azure OpenAI连接...

:: 进入项目根目录
cd /d "%~dp0"

:: 检查Python是否安装
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python未找到。请安装Python 3并重试。
    exit /b 1
)

:: 激活虚拟环境
if exist venv (
    call venv\Scripts\activate.bat
) else if exist mock_venv (
    call mock_venv\Scripts\activate.bat
) else (
    echo 找不到虚拟环境，将使用系统Python。
)

:: 运行测试脚本
python -m backend.scripts.test_openai_connection

:: 等待用户输入
pause 