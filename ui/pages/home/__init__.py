import streamlit as st


def show():
    """NCBI风格首页"""
    
    # 导入导航组件
    from ui.components.navbar import render_status_indicator
    
    # 欢迎区
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a5f7a 0%, #2d8a9e 50%, #159895 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    ">
        <h1 style="margin: 0; font-size: 2rem;">🔬 LocalSingleCell</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            本地化单细胞&空间转录组分析平台
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 状态指示器
    col_status, col_action = st.columns([3, 1])
    with col_status:
        render_status_indicator()
    with col_action:
        pass
    
    st.markdown("---")
    
    # 功能模块卡片区
    st.markdown("### 🔧 分析工具")
    
    # 四大功能模块
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="ncbi-card" onclick="document.getElementById('btn-sc').click()">
            <div class="ncbi-card-header">📊 单细胞转录组分析</div>
            <p>完整的单细胞分析流程：质控、归一化、降维、聚类、差异分析</p>
            <span style="color: #1a5f7a; font-size: 0.9rem;">→ 进入分析</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("单细胞分析", key="btn-sc", use_container_width=True):
            st.session_state.analysis_type = "single_cell"
            st.rerun()
        
        st.markdown("""
        <div class="ncbi-card" onclick="document.getElementById('btn-enrich').click()">
            <div class="ncbi-card-header">🧬 基因富集分析</div>
            <p>GO、KEGG、Reactome富集分析，功能通路解读</p>
            <span style="color: #1a5f7a; font-size: 0.9rem;">→ 开始富集</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("基因富集", key="btn-enrich", use_container_width=True):
            st.session_state.current_page = "enrichment"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="ncbi-card" onclick="document.getElementById('btn-spatial').click()">
            <div class="ncbi-card-header">🗺️ 空间转录组分析</div>
            <p>10x Visium数据处理，空间可视化，热点分析</p>
            <span style="color: #1a5f7a; font-size: 0.9rem;">→ 进入空间</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("空间分析", key="btn-spatial", use_container_width=True):
            st.session_state.analysis_type = "spatial"
            st.rerun()
        
        st.markdown("""
        <div class="ncbi-card" onclick="document.getElementById('btn-ai').click()">
            <div class="ncbi-card-header">🤖 AI自然语言分析</div>
            <p>用自然语言描述需求，AI自动完成参数配置和执行</p>
            <span style="color: #1a5f7a; font-size: 0.9rem;">→ AI分析</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("AI分析", key="btn-ai", use_container_width=True):
            st.session_state.current_page = "AI自然语言分析"
            st.rerun()
    
    st.markdown("---")
    
    # 快捷操作区
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📁 导入数据", use_container_width=True):
            st.session_state.current_page = "数据导入"
            st.rerun()
    
    with col_q2:
        if st.button("📤 导出结果", use_container_width=True):
            st.session_state.current_page = "结果导出"
            st.rerun()
    
    with col_q3:
        if st.button("⚙️ 配置流程", use_container_width=True):
            st.session_state.current_page = "分析流程配置"
            st.rerun()
    
    with col_q4:
        if st.button("❓ 帮助文档", use_container_width=True):
            st.session_state.current_page = "帮助文档"
            st.rerun()
    
    st.markdown("---")
    
    # 快速开始指南（NCBI风格）
    st.markdown("## 🚀 快速开始")
    
    with st.expander("📖 查看使用教程", expanded=False):
        st.markdown("""
        ### 1. 导入数据
        - **本地文件**：支持 h5ad、10x MTX、RDS 格式
        - **SRA下载**：输入SRA号自动下载
        - **示例数据**：内置测试数据快速体验
        
        ### 2. 配置分析
        - 质控参数：线粒体基因比例、细胞计数阈值
        - 聚类参数：分辨率、算法选择
        - 降维方法：PCA、UMAP、tSNE
        
        ### 3. 执行分析
        - 一键分析：自动完成全流程
        - 分步执行：逐个模块运行检查
        
        ### 4. 查看结果
        - 交互式可视化
        - 图表下载
        - 结果导出
        """)
    
    # 数据信息（如果有）
    if st.session_state.get('is_data_loaded', False):
        anndata = st.session_state.get('anndata_obj')
        if anndata is not None:
            st.markdown("---")
            st.markdown("### 📊 当前数据概览")
            
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            
            with info_col1:
                st.metric("细胞数", f"{anndata.obs.shape[0]:,}")
            
            with info_col2:
                st.metric("基因数", f"{anndata.var.shape[0]:,}")
            
            with info_col3:
                n_celltypes = anndata.obs.get('cell_type', anndata.obs.get('Cluster', 'Unknown')).nunique()
                st.metric("细胞类型数", n_celltypes)
            
            with info_col4:
                spatial = "是" if st.session_state.get('is_spatial_data', False) else "否"
                st.metric("空间数据", spatial)
    
    # 系统信息
    st.markdown("---")
    st.caption(f"🖥️ LocalSingleCell v2.0 | 运行平台: 本地 | 环境: Python 3.10+")