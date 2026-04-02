@echo off
chcp 65001 >nul
echo ==============================================================================
echo LocalSingleCell - 本地化单细胞&空间转录组分析工具
echo Windows启动脚本
echo ==============================================================================
echo.

REM 检查Python环境
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.10或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本：%PYTHON_VERSION%
echo.

REM 检查依赖安装
echo [2/4] 检查依赖安装...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo ✅ 依赖安装完成
echo.

REM 创建必要目录
echo [3/4] 准备工作目录...
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "sample_data" mkdir sample_data
echo ✅ 工作目录准备完成
echo.

REM 启动应用
echo [4/4] 启动LocalSingleCell...
echo ==============================================================================
echo 应用即将启动，请在浏览器中打开显示的地址
echo 通常是：http://localhost:8501
echo ==============================================================================
echo.
streamlit run app.py --server.headless true

pause
