# LocalSingleCell 企业级优化需求文档

## 文档信息

| 项目名称 | LocalSingleCell - 本地化单细胞&空间转录组分析工具 |
|---------|------------------------------------------------|
| 文档版本 | v1.0 |
| 创建日期 | 2026-04-02 |
| 目标 | 企业级可交付的本地部署工具 |

---

## 一、优化总览

### 1.1 当前状态评估

| 维度 | 当前状态 | 企业级标准 | 差距 |
|------|---------|-----------|------|
| 功能完整性 | 90% | 100% | 需完善细节 |
| 测试覆盖 | 5% | 80%+ | **严重不足** |
| 类型注解 | 13% | 90%+ | 严重不足 |
| 文档完整性 | 60% | 95%+ | 需补充 |
| 安全性 | 50% | 95%+ | 需加强 |
| 错误处理 | 60% | 90%+ | 需完善 |
| 部署方案 | 70% | 95%+ | 需优化 |
| 代码规范 | 65% | 90%+ | 需统一 |

### 1.2 优化优先级

```
P0 (必须完成) ──────────────────────────────────────
  ├─ 1. 测试框架搭建与核心测试
  ├─ 2. 安全性加固
  ├─ 3. 异常处理完善
  └─ 4. 配置验证机制

P1 (重要优化) ──────────────────────────────────────
  ├─ 5. 类型注解补充
  ├─ 6. 文档体系完善
  ├─ 7. Docker优化
  └─ 8. 代码规范统一

P2 (改进项) ────────────────────────────────────────
  ├─ 9. 项目结构现代化
  ├─ 10. CI/CD配置
  └─ 11. 性能监控
```

---

## 二、P0 优化需求（必须完成）

### 2.1 测试框架搭建与核心测试

#### 需求描述
建立完整的测试体系，确保功能正确性和回归测试能力。

#### 具体要求

**2.1.1 测试框架配置**
```
tests/
├── __init__.py
├── conftest.py              # pytest 配置和 fixtures
├── test_core/
│   ├── test_data_loader.py  # 数据加载测试
│   ├── test_qc_filter.py    # 质控过滤测试
│   ├── test_analysis_pipeline.py
│   ├── test_enrichment.py
│   └── test_ai_parser.py
├── test_utils/
│   ├── test_config_utils.py
│   ├── test_validator_utils.py
│   └── test_exception_utils.py
└── fixtures/
    └── test_data.h5ad       # 测试数据
```

**2.1.2 核心测试用例**
- 数据加载：h5ad格式读取、10x格式读取、异常数据测试
- 质控过滤：参数边界测试、空数据处理、极端值测试
- 分析流程：完整流程测试、参数组合测试
- 工具函数：配置加载、参数验证、异常转换

**2.1.3 测试覆盖率要求**
- 核心模块覆盖率 ≥ 80%
- 工具模块覆盖率 ≥ 70%

#### 验收标准
- [ ] pytest 框架配置完成
- [ ] 至少 50 个测试用例通过
- [ ] 核心模块测试覆盖率 ≥ 80%
- [ ] 可通过 `pytest` 命令运行所有测试

---

### 2.2 安全性加固

#### 需求描述
加强输入验证、文件操作安全、资源限制，确保本地部署安全。

#### 具体要求

**2.2.1 文件上传安全**
```python
# 文件大小限制
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    'h5ad': ['h5ad'],
    '10x': ['zip'],
    'image': ['png', 'jpg', 'tif']
}

# 文件魔数校验
FILE_SIGNATURES = {
    'h5ad': b'\x89HDF\r\n\x1a\n',
    'zip': b'PK\x03\x04'
}
```

**2.2.2 输入验证增强**
- SRA号格式严格校验（防注入）
- 文件名安全检查（防路径遍历）
- 参数范围强制校验

**2.2.3 资源限制**
```yaml
# config.yaml 新增
security:
  max_file_size_mb: 1024
  max_upload_files: 10
  analysis_timeout_minutes: 60
  max_memory_percent: 80
```

#### 验收标准
- [ ] 文件上传有大小限制和类型校验
- [ ] 文件名进行安全检查
- [ ] 所有用户输入经过验证
- [ ] 配置文件包含安全设置

---

### 2.3 异常处理完善

#### 需求描述
建立自定义异常体系，提供精确的错误诊断和用户友好的提示。

#### 具体要求

**2.3.1 自定义异常类**
```python
# utils/exceptions.py
class LocalSingleCellError(Exception):
    """基础异常类"""
    error_code: str
    user_message: str

class DataLoadError(LocalSingleCellError):
    """数据加载错误"""
    pass

class AnalysisError(LocalSingleCellError):
    """分析过程错误"""
    pass

class ConfigurationError(LocalSingleCellError):
    """配置错误"""
    pass

class ValidationError(LocalSingleCellError):
    """验证错误"""
    pass

class ResourceLimitError(LocalSingleCellError):
    """资源限制错误"""
    pass
```

**2.3.2 错误码体系**
| 错误码 | 类型 | 用户提示 |
|-------|------|---------|
| E001 | 文件格式错误 | "不支持的文件格式，请上传 .h5ad 文件" |
| E002 | 文件损坏 | "文件已损坏或格式不正确，请检查文件" |
| E003 | 内存不足 | "内存不足，请尝试降采样或使用更小的数据集" |
| E004 | 参数无效 | "参数值超出有效范围" |
| E005 | 依赖缺失 | "缺少必要的依赖工具" |

**2.3.3 异常处理模式**
```python
try:
    result = analyze_data(adata, config)
except MemoryError:
    raise ResourceLimitError("E003", "内存不足，建议启用降采样")
except ValueError as e:
    raise ValidationError("E004", f"参数错误: {e}")
except Exception as e:
    logger.exception("未知错误")
    raise LocalSingleCellError("E999", "分析过程发生未知错误，请查看日志")
```

#### 验收标准
- [ ] 自定义异常类定义完成
- [ ] 错误码体系文档化
- [ ] 核心模块使用自定义异常
- [ ] 用户看到友好的中文错误提示

---

### 2.4 配置验证机制

#### 需求描述
实现配置文件的加载验证，确保配置值合法。

#### 具体要求

**2.4.1 配置验证函数**
```python
def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    验证配置文件

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # 验证必需字段
    required_fields = ['random_seed', 'qc', 'normalization', 'clustering']
    for field in required_fields:
        if field not in config:
            errors.append(f"缺少必需配置项: {field}")

    # 验证数值范围
    if not (0 <= config.get('clustering', {}).get('resolution', 0.5) <= 2):
        errors.append("聚类分辨率必须在 0-2 之间")

    # 验证类型
    if not isinstance(config.get('random_seed'), int):
        errors.append("随机种子必须是整数")

    return len(errors) == 0, errors
```

**2.4.2 配置默认值回填**
- 缺少可选配置时使用默认值
- 记录配置差异到日志

#### 验收标准
- [ ] 配置加载时自动验证
- [ ] 非法配置给出明确错误提示
- [ ] 缺少可选配置时使用默认值

---

## 三、P1 优化需求（重要优化）

### 3.1 类型注解补充

#### 需求描述
为所有公共函数添加完整的类型注解，提升代码可维护性和IDE支持。

#### 具体要求

**3.1.1 类型注解规范**
```python
from typing import Optional, List, Dict, Any, Tuple, Callable
import anndata as ad
import pandas as pd
import numpy as np

def filter_cells(
    adata: ad.AnnData,
    min_genes: int = 200,
    max_genes: int = 6000,
    min_umi: int = 500,
    max_umi: int = 20000
) -> ad.AnnData:
    """
    过滤细胞

    Args:
        adata: AnnData对象
        min_genes: 最小基因数
        max_genes: 最大基因数
        min_umi: 最小UMI数
        max_umi: 最大UMI数

    Returns:
        过滤后的AnnData对象
    """
    pass
```

**3.1.2 覆盖范围**
- `core/` 目录所有公共函数
- `utils/` 目录所有公共函数
- `ui/` 目录主要函数

#### 验收标准
- [ ] 核心模块类型注解覆盖 ≥ 90%
- [ ] 通过 mypy 静态类型检查

---

### 3.2 文档体系完善

#### 需求描述
建立完整的文档体系，包括用户文档、API文档、开发者文档。

#### 具体要求

**3.2.1 文档结构**
```
docs/
├── README.md              # 项目概述
├── USER_GUIDE.md          # 用户使用手册
├── API_REFERENCE.md       # API参考文档
├── CONFIGURATION.md       # 配置说明
├── DEPLOYMENT.md          # 部署指南（已有）
├── DEVELOPMENT.md         # 开发指南
├── CHANGELOG.md           # 变更日志
└── FAQ.md                 # 常见问题
```

**3.2.2 文档内容要求**
- 用户手册：完整操作流程、截图示例
- API文档：所有公共函数的详细说明
- 配置说明：所有配置项的含义和默认值
- FAQ：至少 20 个常见问题

#### 验收标准
- [ ] 所有文档文件创建完成
- [ ] API文档覆盖所有公共函数
- [ ] FAQ 包含至少 20 个问题

---

### 3.3 Docker优化

#### 需求描述
优化 Docker 镜像，确保安全性和镜像大小。

#### 具体要求

**3.3.1 Dockerfile优化**
```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# 创建非root用户
RUN useradd -m -u 1000 appuser

# 复制依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 复制应用
COPY --chown=appuser:appuser . .

# 切换用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

**3.3.2 安全要求**
- 非 root 用户运行
- 最小化基础镜像
- 健康检查配置

#### 验收标准
- [ ] Docker 镜像以非 root 用户运行
- [ ] 镜像大小 < 2GB
- [ ] 健康检查正常工作

---

### 3.4 代码规范统一

#### 需求描述
统一代码风格，建立代码质量检查机制。

#### 具体要求

**3.4.1 代码风格配置**
```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.isort]
profile = "black"
line_length = 120
```

**3.4.2 统一规范**
- 导入顺序：标准库 → 第三方库 → 本地模块
- 文档字符串：Google 风格
- 命名：snake_case（变量/函数）、PascalCase（类）

#### 验收标准
- [ ] 配置 ruff/isort 工具
- [ ] 所有文件通过代码检查
- [ ] 文档字符串格式统一

---

## 四、P2 优化需求（改进项）

### 4.1 项目结构现代化

#### 需求描述
迁移到现代 Python 项目结构，支持 pyproject.toml。

#### 具体要求
```toml
# pyproject.toml
[project]
name = "localsinglecell"
version = "3.1.0"
description = "本地化单细胞&空间转录组分析工具"
requires-python = ">=3.10"
license = {text = "MIT"}

[project.dependencies]
streamlit = ">=1.32.2"
scanpy = ">=1.10.1"

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "ruff", "mypy"]
```

---

### 4.2 CI/CD配置

#### 需求描述
建立持续集成流程，自动化测试和发布。

#### 具体要求
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov
```

---

### 4.3 性能监控

#### 需求描述
添加性能指标收集和监控功能。

#### 具体要求
- 分析耗时统计
- 内存使用监控
- 操作日志记录

---

## 五、实施计划

### 5.1 阶段一：基础加固（P0）

| 任务 | 预计工作量 | 依赖 |
|------|-----------|------|
| 测试框架搭建 | 2h | - |
| 核心测试编写 | 4h | 测试框架 |
| 安全性加固 | 2h | - |
| 异常处理完善 | 2h | - |
| 配置验证机制 | 1h | - |

**阶段一验收**：程序稳定运行，核心功能有测试覆盖

### 5.2 阶段二：质量提升（P1）

| 任务 | 预计工作量 | 依赖 |
|------|-----------|------|
| 类型注解补充 | 3h | - |
| 文档编写 | 4h | - |
| Docker优化 | 1h | - |
| 代码规范统一 | 2h | - |

**阶段二验收**：代码质量达标，文档完整

### 5.3 阶段三：持续优化（P2）

| 任务 | 预计工作量 | 依赖 |
|------|-----------|------|
| 项目结构现代化 | 2h | 阶段二 |
| CI/CD配置 | 1h | 测试框架 |
| 性能监控 | 2h | - |

**阶段三验收**：项目达到企业级交付标准

---

## 六、验收标准总览

### 最终交付标准

| 维度 | 标准 | 验证方法 |
|------|------|---------|
| 功能完整性 | 所有功能正常运行 | 手动测试 + 自动化测试 |
| 测试覆盖率 | ≥ 70% | pytest-cov |
| 类型注解 | ≥ 90% | mypy 检查 |
| 文档完整性 | 所有文档齐全 | 人工审核 |
| 安全性 | 无已知漏洞 | 安全扫描 |
| 部署 | 一键部署成功 | Docker 构建测试 |
| 性能 | 正常数据集 < 10min | 性能测试 |

---

## 附录：文件修改清单

### 新增文件
```
tests/
├── __init__.py
├── conftest.py
├── test_core/
│   ├── test_data_loader.py
│   ├── test_qc_filter.py
│   └── test_analysis_pipeline.py
└── test_utils/
    ├── test_config_utils.py
    └── test_validator_utils.py

utils/
└── exceptions.py              # 自定义异常类

docs/
├── USER_GUIDE.md
├── API_REFERENCE.md
├── CONFIGURATION.md
├── DEVELOPMENT.md
├── CHANGELOG.md
└── FAQ.md

pyproject.toml
```

### 修改文件
```
utils/validator_utils.py       # 增强验证功能
utils/exception_utils.py       # 集成自定义异常
utils/config_utils.py          # 添加配置验证
core/*.py                      # 添加类型注解
ui/*.py                        # 使用自定义异常
config.yaml                    # 添加安全配置
Dockerfile                     # 安全优化
requirements.txt               # 添加测试依赖
```
