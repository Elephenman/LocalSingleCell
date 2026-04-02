import streamlit as st


def show():
    """
    首页欢迎页面
    """
    st.title("🔬 LocalSingleCell")
    st.subheader("本地化单细胞&空间转录组分析工具")
    
    st.markdown("---")
    
    # 功能介绍卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 单细胞分析")
        st.markdown("""
        - 数据质控与过滤
        - 降维与聚类分析
        - 差异基因分析
        - 基因富集分析
        """)
    
    with col2:
        st.markdown("### 🗺️ 空间转录组")
        st.markdown("""
        - 空间数据导入
        - 空间可变基因
        - 空间可视化
        - 配体-受体分析
        """)
    
    with col3:
        st.markdown("### 🤖 AI自然语言")
        st.markdown("""
        - 自然语言需求解析
        - 智能参数配置
        - 一键分析执行
        - 友好的交互体验
        """)
    
    st.markdown("---")
    
    # 快速开始指南
    st.markdown("## 🚀 快速开始")
    
    st.markdown("### 1. 导入数据")
    st.info("点击左侧导航栏「🏠 数据导入」，选择合适的数据导入方式：")
    st.markdown("- 📁 本地h5ad文件导入")
    st.markdown("- 📂 10x单细胞标准输出导入")
    st.markdown("- 🔗 SRA号数据下载")
    st.markdown("- 🧬 空间转录组数据导入")
    
    st.markdown("### 2. 配置分析参数")
    st.info("数据导入成功后，进入「⚙️ 分析流程配置」页面：")
    st.markdown("- 调整质控、归一化、降维等参数")
    st.markdown("- 预览质控结果")
    st.markdown("- 执行一键分析")
    
    st.markdown("### 3. 查看可视化结果")
    st.info("分析完成后，在「📊 结果可视化」页面查看图表：")
    st.markdown("- UMAP/tSNE降维图")
    st.markdown("- 细胞聚类图")
    st.markdown("- 标记基因表达图")
    st.markdown("- 火山图等差异基因可视化")
    
    st.markdown("### 4. 进行基因富集分析")
    st.info("在「🔬 基因富集分析」页面：")
    st.markdown("- 选择差异基因集")
    st.markdown("- 选择富集数据库（GO、KEGG、Reactome）")
    st.markdown("- 查看富集结果和气泡图")
    
    st.markdown("### 5. 导出分析结果")
    st.info("在「💾 结果导出」页面：")
    st.markdown("- 选择要导出的内容")
    st.markdown("- 一键打包下载")
    st.markdown("- 保存分析报告")
    
    st.markdown("---")
    
    # AI自然语言分析介绍
    st.markdown("## 🤖 使用AI自然语言分析")
    st.success("不想手动配置参数？试试AI自然语言分析！")
    st.markdown("""
    1. 导入数据后，进入「🤖 AI自然语言分析」页面
    2. 用中文描述你的分析需求，例如：
       - "帮我过滤线粒体比例超过15%的细胞，用分辨率0.8聚类"
       - "做GO和KEGG富集分析，生成UMAP图和火山图"
    3. 点击「解析需求」查看AI生成的参数
    4. 确认无误后点击「一键执行分析」
    """)
    
    # 示例需求按钮
    st.markdown("### 示例需求")
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("💡 基础分析示例"):
            st.session_state.example_requirement = "帮我做一个基础的单细胞分析，用默认参数"
            st.success("已复制示例需求，请前往AI自然语言分析页面")
    
    with example_col2:
        if st.button("🎯 严格质控示例"):
            st.session_state.example_requirement = "过滤线粒体比例超过10%的细胞，最少200个基因，用分辨率0.5聚类"
            st.success("已复制示例需求，请前往AI自然语言分析页面")
    
    with example_col3:
        if st.button("📊 富集分析示例"):
            st.session_state.example_requirement = "做GO和KEGG富集分析，生成UMAP图、火山图和气泡图"
            st.success("已复制示例需求，请前往AI自然语言分析页面")
    
    st.markdown("---")
    
    # 技术栈介绍
    st.markdown("## 🛠️ 技术栈")
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("### 核心库")
        st.markdown("- **Streamlit 1.30+**: 低代码UI框架")
        st.markdown("- **Scanpy 1.10+**: 单细胞分析金标准")
        st.markdown("- **Squidpy 1.4+**: 空间转录组分析")
        st.markdown("- **GSEApy**: 基因富集分析")
    
    with tech_col2:
        st.markdown("### 可视化库")
        st.markdown("- **Matplotlib**: 基础图表")
        st.markdown("- **Seaborn**: 统计可视化")
        st.markdown("- **Plotly**: 交互式图表")
    
    st.markdown("---")
    
    # 注意事项
    st.warning("""
    **注意事项**：
    - 本工具仅供科研使用，不用于临床诊断
    - 所有分析在本地完成，无数据上传到云端
    - 大样本数据可能需要较多内存，请确保电脑配置足够
    """)
    
    # 下一步按钮
    st.markdown("---")
    if st.button("🏠 开始使用 - 前往数据导入页面", type="primary", use_container_width=True):
        st.session_state.page = "数据导入"
        st.rerun()
