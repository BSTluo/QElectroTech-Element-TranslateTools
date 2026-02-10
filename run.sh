#!/bin/bash

# QET Element Translator - Mac/Linux Launcher
# 一键启动翻译工具

echo ""
echo "================================================================"
echo "              QET Element Translator - Mac/Linux"
echo "                    一键启动翻译工具"
echo "================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[错误] 未找到 Python！"
    echo ""
    echo "请先安装 Python 3.7 或更高版本"
    echo "• Mac 用户: brew install python3"
    echo "• Linux 用户: sudo apt-get install python3"
    echo ""
    read -p "按任意键继续..." -n 1 -r
    exit 1
fi

# Determine which python to use
if command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi

# Check if translate_config.json exists
if [ ! -f "translate_config.json" ]; then
    echo "[错误] 未找到配置文件 translate_config.json！"
    echo ""
    read -p "按任意键继续..." -n 1 -r
    exit 1
fi

# Check if scripts/translate_to_result.py exists
if [ ! -f "scripts/translate_to_result.py" ]; then
    echo "[错误] 未找到脚本文件 scripts/translate_to_result.py！"
    echo ""
    read -p "按任意键继续..." -n 1 -r
    exit 1
fi

echo "[1/3] 检查环境..."
echo "✓ Python ($PYTHON) 已安装"
echo "✓ 配置文件已找到"
echo "✓ 脚本文件已找到"
echo ""
echo "[2/3] 准备启动..."
echo ""

# Run the translation script
$PYTHON scripts/translate_to_result.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 翻译失败！"
    echo "请检查："
    echo "  1. translate_config.json 配置是否正确"
    echo "  2. 网络连接是否正常"
    echo "  3. API 服务是否可用"
    echo ""
else
    echo ""
    echo "================================================================"
    echo "                       ✓ 翻译完成！"
    echo "================================================================"
    echo ""
    echo "处理结果在: result/ 文件夹"
    echo ""
fi

read -p "按任意键关闭此窗口..." -n 1 -r
