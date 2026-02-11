@echo off
chcp 65001 >nul
echo.
echo ================================================================
echo            QET Element Library Sync Tool
echo              QElectroTech 元件库同步工具
echo ================================================================
echo.

echo [提示] 同步功能已合并到 translate_to_result.py
echo 将执行“同步 + 翻译”一体流程

echo.
python scripts/translate_to_result.py

pause
