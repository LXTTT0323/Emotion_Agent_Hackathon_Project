@echo off
setlocal enabledelayedexpansion
echo 开始运行情感代理上下文存储系统测试...
echo.

REM 检查Python是否已安装
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到Python安装。请安装Python 3.6或更高版本。
    exit /b 1
)

echo 使用Python运行测试...
echo.

REM 检查context_store.py文件是否存在
if not exist "context_store.py" (
    echo 错误: 未找到context_store.py文件。请确保你在正确的目录中。
    exit /b 1
)

REM 检查test_context_store.py文件是否存在
if not exist "test_context_store.py" (
    echo 错误: 未找到test_context_store.py文件。请确保你在正确的目录中。
    exit /b 1
)

REM 运行测试脚本
echo 运行测试脚本...
python test_context_store.py

REM 检查测试是否成功
if %ERRORLEVEL% EQU 0 (
    echo.
    echo 测试成功完成！
    
    REM 检查是否生成了memory_updated.json文件
    if exist "memory_updated.json" (
        for %%I in (memory_updated.json) do set FILE_SIZE=%%~zI
        echo 生成的memory_updated.json文件大小: !FILE_SIZE! 字节
    ) else (
        echo 警告: 未找到memory_updated.json文件。
    )
) else (
    echo.
    echo 测试运行失败。请查看上面的错误信息。
)

echo.
echo 如需更多信息，请参考README.md文件。
pause
endlocal 