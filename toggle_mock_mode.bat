@echo off
echo Emotion Agent - 切换模拟模式

:: 进入项目根目录
cd /d "%~dp0"

:: 读取当前.env文件
set ENV_FILE=backend\.env
set MOCK_ENABLED=
for /f "tokens=1,2 delims==" %%a in (%ENV_FILE%) do (
    if "%%a"=="USE_MOCK_RESPONSES" set MOCK_ENABLED=%%b
)

:: 切换模式
if "%MOCK_ENABLED%"=="1" (
    echo 当前设置：模拟模式已启用
    echo 切换到真实OpenAI模式...
    
    :: 创建临时文件
    (for /f "tokens=1,* delims==" %%a in (%ENV_FILE%) do (
        if "%%a"=="USE_MOCK_RESPONSES" (
            echo USE_MOCK_RESPONSES=0
        ) else (
            echo %%a=%%b
        )
    )) > %ENV_FILE%.tmp
    
    :: 替换原文件
    move /y %ENV_FILE%.tmp %ENV_FILE% > nul
    
    echo 模式已切换！现在使用真实OpenAI模式。
    echo 请确保您的AZURE_OPENAI_API_KEY已正确设置。
) else (
    echo 当前设置：使用真实OpenAI模式
    echo 切换到模拟模式...
    
    :: 创建临时文件
    (for /f "tokens=1,* delims==" %%a in (%ENV_FILE%) do (
        if "%%a"=="USE_MOCK_RESPONSES" (
            echo USE_MOCK_RESPONSES=1
        ) else (
            echo %%a=%%b
        )
    )) > %ENV_FILE%.tmp
    
    :: 替换原文件
    move /y %ENV_FILE%.tmp %ENV_FILE% > nul
    
    echo 模式已切换！现在使用模拟模式。
    echo 不需要OpenAI API密钥即可运行。
)

echo.
echo 当前模式设置为：
findstr "USE_MOCK_RESPONSES" %ENV_FILE%
echo.
echo 按任意键继续...
pause > nul 