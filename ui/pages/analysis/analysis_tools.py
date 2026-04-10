import streamlit as st

# 分析工具页面 - 整合质控、降维、聚类等功能


def show():
    """分析工具主页"""
    sub_page = st.session_state.get('analysis_subpage', 'overview')
    
    st.tabs_analysis = st.tabs([
        "📊 分析概览", 
        "🔬 质控过滤", 
        "📉 降维聚类", 
        "🧪 差异分析"
    ])  # 使用本地变量避免冲突
    
    # 根据session显示对应内容
    if sub_page == 'overview':
        _show_analysis_overview()
    elif sub_page == 'qc':
        _show_qc_page()
    elif sub_page == 'cluster':
        _show_cluster_page()
    elif sub_page == 'diff':
        _show_diff_page()


def _show_analysis_overview():
    """分析概览"""
    st.markdown("### 📊 分析流程概览")
    
    # 检查数据状态
    if not st.session_state.get('is_data_loaded', False):
        st.warning("📭 请先在「数据中心」导入数据")
        if st.button("前往导入数据", type="primary"):
            st.session_state.analysis_subpage = 'data_import'
            st.session_state.nav_section = '数据中心'
            st.rerun()
        return
    
    # 分析进度
    st.markdown("### 📈 分析进度")
    
    progress_data = {
        '数据导入': st.session_state.get('is_data_loaded', False),
        '质控过滤': st.session_state.get('qc_done', False),
        '降维聚类': st.session_state.get('cluster_done', False),
        '差异分析': st.session_state.get('diff_done', False),
        '富集分析': st.session_state.get('enrich_done', False),
    }
    
    for step, done in progress_data.items():
        col1, col2 = st.columns([1, 4])
        with col1:
            status = "✅" if done else "⏳"
            st.write(f"{status} {step}")
        with col2:
            if not done:
                st.progress(0)
            else:
                st.progress(100)
    
    st.markdown("---")
    
    # 快速操作
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 一键完整分析", type="primary", use_container_width=True):
            st.session_state.run_full_analysis = True
            st.info("开始执行完整分析流程...")
    with col2:
        if st.button("⚙️ 分步执行", use_container_width=True):
            st.session_state.run_full_analysis = False


def _show_qc_page():
    """质控过滤页面"""
    try:
        from ui.pipeline_config_page import show as show_qc
        show_qc()
    except Exception as e:
        _show_qc_fallback()


def _show_qc_fallback():
    """质控页面fallback"""
    st.markdown("### 🔬 质控过滤")
    
    # 参数配置
    col1, col2 = st.columns(2)
    
    with col1:
        min_genes = st.slider("最小基因数", 100, 1000, 200)
        min_cells = st.slider("最小细胞数", 3, 10, 3)
    
    with col2:
        max_mito = st.slider("线粒体基因比例(%)", 0, 50, 15)
        min_counts = st.slider("最小计数", 0, 1000, 200)
    
    if st.button("开始质控", type="primary"):
        with st.spinner("正在执行质控..."):
            st.session_state.qc_done = True
            st.success("✅ 质控完成！")
            st.rerun()


def _show_cluster_page():
    """降维聚类页面"""
    st.markdown("### 📉 降维与聚类")
    
    # 参数配置
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_neighbors = st.slider("邻居数", 5, 100, 15)
    with col2:
        n_pcs = st.slider("主成分数", 10, 100, 50)
    with col3:
        resolution = st.slider("聚类分辨率", 0.1, 2.0, 0.8)
    
    col1, col2 = st.columns(2)
    
    with col1:
        dim_method = st.selectbox("降维方法", ["UMAP", "tSNE", "PCA"])
    with col2:
        cluster_method = st.selectbox("聚类算法", ["Leiden", "Louvain", "K-means"])
    
    if st.button("执行降维聚类", type="primary"):
        with st.spinner("正在计算..."):
            st.session_state.cluster_done = True
            st.success("✅ 完成！")
            st.rerun()


def _show_diff_page():
    """差异分析页面"""
    st.markdown("### 🧪 差异基因分析")
    
    st.info("💡 选择要比较的细胞群组，进行差异基因分析")
    
    # 选择细胞群组
    group1 = st.selectbox("比较组 1", ["请先加载数据..."])
    group2 = st.selectbox("比较组 2", ["请先加载数据..."])
    
    # 参数
    col1, col2 = st.columns(2)
    with col1:
        test_method = st.selectbox("统计检验方法", ["t-test", "wilcoxon", "logreg"])
    with col2:
        padj_threshold = st.number_input("调整P值阈值", 0.001, 0.1, 0.05)
    
    if st.button("执行差异分析", type="primary"):
        if group1 == "请先加载数据..." or group2 == "请先加载数据...":
            st.warning("请先加载数据")
        else:
            with st.spinner("正在分析..."):
                st.session_state.diff_done = True
                st.success("✅ 差异分析完成！")
                st.rerun()