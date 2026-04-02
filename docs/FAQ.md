# LocalSingleCell 常见问题解答 (FAQ)

## 目录

- [安装与部署](#安装与部署)
- [数据导入](#数据导入)
- [质控过滤](#质控过滤)
- [分析流程](#分析流程)
- [可视化](#可视化)
- [富集分析](#富集分析)
- [导出与报告](#导出与报告)
- [错误处理](#错误处理)
- [性能优化](#性能优化)

---

## 安装与部署

### Q1: 支持哪些操作系统？

**A**: LocalSingleCell 支持以下操作系统：
- Windows 10/11
- macOS 10.15 (Catalina) 及以上
- Linux (Ubuntu 18.04+, CentOS 7+, Debian 10+)

### Q2: Python版本要求是什么？

**A**: 要求 Python 3.10 - 3.12。推荐使用 Python 3.11。

```bash
# 检查Python版本
python --version

# 使用conda创建环境
conda create -n lsc python=3.11
conda activate lsc
```

### Q3: pip安装依赖失败怎么办？

**A**: 尝试以下解决方案：

```bash
# 方案1: 升级pip
python -m pip install --upgrade pip

# 方案2: 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方案3: 逐个安装
pip install streamlit==1.32.2
pip install scanpy==1.10.1
# ... 其他依赖
```

### Q4: 如何在服务器上部署？

**A**: 服务器部署步骤：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 后台启动
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# 3. 或使用Docker
docker build -t localsinglecell .
docker run -d -p 8501:8501 localsinglecell
```

### Q5: 如何更新到最新版本？

**A**:
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
```

---

## 数据导入

### Q6: 支持哪些数据格式？

**A**: 支持以下格式：

| 格式 | 扩展名 | 说明 |
|-----|-------|------|
| h5ad | .h5ad | AnnData标准格式，推荐 |
| 10x | .zip | CellRanger输出，需压缩 |
| SRA | SRR号 | NCBI SRA数据库 |

### Q7: 文件上传大小有限制吗？

**A**: 默认限制为1GB。超过此大小的文件建议：
1. 使用降采样功能
2. 在本地预处理后再上传
3. 修改配置增加限制

### Q8: 10x数据如何上传？

**A**: 步骤如下：

```bash
# 1. 找到CellRanger输出目录
filtered_feature_bc_matrix/
├── barcodes.tsv.gz
├── features.tsv.gz
└── matrix.mtx.gz

# 2. 压缩为zip文件
zip -r data.zip filtered_feature_bc_matrix/

# 3. 在界面上传zip文件
```

### Q9: 导入数据后显示乱码怎么办？

**A**: 这通常是中文字体问题：

```python
# 程序会自动配置字体，如仍有问题：
# 1. 确保系统安装了中文字体
# Windows: 微软雅黑
# macOS: 苹方
# Linux: 文泉驿微米黑

# 2. 手动设置环境变量
export LANG=zh_CN.UTF-8
```

### Q10: SRA数据下载失败怎么办？

**A**: SRA下载需要预先安装SRA Toolkit：

```bash
# 下载SRA Toolkit
# Windows: https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/
# Linux:
wget https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-centos_linux64.tar.gz
tar -xzf sratoolkit.current-centos_linux64.tar.gz
export PATH=$PATH:$PWD/sratoolkit.*/bin

# 测试
prefetch --version
```

---

## 质控过滤

### Q11: 质控参数如何选择？

**A**: 推荐参数：

| 参数 | 10x数据 | Smart-seq数据 | 说明 |
|-----|---------|--------------|------|
| 最小基因数 | 200-500 | 1000-2000 | 过滤死细胞 |
| 最大基因数 | 5000-7000 | 8000-10000 | 过滤双细胞 |
| 最大MT比例 | 10-20% | 5-10% | 过滤低质量细胞 |

### Q12: 为什么需要过滤线粒体基因？

**A**: 线粒体基因比例高的原因：
- 细胞凋亡或坏死
- 细胞质RNA丢失
- 测序质量问题

高MT比例的细胞通常质量较差，建议过滤。

### Q13: 质控过滤后细胞太少怎么办？

**A**: 可能原因和解决方案：

| 原因 | 解决方案 |
|-----|---------|
| 参数过严 | 放宽min_genes、增加max_mt_percent |
| 数据质量问题 | 检查原始数据质量 |
| 样本特性 | 某些样本本身细胞数少 |

### Q14: 如何判断质控参数是否合适？

**A**: 查看质控指标分布：
1. 基因数分布应呈双峰，取中间区域
2. UMI数分布应呈对数正态分布
3. MT比例一般集中在低值区

---

## 分析流程

### Q15: 分析时间太长怎么办？

**A**: 优化建议：

| 细胞数 | 建议操作 |
|-------|---------|
| < 10,000 | 正常运行 |
| 10,000-50,000 | 减少高变基因数到1500 |
| > 50,000 | 启用降采样 |

### Q16: 聚类结果不理想怎么办？

**A**: 调整策略：

```yaml
# 聚类过多
resolution: 0.3  # 降低分辨率

# 聚类过少
resolution: 1.0  # 提高分辨率

# 聚类不清晰
n_pcs: 40        # 增加PCA主成分
n_neighbors: 20  # 增加邻居数
```

### Q17: 如何选择聚类分辨率？

**A**: 分辨率与聚类数的关系：

| 分辨率 | 预期聚类数 | 适用场景 |
|-------|-----------|---------|
| 0.1-0.3 | 3-5 | 大细胞类型 |
| 0.4-0.6 | 5-15 | 常规分析 |
| 0.7-1.0 | 10-20 | 细胞亚群 |
| 1.0-2.0 | 20+ | 稀有亚群 |

### Q18: PCA主成分数如何选择？

**A**: 建议方法：
1. 查看PCA方差贡献图，取拐点
2. 一般30-50个主成分足够
3. 复杂样本可增加到100

### Q19: UMAP和tSNE选哪个？

**A**: 对比：

| 特性 | UMAP | tSNE |
|-----|------|------|
| 速度 | 快 | 慢 |
| 全局结构 | 保留较好 | 保留较差 |
| 可解释性 | 较好 | 较差 |
| 推荐 | ✅ 首选 | 备选 |

---

## 可视化

### Q20: 图表中文乱码怎么办？

**A**: 程序已自动配置中文字体。如仍有问题：

```python
# 检查字体配置
import matplotlib.pyplot as plt
print(plt.rcParams['font.sans-serif'])
```

### Q21: 如何自定义图表颜色？

**A**: 在可视化页面可以：
1. 选择预设颜色主题
2. 自定义颜色列表

### Q22: 图表分辨率如何调整？

**A**: 导出时可选择：
- PNG 300dpi（推荐）
- PNG 600dpi（高清）
- PDF（矢量图）
- SVG（矢量图）

### Q23: 如何调整图表大小？

**A**: 在图表配置区域可以设置：
- 宽度（英寸）
- 高度（英寸）
- 点大小

---

## 富集分析

### Q24: 富集分析支持哪些数据库？

**A**: 支持的数据库：

| 数据库 | 全称 | 适用物种 |
|-------|------|---------|
| GO-BP | Gene Ontology Biological Process | 人/小鼠/大鼠 |
| GO-CC | Gene Ontology Cellular Component | 人/小鼠/大鼠 |
| GO-MF | Gene Ontology Molecular Function | 人/小鼠/大鼠 |
| KEGG | Kyoto Encyclopedia of Genes and Genomes | 人/小鼠/大鼠 |
| Reactome | Reactome Pathway Database | 人 |

### Q25: 富集分析结果为空怎么办？

**A**: 可能原因和解决方案：

| 原因 | 解决方案 |
|-----|---------|
| 差异基因太少 | 放宽p值和log2FC阈值 |
| 基因名格式不匹配 | 检查是否为标准基因名 |
| 网络问题 | 检查网络连接 |

### Q26: 如何选择合适的物种？

**A**: 物种选择：
- 人样本选择 "Human"
- 小鼠样本选择 "Mouse"
- 大鼠样本选择 "Rat"

### Q27: 富集结果如何解读？

**A**: 关键指标：

| 指标 | 说明 | 重要性 |
|-----|------|-------|
| Adjusted P-value | 校正后p值 | < 0.05显著 |
| Overlap | 富集基因数/背景基因数 | 越高越好 |
| Combined Score | 综合得分 | 用于排序 |

---

## 导出与报告

### Q28: 可以导出哪些结果？

**A**: 支持导出：

| 内容 | 格式 | 说明 |
|-----|------|------|
| AnnData对象 | .h5ad | 完整数据 |
| 质控结果 | .csv | 细胞信息 |
| 聚类结果 | .csv | 细胞标签 |
| 标记基因 | .csv | 各聚类标记 |
| 差异基因 | .csv | 差异分析结果 |
| 富集结果 | .xlsx | 各数据库结果 |
| 分析报告 | .html | 完整报告 |
| 图表 | .png/.pdf | 可视化结果 |

### Q29: 如何在其他软件中使用导出的数据？

**A**: h5ad文件兼容性：

```python
# Python (Scanpy)
import scanpy as sc
adata = sc.read_h5ad("adata.h5ad")

# R (Seurat)
library(SeuratDisk)
Convert("adata.h5ad", dest = "h5seurat")
adata <- LoadH5Seurat("adata.h5seurat")
```

### Q30: 分析报告包含哪些内容？

**A**: HTML报告包含：
- 数据基本信息
- 质控统计
- 聚类结果
- 核心图表
- 参数记录

---

## 错误处理

### Q31: 遇到MemoryError怎么办？

**A**: 解决方案：

```yaml
# 1. 启用降采样
downsampling:
  apply: true
  target_cells: 10000

# 2. 减少高变基因数
normalization:
  hvg:
    n_top_genes: 1500

# 3. 增加系统内存
```

### Q32: 程序崩溃无响应怎么办？

**A**: 排查步骤：
1. 查看logs目录下的日志文件
2. 检查内存使用情况
3. 尝试使用更小的数据集
4. 重启程序

### Q33: 错误代码含义？

**A**: 错误代码对照表：

| 代码 | 类型 | 说明 |
|-----|------|------|
| E101 | 文件错误 | 文件不存在 |
| E102 | 格式错误 | 文件格式无效 |
| E103 | 大小错误 | 文件过大 |
| E201 | 质控错误 | 质控参数问题 |
| E501 | 内存错误 | 内存不足 |
| E502 | 磁盘错误 | 磁盘空间不足 |

---

## 性能优化

### Q34: 如何处理大规模数据集？

**A**: 优化策略：

```yaml
# 大规模数据配置示例
performance:
  downsampling:
    apply: true
    target_cells: 20000
    method: random

  memory:
    gc_interval: 100

normalization:
  hvg:
    n_top_genes: 1500  # 减少基因数

clustering:
  n_pcs: 30           # 减少主成分
```

### Q35: 如何加速分析？

**A**: 加速建议：
1. 使用SSD硬盘
2. 关闭其他程序释放内存
3. 启用并行计算（配置n_jobs）
4. 使用降采样

### Q36: 支持GPU加速吗？

**A**: 目前不支持GPU加速，所有计算基于CPU。

---

## 其他问题

### Q37: 如何引用本项目？

**A**: 如在论文中使用，请引用：
```
LocalSingleCell: 本地化单细胞&空间转录组分析工具
https://github.com/your-repo/LocalSingleCell
```

### Q38: 如何获取帮助？

**A**: 获取帮助的方式：
1. 查看帮助文档页面
2. 阅读FAQ文档
3. 提交GitHub Issue
4. 查阅API文档

### Q39: 如何贡献代码？

**A**: 贡献流程：
1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 等待审核

### Q40: 数据安全吗？

**A**: 完全安全：
- 所有计算在本地完成
- 无网络数据传输
- 不收集用户数据
- 符合数据隐私要求

---

**版本**: v3.1.0
**更新日期**: 2026-04-02
