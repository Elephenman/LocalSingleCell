# LocalSingleCell API 参考文档

## 模块概览

```
LocalSingleCell/
├── core/                    # 核心分析模块
│   ├── data_loader.py       # 数据加载
│   ├── qc_filter.py         # 质控过滤
│   ├── analysis_pipeline.py # 分析流程
│   ├── visualization.py     # 可视化
│   ├── enrichment.py        # 富集分析
│   └── ai_parser.py         # AI解析器
└── utils/                   # 工具模块
    ├── config_utils.py      # 配置工具
    ├── security_utils.py    # 安全工具
    ├── exception_utils.py   # 异常处理
    └── validator_utils.py   # 验证工具
```

---

## core.data_loader - 数据加载模块

### read_h5ad

```python
def read_h5ad(file_path: Union[str, Path]) -> ad.AnnData
```

读取h5ad格式的AnnData文件。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| file_path | str \| Path | 是 | - | h5ad文件路径 |

**返回:**

| 类型 | 说明 |
|------|------|
| ad.AnnData | AnnData对象 |

**异常:**

| 异常类型 | 触发条件 |
|---------|---------|
| FileNotFoundError | 文件不存在 |
| DataLoadError | 文件读取失败 |

**示例:**

```python
from core.data_loader import read_h5ad

# 读取h5ad文件
adata = read_h5ad("data/pbmc.h5ad")

# 查看数据信息
print(f"细胞数: {adata.n_obs}, 基因数: {adata.n_vars}")
```

---

### read_10x_mtx

```python
def read_10x_mtx(
    matrix_dir: Union[str, Path],
    var_names: str = 'gene_symbols',
    cache: bool = False
) -> ad.AnnData
```

读取10x Genomics标准输出格式数据。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| matrix_dir | str \| Path | 是 | - | 10x矩阵目录路径 |
| var_names | str | 否 | 'gene_symbols' | 变量名类型 |
| cache | bool | 否 | False | 是否使用缓存 |

**返回:**

| 类型 | 说明 |
|------|------|
| ad.AnnData | AnnData对象 |

**示例:**

```python
from core.data_loader import read_10x_mtx

# 读取10x数据
adata = read_10x_mtx("data/filtered_feature_bc_matrix/")
```

---

### check_10x_structure

```python
def check_10x_structure(directory: Union[str, Path]) -> Tuple[bool, str]
```

检查目录是否符合10x标准格式。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| directory | str \| Path | 是 | - | 要检查的目录 |

**返回:**

| 类型 | 说明 |
|------|------|
| Tuple[bool, str] | (是否有效, 提示信息) |

**示例:**

```python
from core.data_loader import check_10x_structure

is_valid, message = check_10x_structure("data/filtered_feature_bc_matrix/")
if is_valid:
    print("格式正确")
else:
    print(f"格式错误: {message}")
```

---

## core.qc_filter - 质控过滤模块

### calculate_qc_metrics

```python
def calculate_qc_metrics(adata: AnnData) -> AnnData
```

计算质控指标。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| adata | AnnData | 是 | - | AnnData对象 |

**返回:**

| 类型 | 说明 |
|------|------|
| AnnData | 添加了质控指标的AnnData对象 |

**添加的obs列:**

- `n_genes_by_counts`: 每个细胞检测到的基因数
- `total_counts`: 每个细胞的总UMI数

**示例:**

```python
from core.qc_filter import calculate_qc_metrics

adata = calculate_qc_metrics(adata)
print(adata.obs[['n_genes_by_counts', 'total_counts']].head())
```

---

### filter_cells

```python
def filter_cells(
    adata: AnnData,
    min_genes: int = 200,
    max_genes: int = 6000,
    min_umi: int = 500,
    max_umi: int = 20000
) -> AnnData
```

根据质控指标过滤细胞。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| adata | AnnData | 是 | - | AnnData对象 |
| min_genes | int | 否 | 200 | 最小基因数 |
| max_genes | int | 否 | 6000 | 最大基因数 |
| min_umi | int | 否 | 500 | 最小UMI数 |
| max_umi | int | 否 | 20000 | 最大UMI数 |

**返回:**

| 类型 | 说明 |
|------|------|
| AnnData | 过滤后的AnnData对象 |

**示例:**

```python
from core.qc_filter import filter_cells

# 使用默认参数过滤
adata = filter_cells(adata)

# 自定义参数过滤
adata = filter_cells(
    adata,
    min_genes=500,
    max_genes=5000,
    min_umi=1000,
    max_umi=50000
)
```

---

### calculate_mitochondrial_percent

```python
def calculate_mitochondrial_percent(
    adata: AnnData,
    mitochondrial_prefix: str = "MT-"
) -> AnnData
```

计算线粒体基因比例。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| adata | AnnData | 是 | - | AnnData对象 |
| mitochondrial_prefix | str | 否 | "MT-" | 线粒体基因前缀 |

**返回:**

| 类型 | 说明 |
|------|------|
| AnnData | 添加了mt_percent列的AnnData对象 |

**示例:**

```python
from core.qc_filter import calculate_mitochondrial_percent

# 人样本
adata = calculate_mitochondrial_percent(adata, "MT-")

# 小鼠样本
adata = calculate_mitochondrial_percent(adata, "mt-")
```

---

### filter_mitochondrial_cells

```python
def filter_mitochondrial_cells(
    adata: AnnData,
    max_mt_percent: float = 20.0
) -> AnnData
```

过滤线粒体基因比例过高的细胞。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| adata | AnnData | 是 | - | AnnData对象 |
| max_mt_percent | float | 否 | 20.0 | 最大线粒体比例(%) |

**返回:**

| 类型 | 说明 |
|------|------|
| AnnData | 过滤后的AnnData对象 |

---

## core.analysis_pipeline - 分析流程模块

### run_single_cell_pipeline

```python
def run_single_cell_pipeline(
    adata: AnnData,
    config: dict,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Tuple[AnnData, dict]
```

执行完整的单细胞分析流程。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| adata | AnnData | 是 | - | AnnData对象 |
| config | dict | 是 | - | 分析参数配置 |
| progress_callback | Callable | 否 | None | 进度回调函数 |

**返回:**

| 类型 | 说明 |
|------|------|
| Tuple[AnnData, dict] | (分析后的AnnData, 结果摘要字典) |

**配置结构:**

```python
config = {
    'random_seed': 42,
    'qc': {
        'gene_filter': {'apply': True, 'min_cells': 3},
        'cell_filter': {
            'min_genes': 200,
            'max_genes': 6000,
            'min_umi': 500,
            'max_umi': 20000
        },
        'mitochondrial': {
            'apply': True,
            'prefix': 'MT-',
            'max_percent': 20
        }
    },
    'normalization': {
        'method': 'scanpy',
        'target_sum': 1e4,
        'hvg': {'apply': True, 'n_top_genes': 2000},
        'scaling': {'apply': True, 'max_value': 10}
    },
    'dimension_reduction': {
        'pca': {'n_comps': 50, 'use_hvg': True},
        'umap': {'apply': True, 'n_neighbors': 15, 'min_dist': 0.5}
    },
    'clustering': {
        'n_pcs': 30,
        'n_neighbors': 15,
        'resolution': 0.5
    },
    'differential': {'apply': True, 'method': 'wilcoxon'}
}
```

**示例:**

```python
from core.analysis_pipeline import run_single_cell_pipeline
from utils.config_utils import load_config

# 加载默认配置
config = load_config()

# 执行分析
adata, result = run_single_cell_pipeline(
    adata,
    config,
    progress_callback=lambda p, s: print(f"{p}%: {s}")
)

# 查看结果
print(f"质控前: {result['pre_qc']}")
print(f"质控后: {result['post_qc']}")
```

---

## core.enrichment - 富集分析模块

### run_enrichment

```python
def run_enrichment(
    gene_list: list,
    organism: str = 'human',
    databases: list = ['GO_BP', 'KEGG'],
    p_adjust_cutoff: float = 0.05,
    min_gene_count: int = 3
) -> dict
```

执行基因富集分析。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| gene_list | list | 是 | - | 基因名列表 |
| organism | str | 否 | 'human' | 物种 |
| databases | list | 否 | ['GO_BP', 'KEGG'] | 数据库列表 |
| p_adjust_cutoff | float | 否 | 0.05 | p值阈值 |
| min_gene_count | int | 否 | 3 | 最小基因数 |

**返回:**

| 类型 | 说明 |
|------|------|
| dict | 各数据库的富集结果DataFrame |

**示例:**

```python
from core.enrichment import run_enrichment

# 准备基因列表
genes = ['CD3D', 'CD3E', 'CD4', 'CD8A', 'IL7R']

# 执行富集分析
results = run_enrichment(
    gene_list=genes,
    organism='human',
    databases=['GO_BP', 'KEGG']
)

# 查看结果
for db, df in results.items():
    print(f"\n{db}:")
    print(df.head())
```

---

## utils.config_utils - 配置工具模块

### load_config

```python
def load_config(config_path: Optional[str] = None) -> dict
```

加载配置文件。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| config_path | str | 否 | None | 配置文件路径 |

**返回:**

| 类型 | 说明 |
|------|------|
| dict | 配置字典 |

**示例:**

```python
from utils.config_utils import load_config

# 加载默认配置
config = load_config()

# 加载指定配置
config = load_config("custom_config.yaml")
```

---

### validate_config

```python
def validate_config(config: dict) -> Tuple[bool, List[str]]
```

验证配置参数。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| config | dict | 是 | - | 配置字典 |

**返回:**

| 类型 | 说明 |
|------|------|
| Tuple[bool, List[str]] | (是否有效, 错误消息列表) |

---

## utils.security_utils - 安全工具模块

### validate_file_size

```python
def validate_file_size(
    file_path: Union[str, Path],
    max_size_mb: int = 1024
) -> Tuple[bool, str]
```

验证文件大小。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| file_path | str \| Path | 是 | - | 文件路径 |
| max_size_mb | int | 否 | 1024 | 最大大小(MB) |

**返回:**

| 类型 | 说明 |
|------|------|
| Tuple[bool, str] | (是否有效, 提示信息) |

---

### validate_sra_id

```python
def validate_sra_id(sra_id: str) -> Tuple[bool, str]
```

验证SRA ID格式。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| sra_id | str | 是 | - | SRA编号 |

**返回:**

| 类型 | 说明 |
|------|------|
| Tuple[bool, str] | (是否有效, 提示信息) |

**示例:**

```python
from utils.security_utils import validate_sra_id

# 验证SRA ID
is_valid, message = validate_sra_id("SRR123456")
# is_valid: True

is_valid, message = validate_sra_id("ABC123")
# is_valid: False
```

---

### sanitize_filename

```python
def sanitize_filename(filename: str) -> str
```

清理文件名中的危险字符。

**参数:**

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| filename | str | 是 | - | 原始文件名 |

**返回:**

| 类型 | 说明 |
|------|------|
| str | 清理后的安全文件名 |

---

## utils.exceptions - 异常模块

### 自定义异常类

```python
# 基础异常
class LocalSingleCellError(Exception):
    error_code: str
    user_message: str

# 数据异常
class DataLoadError(LocalSingleCellError): pass
class InvalidFileFormatError(DataLoadError): pass

# 分析异常
class AnalysisError(LocalSingleCellError): pass
class QCError(AnalysisError): pass

# 配置异常
class ConfigurationError(LocalSingleCellError): pass
class InvalidConfigError(ConfigurationError): pass

# 资源异常
class ResourceLimitError(LocalSingleCellError): pass
class MemoryLimitError(ResourceLimitError): pass
```

**使用示例:**

```python
from utils.exceptions import DataLoadError, MemoryLimitError

try:
    adata = load_large_data()
except FileNotFoundError as e:
    raise DataLoadError("数据文件不存在", error_code="E101")
except MemoryError as e:
    raise MemoryLimitError("内存不足，请启用降采样")
```

---

## 完整使用示例

### 基础分析流程

```python
import sys
sys.path.insert(0, '.')

from core.data_loader import read_h5ad
from core.qc_filter import (
    calculate_qc_metrics,
    calculate_mitochondrial_percent,
    filter_cells,
    filter_mitochondrial_cells
)
from core.analysis_pipeline import run_single_cell_pipeline
from utils.config_utils import load_config

# 1. 加载数据
adata = read_h5ad("data/pbmc.h5ad")

# 2. 加载配置
config = load_config()

# 3. 执行分析
adata, result = run_single_cell_pipeline(adata, config)

# 4. 查看结果
print(f"聚类数: {len(adata.obs['leiden'].unique())}")
```

---

## utils.performance_utils - 性能监控模块

### PerformanceLogger

```python
class PerformanceLogger(
    output_dir: str = "logs/performance",
    enable_monitoring: bool = True,
    log_memory: bool = True,
    log_timing: bool = True,
    alert_memory_percent: float = 85.0
)
```

性能日志记录器，用于跟踪分析步骤的耗时和内存使用。

**参数:**

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| output_dir | str | "logs/performance" | 日志输出目录 |
| enable_monitoring | bool | True | 是否启用监控 |
| log_memory | bool | True | 是否记录内存使用 |
| log_timing | bool | True | 是否记录耗时 |
| alert_memory_percent | float | 85.0 | 内存告警阈值(%) |

**主要方法:**

| 方法 | 说明 |
|------|------|
| `track_step(step_name, metadata)` | 跟踪步骤执行的上下文管理器 |
| `get_summary()` | 获取性能摘要字典 |
| `save_report(filename)` | 保存性能报告为JSON文件 |
| `clear_records()` | 清除所有记录 |

**示例:**

```python
from utils.performance_utils import PerformanceLogger

# 创建记录器
perf = PerformanceLogger()

# 跟踪步骤
with perf.track_step("数据加载"):
    adata = sc.read_h5ad("data.h5ad")

with perf.track_step("质控过滤"):
    adata = filter_cells(adata)

# 查看摘要
summary = perf.get_summary()
print(f"总耗时: {summary['total_step_duration_seconds']}s")

# 保存报告
perf.save_report()
```

---

### track_performance

```python
@contextmanager
def track_performance(
    step_name: str,
    metadata: Optional[Dict[str, Any]] = None
) -> AnalysisTimer
```

跟踪性能的便捷上下文管理器。

**参数:**

| 参数名 | 类型 | 说明 |
|-------|------|------|
| step_name | str | 步骤名称 |
| metadata | dict | 额外元数据 |

**示例:**

```python
from utils.performance_utils import track_performance

with track_performance("数据分析"):
    # 执行分析操作
    result = analyze_data(adata)
```

---

### monitor_performance

```python
def monitor_performance(step_name: Optional[str] = None)
```

性能监控装饰器，自动跟踪函数执行性能。

**参数:**

| 参数名 | 类型 | 说明 |
|-------|------|------|
| step_name | str | 步骤名称（默认使用函数名） |

**示例:**

```python
from utils.performance_utils import monitor_performance

@monitor_performance("数据加载")
def load_data(path):
    return sc.read_h5ad(path)
```

---

### MemoryMonitor

```python
class MemoryMonitor(alert_percent: float = 85.0)
```

内存监控器，用于检查内存使用情况。

**主要方法:**

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `get_memory_usage()` | float | 获取当前进程内存使用(MB) |
| `get_system_memory_info()` | dict | 获取系统内存信息 |
| `check_memory_alert()` | tuple | 检查内存是否超过告警阈值 |

---

### get_system_info

```python
def get_system_info() -> Dict[str, Any]
```

获取系统信息，包括CPU数量、内存总量等。

**返回:**

```python
{
    "cpu_count": 8,
    "memory_total_gb": 16.0,
    "memory_available_gb": 8.0,
    "memory_used_percent": 50.0,
    "platform": "nt",
    "python_version": "3.11.0"
}
```

---

**版本**: v3.2.0
**更新日期**: 2026-04-02
