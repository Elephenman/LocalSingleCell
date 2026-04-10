# LocalSingleCell - 本地化单细胞&空间转录组分析工具

一款完全本地化、无云端依赖、低代码UI界面、基于成熟开源生信工具封装的单细胞&空间转录组全流程分析工具。

## 功能特性

### 🔬 核心功能
- **完全本地化运行**：所有计算在本地完成，无数据隐私风险
- **单细胞转录组分析**：完整的单细胞分析流程
- **空间转录组分析**：支持10x Visium等空间数据格式
- **AI自然语言分析**：内置规则解析器，支持自然语言需求转换
- **一键分析**：无需编程，通过UI即可完成全流程分析

### 📊 分析流程
- 数据导入（h5ad、10x格式、SRA下载）
- 质控过滤
- 归一化与高变基因筛选
- 降维分析（PCA、UMAP、tSNE）
- 细胞聚类（Leiden算法）
- 差异基因分析
- 基因富集分析（GO、KEGG、Reactome）
- 空间转录组专属分析
- 结果可视化与导出

### 🛠️ 技术栈
- **Python 3.10+**
- **Streamlit 1.32+**：低代码UI框架
- **Scanpy 1.10+**：单细胞分析金标准
- **Squidpy 1.4+**：空间转录组分析
- **GSEApy**：富集分析
- **Matplotlib/Seaborn/Plotly**：可视化

## 安装与使用

### 1. 环境要求
- Windows 10/11 或 Linux/macOS
- Python 3.10 - 3.12
- 至少8GB RAM（推荐16GB+）

### 2. 安装依赖
```bash
cd LocalSingleCell
pip install -r requirements.txt
```

### 3. 启动程序
```bash
streamlit run app.py --server.headless true
```

### 4. 访问应用
程序启动后，在浏览器中打开显示的本地URL（通常是 http://localhost:8501）

## 使用说明

### 快速开始
1. **导入数据**：上传h5ad文件或10x格式数据
2. **配置参数**：使用默认参数或自定义调整
3. **执行分析**：点击一键分析按钮
4. **查看结果**：在可视化页面查看图表
5. **导出结果**：下载分析结果和报告

### AI自然语言分析
1. 导入数据后，进入「AI自然语言分析」页面
2. 输入自然语言需求，例如：
   - "帮我分析这个数据，过滤线粒体比例超过15%的细胞，分辨率0.8聚类"
   - "做GO和KEGG富集分析，生成UMAP图和火山图"
3. 点击「解析需求」查看生成的参数
4. 确认参数后点击「一键执行分析」

## 项目结构

```
LocalSingleCell/
├── app.py                      # 主入口文件
├── requirements.txt            # 依赖包列表
├── config.yaml                 # 全局配置文件
├── README.md                   # 项目说明文档
│
├── core/                       # 核心分析模块
│   ├── __init__.py             # 模块导出
│   ├── data_loader.py          # 数据加载
│   ├── qc_filter.py            # 质控过滤
│   ├── analysis_pipeline.py    # 单细胞分析流程
│   ├── spatial_pipeline.py     # 空间分析流程
│   ├── spatial_loader.py       # 空间数据加载
│   ├── visualization.py        # 可视化
│   ├── spatial_visualization.py # 空间可视化
│   ├── enrichment.py           # 富集分析
│   ├── ai_parser.py            # AI需求解析器
│   ├── sra_processor.py        # SRA数据处理
│   ├── downsampling.py         # 降采样工具
│   └── config/                 # 配置管理
│       ├── param_manager.py    # 参数管理器
│       └── parameter_schema.py # 参数模式定义
│
├── ui/                         # UI界面模块
│   ├── __init__.py             # 模块导出
│   ├── sidebar.py              # 侧边栏导航
│   ├── home_page.py            # 首页
│   ├── data_import_page.py     # 数据导入页面
│   ├── pipeline_config_page.py # 分析配置页面
│   ├── spatial_pipeline_config_page.py # 空间配置页面
│   ├── visualization_page.py   # 可视化页面
│   ├── spatial_visualization_page.py # 空间可视化页面
│   ├── enrichment_page.py      # 富集分析页面
│   ├── ai_analysis_page.py     # AI分析页面
│   ├── result_export_page.py   # 结果导出页面
│   ├── help_page.py            # 帮助页面
│   └── components/             # 可复用UI组件
│       ├── navbar.py           # 导航栏组件
│       └── param_editor.py     # 参数编辑器组件
│
├── utils/                      # 工具函数模块
│   ├── config_utils.py         # 配置工具
│   ├── logger_utils.py         # 日志工具
│   ├── validator_utils.py      # 验证工具
│   ├── exception_utils.py      # 异常处理
│   ├── exceptions.py           # 自定义异常类
│   ├── performance_utils.py    # 性能监控
│   ├── security_utils.py       # 安全工具
│   └── visual_utils.py         # 可视化工具
│
├── tests/                      # 单元测试
│   ├── test_core/              # 核心模块测试
│   └── test_utils/             # 工具模块测试
│
├── docs/                       # 文档目录
├── logs/                       # 日志目录
└── temp/                       # 临时文件目录
```

## 核心红线规则
1. **完全本地化**：所有功能在本地完成，无云端依赖
2. **开源合规**：使用开源免费工具
3. **开箱即用**：仅需安装依赖和启动命令
4. **友好容错**：完善的异常处理和中文提示
5. **中文适配**：所有界面和提示为中文

## 版本历史

### v3.1.0 (2026-04-10)
- 🧹 代码审查优化，清理临时文件
- 🔧 重命名异常类避免与内置冲突
- 📦 补充模块级导出，优化导入体验
- 🗑️ 删除冗余的 ui/pages 目录，统一架构

### v3.0.0 (2026-04-01)
- ✨ 新增AI自然语言分析功能
- 🔧 内置规则解析器，支持自然语言需求转换
- 📝 支持示例需求快速测试
- 🔄 参数验证与一键执行

### v2.0.0 (2026-03-31)
- ✨ 新增空间转录组分析功能
- 🗺️ 支持10x Visium数据格式
- 🎨 空间可视化图表
- 📊 空间可变基因分析

### v1.0.0 (2026-03-30)
- 🎉 初始版本发布
- ✅ 单细胞转录组完整分析流程
- 📊 丰富的可视化图表
- 📦 结果导出功能

## 许可证
本项目为开源项目，仅供学习和研究使用。

## 贡献
欢迎提交Issue和Pull Request！

## 联系方式
如有问题或建议，请通过Issue反馈。

---

**注意**：本工具仅供科研使用，不用于临床诊断。
