# LocalSingleCell 部署指南

本文档提供LocalSingleCell在不同环境下的详细部署指南。

---

## 目录

- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [Docker部署](#docker部署)
- [手动部署](#手动部署)
- [性能调优](#性能调优)
- [故障排除](#故障排除)

---

## 系统要求

### 最低配置
- **操作系统**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.10 - 3.12
- **内存**: 8GB RAM
- **存储**: 10GB 可用空间
- **网络**: 仅用于依赖安装和SRA数据下载

### 推荐配置
- **操作系统**: Windows 11, Ubuntu 22.04+, macOS 12+
- **Python**: 3.11
- **内存**: 16GB+ RAM
- **存储**: 50GB+ 可用SSD
- **CPU**: 4+ 核心

---

## 快速部署

### Windows用户

1. **下载项目**
   ```bash
   cd LocalSingleCell
   ```

2. **双击运行启动脚本**
   ```
   双击 start.bat
   ```

3. **等待自动安装和启动**
   - 脚本会自动检查Python环境
   - 自动创建虚拟环境
   - 自动安装依赖
   - 自动启动应用

4. **访问应用**
   - 浏览器打开: http://localhost:8501

### Linux/macOS用户

1. **下载项目**
   ```bash
   cd LocalSingleCell
   ```

2. **添加执行权限并运行**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

3. **访问应用**
   - 浏览器打开: http://localhost:8501

---

## Docker部署

### 前置条件

- 安装 Docker Engine: https://docs.docker.com/get-docker/
- 安装 Docker Compose: https://docs.docker.com/compose/install/

### 方式1：使用Docker Compose（推荐）

1. **进入项目目录**
   ```bash
   cd LocalSingleCell
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f
   ```

4. **访问应用**
   - 浏览器打开: http://localhost:8501

5. **停止服务**
   ```bash
   docker-compose down
   ```

### 方式2：手动构建和运行

1. **构建Docker镜像**
   ```bash
   cd LocalSingleCell
   docker build -t localsinglecell:latest .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name localsinglecell \
     -p 8501:8501 \
     -v $(pwd)/logs:/app/logs \
     -v $(pwd)/temp:/app/temp \
     -v $(pwd)/sample_data:/app/sample_data \
     --restart unless-stopped \
     localsinglecell:latest
   ```

3. **查看容器状态**
   ```bash
   docker ps
   ```

4. **查看日志**
   ```bash
   docker logs -f localsinglecell
   ```

5. **停止容器**
   ```bash
   docker stop localsinglecell
   ```

6. **删除容器**
   ```bash
   docker rm localsinglecell
   ```

### Docker常用命令

```bash
# 查看所有容器
docker ps -a

# 查看容器资源使用
docker stats

# 进入容器
docker exec -it localsinglecell /bin/bash

# 重启容器
docker restart localsinglecell

# 更新镜像
docker-compose pull
docker-compose up -d
```

---

## 手动部署

### 1. 环境准备

#### Windows

1. **安装Python**
   - 下载: https://www.python.org/downloads/
   - 选择 Python 3.10 或 3.11
   - 安装时勾选 "Add Python to PATH"

2. **验证安装**
   ```cmd
   python --version
   pip --version
   ```

#### Linux (Ubuntu/Debian)

1. **安装Python**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   ```

2. **验证安装**
   ```bash
   python3 --version
   pip3 --version
   ```

#### macOS

1. **安装Homebrew（如果未安装）**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **安装Python**
   ```bash
   brew install python@3.11
   ```

3. **验证安装**
   ```bash
   python3 --version
   pip3 --version
   ```

### 2. 项目安装

1. **进入项目目录**
   ```bash
   cd LocalSingleCell
   ```

2. **创建虚拟环境（推荐）**

   **Windows:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **升级pip**
   ```bash
   pip install --upgrade pip
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **创建必要目录**
   ```bash
   mkdir -p logs temp sample_data
   ```

### 3. 生成示例数据（可选）

```bash
python scripts/generate_sample_data.py
```

### 4. 启动应用

```bash
streamlit run app.py --server.headless true
```

### 5. 访问应用

浏览器打开: http://localhost:8501

---

## 性能调优

### 配置文件优化

编辑 `config.yaml` 文件调整性能参数：

```yaml
performance:
  auto_downsample:
    enabled: true
    max_cells: 10000        # 根据内存调整
    max_genes: 20000        # 根据内存调整
    suggest_only: false
  
  memory:
    gc_threshold_percent: 80
    enable_cache: true
  
  parallel:
    enabled: true
    n_jobs: -1                # 使用所有CPU核心
```

### 低配置电脑优化

如果您的电脑配置较低（<8GB RAM），建议：

1. **降低降采样阈值**
   ```yaml
   performance:
     auto_downsample:
       max_cells: 5000
       max_genes: 10000
   ```

2. **关闭其他应用**
   - 关闭浏览器多余标签页
   - 关闭后台运行的程序

3. **使用示例数据测试**
   - 先用PBMC3k等小数据测试
   - 确认正常后再处理大数据

### Streamlit配置优化

编辑 `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501
maxUploadSize = 2048        # 最大上传文件大小（MB）

[client]
showErrorDetails = false

[logger]
level = "info"
```

---

## 故障排除

### 常见问题

#### 1. Python版本不兼容

**问题**: `Python version X is not supported`

**解决方案**:
- 安装Python 3.10 - 3.12
- 使用虚拟环境管理多个Python版本

#### 2. 依赖安装失败

**问题**: `pip install` 报错

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

#### 3. 端口被占用

**问题**: `Port 8501 is already in use`

**解决方案**:
```bash
# Windows查找占用进程
netstat -ano | findstr :8501
taskkill /PID <进程ID> /F

# Linux/macOS查找占用进程
lsof -ti:8501 | xargs kill -9

# 或使用其他端口启动
streamlit run app.py --server.port 8502
```

#### 4. 内存不足

**问题**: `MemoryError` 或程序崩溃

**解决方案**:
1. 启用自动降采样（默认已启用）
2. 在配置文件中降低 `max_cells` 和 `max_genes`
3. 关闭其他占用内存的程序
4. 使用更小的数据集测试

#### 5. Docker无法启动

**问题**: Docker服务未运行

**解决方案**:
```bash
# Windows
# 以管理员身份运行命令提示符
net start com.docker.service

# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS
# 打开Docker Desktop应用
```

#### 6. 中文字体乱码

**问题**: 图表中文字显示为方框

**解决方案**:
- 程序会自动配置中文字体
- 如仍有问题，检查系统是否安装了中文字体
- Windows: 确保有微软雅黑
- Linux: 安装文泉驿微米黑 `sudo apt install fonts-wqy-microhei`

### 日志查看

应用日志位于 `logs/app.log`:

```bash
# 查看最新日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

### 获取帮助

如果以上解决方案无法解决您的问题：

1. 查看 `logs/app.log` 获取详细错误信息
2. 检查常见问题FAQ（见README.md）
3. 提交Issue，包含：
   - 错误信息
   - 操作系统版本
   - Python版本
   - 复现步骤

---

## 生产环境部署建议

### 1. 使用反向代理

使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. 配置HTTPS

使用Let's Encrypt免费证书：

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

### 3. 数据备份

定期备份重要数据：

```bash
# 备份脚本示例
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/localsinglecell_$DATE.tar.gz \
  sample_data/ \
  logs/ \
  config.yaml
```

---

## 附录

### A. 端口说明

| 端口 | 用途 |
|------|------|
| 8501 | Streamlit应用默认端口 |

### B. 目录说明

| 目录 | 用途 |
|------|------|
| logs/ | 日志文件 |
| temp/ | 临时文件 |
| sample_data/ | 示例数据 |
| core/ | 核心分析模块 |
| ui/ | UI界面模块 |
| utils/ | 工具函数模块 |

### C. 参考资源

- Streamlit文档: https://docs.streamlit.io/
- Scanpy文档: https://scanpy.readthedocs.io/
- Docker文档: https://docs.docker.com/
- Python官方文档: https://docs.python.org/

---

**最后更新**: 2026-04-02
**版本**: v4.0.0
