#!/bin/bash

# ==============================================================================
# LocalSingleCell - 本地化单细胞&空间转录组分析工具
# Linux/macOS启动脚本
# ==============================================================================

set -e

echo "=============================================================================="
echo "LocalSingleCell - 本地化单细胞&空间转录组分析工具"
echo "Linux/macOS启动脚本"
echo "=============================================================================="
echo ""

# 检查Python环境
echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.10或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python版本：$PYTHON_VERSION"
echo ""

# 检查依赖安装
echo "[2/4] 检查依赖安装..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"
echo ""

# 创建必要目录
echo "[3/4] 准备工作目录..."
mkdir -p logs temp sample_data
echo "✅ 工作目录准备完成"
echo ""

# 启动应用
echo "[4/4] 启动LocalSingleCell..."
echo "=============================================================================="
echo "应用即将启动，请在浏览器中打开显示的地址"
echo "通常是：http://localhost:8501"
echo "=============================================================================="
echo ""

streamlit run app.py --server.headless true
