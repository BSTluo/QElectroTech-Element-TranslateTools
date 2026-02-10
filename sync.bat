@echo off
chcp 65001 >nul
echo.
echo ================================================================
echo            QET Element Library Sync Tool
echo              QElectroTech 元件库同步工具
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

REM Check if scripts exist
if not exist "scripts\sync_from_qet.py" (
    echo [错误] 未找到同步脚本 scripts/sync_from_qet.py！
    echo.
    pause
    exit /b 1
)

echo [检查] 环境准备...
echo ✓ Python 已安装
echo ✓ 同步脚本已找到
echo.

REM Run sync script
python scripts/sync_from_qet.py

REM Check result
if errorlevel 1 (
    echo.
    echo [失败] 同步未完成
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo                   ✓ 同步完成！
echo ================================================================
echo.
echo 下一步: 运行 run.bat 或 run_with_sync.bat 开始翻译
echo.
pause
