# LocalSingleCell - Claude Code 项目指南

## 项目概述

LocalSingleCell 是一款完全本地化、无云端依赖的单细胞&空间转录组分析工具，基于 Streamlit 构建低代码 UI 界面，封装了 Scanpy/Squidpy 等成熟开源生信工具。

### 核心特性
- 完全本地化运行，无数据隐私风险
- 支持单细胞转录组和空间转录组分析
- AI 自然语言解析需求（规则引擎）
- 中文界面和提示

## 技术栈

- **Python 3.10-3.12**
- **Streamlit 1.32+**: Web UI 框架
- **Scanpy 1.10+**: 单细胞分析核心库
- **Squidpy 1.4+**: 空间转录组分析
- **GSEApy**: 基因富集分析
- **Matplotlib/Seaborn/Plotly**: 可视化

## 项目结构

```
LocalSingleCell/
├── app.py                 # 主入口
├── config.yaml            # 全局配置文件
├── core/                  # 核心分析模块
│   ├── data_loader.py     # 数据加载
│   ├── qc_filter.py       # 质控过滤
│   ├── analysis_pipeline.py   # 单细胞分析流程
│   ├── spatial_pipeline.py    # 空间分析流程
│   ├── visualization.py       # 可视化
│   ├── enrichment.py      # 富集分析
│   └── ai_parser.py       # AI 需求解析器
├── ui/                    # UI 页面模块
│   ├── sidebar.py         # 侧边栏导航
│   ├── home_page.py       # 首页
│   ├── data_import_page.py    # 数据导入
│   ├── pipeline_config_page.py    # 分析配置
│   ├── visualization_page.py   # 可视化页面
│   └── ...
├── utils/                 # 工具函数
│   ├── config_utils.py    # 配置工具
│   ├── logger_utils.py    # 日志工具
│   └── ...
└── tests/                 # 测试目录
```

## 代码规范

### 代码风格
- 行长度上限: 120 字符
- 使用中文注释和文档字符串
- 函数使用 type hints

### 命名约定
- 文件名: snake_case
- 类名: PascalCase
- 函数/变量: snake_case
- 常量: UPPER_SNAKE_CASE

### 模块组织
- `core/`: 核心分析逻辑，无 UI 依赖
- `ui/`: Streamlit 页面组件
- `utils/`: 通用工具函数

## 关键约束

### 核心红线（不可违反）
1. **完全本地化**: 所有功能必须在本地完成，禁止任何云端依赖
2. **开源合规**: 只使用开源免费工具
3. **开箱即用**: 仅需 `pip install` 和启动命令
4. **中文适配**: 所有界面和提示必须为中文

### Git 提交规范
- 提交作者只能是本地配置用户，禁止添加 `Co-Authored-By`
- 提交信息使用中文或英文，简洁明了

### 远程仓库
- `origin` → GitHub (主仓库)
- `gitee` → Gitee (镜像仓库)
- 推送时需同时推送到两个仓库

## 运行命令

### 启动应用
```bash
streamlit run app.py --server.headless true
```

### 运行测试
```bash
pytest tests/ -v
```

### 代码检查
```bash
ruff check .
ruff format .
```

## 配置说明

全局配置在 `config.yaml` 中，包含：
- 性能优化配置（自动降采样、内存优化）
- 质控参数默认值
- 归一化参数
- 降维参数
- 聚类参数
- 富集分析参数

## UI 开发指南

### 页面结构
每个 UI 页面模块应包含 `show()` 函数作为入口：
```python
def show():
    st.title("页面标题")
    # 页面内容
```

### Session State
应用使用 Streamlit session_state 管理状态：
- `anndata_obj`: 当前加载的 AnnData 对象
- `is_data_loaded`: 数据是否已加载
- `is_spatial_data`: 是否为空间数据
- `is_analysis_done`: 分析是否完成
- `pipeline_config`: 分析参数配置
- `analysis_result`: 分析结果摘要

## AI 解析器

`core/ai_parser.py` 实现基于规则的自然语言解析：
- 解析用户中文需求
- 提取质控、聚类、降维等参数
- 生成分析流程配置
- 不依赖外部 LLM API
