@echo off
chcp 65001 >nul
echo.
echo ================================================================
echo              QET Element Translator - Windows
echo                    一键启动翻译工具
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo.
    echo 请先安装 Python 3.7 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if translate_config.json exists
if not exist "translate_config.json" (
    echo [错误] 未找到配置文件 translate_config.json！
    echo.
    pause
    exit /b 1
)

REM Check if scripts/translate_to_result.py exists
if not exist "scripts\translate_to_result.py" (
    echo [错误] 未找到脚本文件 scripts/translate_to_result.py！
    echo.
    pause
    exit /b 1
)

echo [1/3] 检查环境...
echo ✓ Python 已安装
echo ✓ 配置文件已找到
echo ✓ 脚本文件已找到
echo.
echo [2/3] 准备启动...
echo.

REM Run the translation script
python scripts/translate_to_result.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo [错误] 翻译失败！
    echo(请检查：
    echo(  1. translate_config.json 配置是否正确
    echo(  2. 网络连接是否正常
    echo(  3. API 服务是否可用
    echo.
) else (
    echo.
    echo ================================================================
    echo                       ✓ 翻译完成！
    echo ================================================================
    echo.
    echo 处理结果在: result/ 文件夹
    echo.
)

pause
