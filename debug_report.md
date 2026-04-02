# LocalSingleCell 代码调试报告

## 📅 调试日期
2026-04-01

---

## 🔍 一、问题清单

### 问题 1: spatial_visualization_page.py 中 st.slider 的 value=None 导致错误
**文件位置**: `ui/spatial_visualization_page.py:43`
**行号**: 43, 97
**严重程度**: 🔴 高
**问题描述**:
```python
spot_size = st.slider("点大小", min_value=1, max_value=50, step=1, value=None)
```
Streamlit 的 slider 组件不接受 `value=None`，这会导致运行时错误。

**根本原因**:
st.slider 需要一个有效的默认值，而不是 None。

**修复方案**:
- 方案1：设置默认值，例如 `value=10`
- 方案2：使用 `None` 以外的默认值，并在代码中处理

---

### 问题 2: spatial_visualization.py 中空间可变基因绘图逻辑问题
**文件位置**: `core/spatial_visualization.py:135-171`
**行号**: 147-164
**严重程度**: 🟡 中
**问题描述**:
```python
fig, ax = plt.subplots(figsize=(10, 6))
if 'moranI' in adata.uns:
    # ...
    sq.pl.spatial_scatter(..., show=False)
    fig = plt.gcf()  # 这里会覆盖之前创建的 fig
else:
    ax.text(...)
```
当有结果时，`fig` 被 `plt.gcf()` 覆盖，可能导致不一致。

**根本原因**:
创建了初始 figure，但随后用 `plt.gcf()` 替换，造成不必要的复杂性。

**修复方案**:
- 方案1：不在有结果分支前创建 figure
- 方案2：保持 figure 创建逻辑一致

---

### 问题 3: spatial_loader.py 中空间数据验证检查过度严格
**文件位置**: `core/spatial_loader.py:72-96`
**行号**: 89-94
**严重程度**: 🟡 中
**问题描述**:
```python
if 'spatial' not in adata.uns or 'images' not in adata.uns['spatial']:
    issues.append("缺少组织切片图像")
```
有些空间转录组数据可能没有图像但仍有空间坐标，这样的检查会导致用户无法使用这些数据。

**根本原因**:
将图像作为必需条件，但实际中空间坐标才是空间转录组的核心。

**修复方案**:
- 方案1：降低图像检查的严格程度，改为警告而非错误
- 方案2：让图像检查为可选

---

### 问题 4: spatial_pipeline_config_page.py 中 st.experimental_rerun 已弃用
**文件位置**: `ui/spatial_pipeline_config_page.py:29`
**行号**: 29, 59, 315
**严重程度**: 🟡 中
**问题描述**:
```python
st.experimental_rerun()
```
在新版本 Streamlit 中，`st.experimental_rerun()` 已被弃用，应该使用 `st.rerun()`。

**根本原因**:
使用了过时的 API。

**修复方案**:
- 将 `st.experimental_rerun()` 替换为 `st.rerun()`

---

### 问题 5: data_import_page.py 中同样使用了已弃用的 experimental_rerun
**文件位置**: `ui/data_import_page.py:53`
**行号**: 53, 112, 236, 291
**严重程度**: 🟡 中
**问题描述**:
同上，使用了已弃用的 API。

**根本原因**:
同上。

**修复方案**:
同上。

---

### 问题 6: spatial_visualization.py 中 plot_genes_spatial 在无图像时的逻辑不完整
**文件位置**: `core/spatial_visualization.py:78-132`
**行号**: 108-116
**严重程度**: 🟢 低
**问题描述**:
`plot_genes_spatial` 函数只绘制空间散点图，但无法方便地叠加图像。虽然有 `plot_image_with_overlay`，但多基因的情况没有对应的函数。

**根本原因**:
功能设计上的缺口。

**修复方案**:
- 方案1：添加可选参数支持图像叠加
- 方案2：保持现状，在页面级别处理

---

### 问题 7: spatial_pipeline_config_page.py 中页面跳转逻辑有问题
**文件位置**: `ui/spatial_pipeline_config_page.py:294-315`
**行号**: 297-298
**严重程度**: 🟡 中
**问题描述**:
```python
# 跳转到空间结果可视化页面
st.session_state.page = "空间结果可视化"
# ... 执行分析 ...
st.experimental_rerun()
```
在设置 `page` 状态后立即执行长时间运行的分析，这可能导致页面跳转与分析执行的时序问题。

**根本原因**:
状态设置和分析执行的顺序可能需要调整。

**修复方案**:
- 方案1：先执行分析，完成后再设置跳转
- 方案2：使用 Streamlit 的状态管理更好地处理

---

### 问题 8: spatial_pipeline.py 中空间可变基因参数可能有兼容性问题
**文件位置**: `core/spatial_pipeline.py:129-134`
**行号**: 133
**严重程度**: 🟡 中
**问题描述**:
```python
genes='highly_variable' if config['normalization']['hvg']['apply'] else None
```
`squidpy.gr.spatial_autocorr` 的 `genes` 参数接受的格式需要确认，可能不是直接接受 'highly_variable' 字符串。

**根本原因**:
API 调用参数可能不正确。

**修复方案**:
- 方案1：检查 Squidpy 文档，确保参数格式正确
- 方案2：如果 'highly_variable' 不可用，直接传入高变基因列表

---

## 📊 二、问题统计

| 严重程度 | 数量 | 占比 |
|---------|------|------|
| 🔴 高 | 1 | 12.5% |
| 🟡 中 | 5 | 62.5% |
| 🟢 低 | 2 | 25.0% |

**总计**: 8 个问题

---

## 🔧 三、修复优先级建议

### 立即修复（P0）
1. 问题 1: st.slider value=None 错误 - 会导致直接崩溃

### 尽快修复（P1）
2. 问题 4, 5: 弃用 API 更新
3. 问题 7: 页面跳转逻辑
4. 问题 8: 空间可变基因参数

### 计划修复（P2）
5. 问题 2: 绘图逻辑优化
6. 问题 3: 数据验证严格度
7. 问题 6: 多基因图像叠加

---

## 📝 四、总体评估

### 代码质量
- ✅ 语法检查全部通过
- ✅ 模块导入基本正常
- ⚠️ 存在一些运行时潜在问题
- ⚠️ 使用了一些已弃用的 API

### 架构设计
- ✅ 模块化设计良好
- ✅ 职责分离清晰
- ⚠️ 部分页面间跳转逻辑需要优化

### 建议
1. 优先修复会导致崩溃的问题（问题 1）
2. 逐步更新弃用的 API
3. 添加更完善的错误处理
4. 考虑添加单元测试

---

## 🚀 五、下一步行动

1. 按照优先级顺序修复问题
2. 修复后重新进行全面测试
3. 测试空间转录组端到端流程
4. 生成修复报告
