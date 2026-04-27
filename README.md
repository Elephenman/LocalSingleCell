# LocalSingleCell - 本地化单细胞 & 空间转录组分析工具

一款完全本地化、无云端依赖、低代码 UI 界面、基于成熟开源生信工具封装的单细胞 & 空间转录组全流程分析工具。

## 功能特性

### 🔬 核心功能
- **完全本地化运行**：所有计算在本地完成，无数据隐私风险
- **单细胞转录组分析**：完整的单细胞分析流程（QC → 归一化 → 降维 → 聚类 → 差异表达 → 富集）
- **空间转录组分析**：支持 10x Visium 等空间数据格式
- **AI 自然语言分析**：内置规则解析器，支持中文自然语言需求转换
- **一键分析**：无需编程，通过 UI 即可完成全流程分析

### 📊 分析流程
1. **数据导入**：支持 h5ad、10x 格式、SRA 数据下载
2. **质控过滤**：线粒体/核糖体比例过滤，细胞/基因阈值筛选
3. **归一化与高变基因筛选**：Scanpy 标准归一化 / CPM，保留原始 counts 层
4. **降维分析**：PCA → UMAP / tSNE
5. **细胞聚类**：Leiden / Louvain 算法
6. **差异基因分析**：Wilcoxon / t-test / logreg
7. **基因富集分析**：GO、KEGG、Reactome（GSEApy，完全离线）
8. **空间转录组专属分析**：空间可变基因、邻域富集、配体-受体（开发中）
9. **结果可视化与导出**：UMAP/tSNE 散点图、基因表达图、热图、火山图

### 🛠️ 技术栈
- **Python 3.10+**
- **Streamlit 1.30+**：低代码 UI 框架
- **Scanpy 1.10+**：单细胞分析金标准
- **Squidpy 1.4+**：空间转录组分析
- **GSEApy**：富集分析（离线运行）
- **Matplotlib / Seaborn / Plotly**：可视化

## 安装与使用

### 环境要求
- Windows 10/11 或 Linux / macOS
- Python 3.10+
- 至少 8GB RAM（推荐 16GB+）

### 安装依赖
```bash
cd LocalSingleCell
pip install -r requirements.txt
```

### 启动程序
```bash
streamlit run app.py --server.headless true
```

启动后浏览器打开 http://localhost:8501

### Docker 部署
```bash
docker-compose up -d
```

详见 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 使用说明

### 快速开始
1. **导入数据**：上传 h5ad 文件或 10x 格式数据
2. **配置参数**：使用默认参数或自定义调整
3. **执行分析**：点击一键分析按钮
4. **查看结果**：在可视化页面查看图表
5. **导出结果**：下载分析结果和报告

### AI 自然语言分析
1. 导入数据后，进入「AI 自然语言分析」页面
2. 输入自然语言需求，例如：
   - "帮我分析这个数据，过滤线粒体比例超过 15% 的细胞，分辨率 0.8 聚类"
   - "做 GO 和 KEGG 富集分析，生成 UMAP 图和火山图"
3. 点击「解析需求」查看生成的参数
4. 确认参数后点击「一键执行分析」

## 项目结构

```
LocalSingleCell/
├── app.py                          # 主入口（Streamlit 应用）
├── config.yaml                     # 全局配置文件
├── requirements.txt                # 依赖列表
├── pyproject.toml                  # 项目元数据
├── Dockerfile / docker-compose.yml # Docker 部署
├── start.sh / start.bat            # 启动脚本
├── LICENSE                         # MIT 许可证
│
├── core/                           # 核心分析模块
│   ├── data_loader.py              # 数据加载（h5ad / 10x / SRA）
│   ├── qc_filter.py                # 质控过滤（兼容稀疏矩阵）
│   ├── analysis_pipeline.py        # 单细胞全流程 pipeline
│   ├── spatial_pipeline.py         # 空间转录组 pipeline
│   ├── spatial_loader.py           # 空间数据加载
│   ├── spatial_visualization.py    # 空间可视化
│   ├── visualization.py            # 通用可视化（UMAP / tSNE / 热图）
│   ├── enrichment.py               # 富集分析（GO / KEGG / Reactome）
│   ├── ai_parser.py                # AI 自然语言参数解析器
│   ├── downsampling.py             # 降采样（细胞 / 基因）
│   ├── sra_processor.py            # SRA 数据处理
│   └── config/                     # 配置管理
│       ├── param_manager.py        # 参数管理器
│       └── parameter_schema.py     # 参数 Schema
│
├── ui/                             # UI 界面模块
│   ├── sidebar.py                  # 侧边栏导航
│   ├── home_page.py                # 首页
│   ├── data_import_page.py         # 数据导入页
│   ├── pipeline_config_page.py     # 单细胞配置页
│   ├── spatial_pipeline_config_page.py # 空间配置页
│   ├── visualization_page.py       # 可视化页
│   ├── spatial_visualization_page.py   # 空间可视化页
│   ├── enrichment_page.py          # 富集分析页
│   ├── ai_analysis_page.py         # AI 分析页
│   ├── result_export_page.py       # 结果导出页
│   ├── help_page.py                # 帮助页
│   └── components/                 # UI 组件
│       ├── navbar.py               # 导航栏
│       └── param_editor.py         # 参数编辑器
│
├── utils/                          # 工具函数模块
│   ├── config_utils.py             # 配置工具
│   ├── exception_utils.py          # 异常处理（完整异常链）
│   ├── exceptions.py               # 自定义异常类
│   ├── logger_utils.py             # 日志工具
│   ├── validator_utils.py          # 验证工具
│   ├── visual_utils.py             # 可视化辅助
│   ├── performance_utils.py        # 性能监控
│   └── security_utils.py           # 安全工具
│
├── tests/                          # 单元测试
│   ├── conftest.py                 # 测试配置
│   ├── test_core/                  # 核心模块测试
│   └── test_utils/                 # 工具模块测试
│
├── scripts/                        # 辅助脚本
│   └── generate_sample_data.py     # 示例数据生成
│
├── docs/                           # 文档
│   ├── API_REFERENCE.md            # API 参考
│   ├── USER_GUIDE.md               # 用户指南
│   └── FAQ.md                      # 常见问题
│
├── data/                           # 示例数据
├── logs/                           # 日志目录
└── temp/                           # 临时文件目录
```

## 核心原则

1. **完全本地化**：所有功能在本地完成，无云端依赖
2. **开源合规**：使用开源免费工具
3. **开箱即用**：仅需安装依赖和启动命令
4. **友好容错**：完善的异常处理和中文提示，保留完整异常链
5. **中文适配**：所有界面和提示为中文

## 版本历史

### v3.2.0 (2026-04-27) — 稳定性修复版
- 🔴 修复 enrichment.py 中无意义的网络请求调用（完全离线化）
- 🔴 修复 qc_filter.py 稀疏矩阵类型错误（线粒体/核糖体比例计算）
- 🔴 修复 visualization.py 全局状态并发安全问题（改用显式 fig/ax）
- 🟡 修复 app.py 相对路径创建 temp/logs 目录问题
- 🟡 修复 analysis_pipeline.py 归一化前丢失原始 counts 层
- 🟡 修复 analysis_pipeline.py UMAP 重复传递 n_neighbors 参数
- 🟡 修复 exception_utils.py 异常链丢失问题
- 🟡 修复 ai_parser.py config key 不一致（scanpy_standard→scanpy 等）
- 🟢 downsampling.py 随机种子参数化
- 🟢 spatial_pipeline.py 配体-受体分析占位改为明确功能提示

### v3.1.0 (2026-04-15)
- 🔧 代码审查优化和清理
- 📦 UI 架构重构，新增配置管理和组件模块

### v3.0.0 (2026-04-01)
- ✨ 新增 AI 自然语言分析功能
- 🔧 内置规则解析器，支持自然语言需求转换

### v2.0.0 (2026-03-31)
- ✨ 新增空间转录组分析功能
- 🗺️ 支持 10x Visium 数据格式

### v1.0.0 (2026-03-30)
- 🎉 初始版本发布

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**：本工具仅供科研使用，不用于临床诊断。