@echo off
chcp 65001 >nul
echo.
echo ================================================================
echo          QET Element Auto-Sync and Translator
echo                 自动同步并翻译元件库
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

REM Check if scripts exist
if not exist "scripts\sync_from_qet.py" (
    echo [错误] 未找到同步脚本 scripts/sync_from_qet.py！
    echo.
    pause
    exit /b 1
)

if not exist "scripts\translate_to_result.py" (
    echo [错误] 未找到翻译脚本 scripts/translate_to_result.py！
    echo.
    pause
    exit /b 1
)

echo [1/4] 检查环境...
echo ✓ Python 已安装
echo ✓ 配置文件已找到
echo ✓ 脚本文件已找到
echo.

REM Step 1: Sync from QElectroTech
echo [2/4] 从 QElectroTech 同步元件库...
echo.
python scripts/sync_from_qet.py

REM Check sync result
if errorlevel 1 (
    echo.
    echo [错误] 同步失败！
    echo 请检查：
    echo   1. QElectroTech 是否已安装
    echo   2. 或在 translate_config.json 中手动配置 qet_elements_path
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] 开始翻译...
echo.

REM Step 2: Run translation
python scripts/translate_to_result.py

REM Check translation result
if errorlevel 1 (
    echo.
    echo [错误] 翻译失败！
    echo 请检查：
    echo   1. translate_config.json 配置是否正确
    echo   2. 网络连接是否正常
    echo   3. API 服务是否可用
    echo.
) else (
    echo.
    echo ================================================================
    echo                   ✓ 全部完成！
    echo ================================================================
    echo.
    echo 处理结果在: result/ 文件夹
    echo.
    echo 使用说明：
    echo   将 result 文件夹中的内容复制到
    echo   QElectroTech 安装目录的 elements 文件夹即可
    echo.
)

pause
