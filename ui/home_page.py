import streamlit as st


def show():
    """
    首页 - 卡片式6个核心入口
    """
    # 页面标题
    st.title("🔬 LocalSingleCell")
    st.subheader("本地化单细胞&空间转录组分析工具")
    
    st.markdown("---")
    
    # ========================================
    # 6个核心入口卡片
    # ========================================
    
    # 定义6个核心入口
    entries = [
        {
            "icon": "🏠",
            "title": "首页",
            "description": "欢迎页 + 快速开始向导",
            "page": "首页",
            "color": "#134273"
        },
        {
            "icon": "📁",
            "title": "数据管理",
            "description": "数据导入 + 当前数据状态",
            "page": "数据导入",
            "color": "#1a5a96"
        },
        {
            "icon": "🔬",
            "title": "分析工具",
            "description": "一站式分析配置",
            "page": "分析工具",
            "color": "#2d8cf0"
        },
        {
            "icon": "📊",
            "title": "结果查看",
            "description": "可视化展示",
            "page": "结果查看",
            "color": "#28a745"
        },
        {
            "icon": "💾",
            "title": "导出",
            "description": "数据导出与报告生成",
            "page": "结果导出",
            "color": "#ffc107"
        },
        {
            "icon": "❓",
            "title": "帮助",
            "description": "使用指南与FAQ",
            "page": "帮助文档",
            "color": "#17a2b8"
        }
    ]
    
    # 渲染6个卡片 (3x2 网格)
    cols = st.columns(3)
    
    for idx, entry in enumerate(entries):
        col = cols[idx % 3]
        
        with col:
            # 卡片容器 - 使用 HTML 实现自定义样式
            card_html = f"""
            <div class="entry-card" style="background: linear-gradient(135deg, {entry['color']}, {entry['color']}dd);">
                <div class="entry-card-icon">{entry['icon']}</div>
                <h3 style="color: white !important; margin-bottom: 8px; font-size: 1.3rem;">{entry['title']}</h3>
                <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px; line-height: 1.5;">{entry['description']}</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 按钮触发跳转
            if st.button(f"进入{entry['title']}", key=f"btn_{entry['page']}", use_container_width=True):
                st.session_state.page = entry['page']
                st.rerun()
    
    st.markdown("---")
    
    # ========================================
    # 当前数据状态展示
    # ========================================
    
    # 检查是否有数据加载
    if st.session_state.get('is_data_loaded', False):
        st.success("✅ 已加载数据")
        
        # 显示数据基本信息
        data_col1, data_col2, data_col3, data_col4 = st.columns(4)
        
        anndata_obj = st.session_state.get('anndata_obj')
        
        with data_col1:
            if anndata_obj is not None:
                st.metric("细胞数", f"{anndata_obj.n_obs:,}")
        
        with data_col2:
            if anndata_obj is not None:
                st.metric("基因数", f"{anndata_obj.n_vars:,}")
        
        with data_col3:
            if anndata_obj is not None:
                st.metric("细胞类型数", f"{len(anndata_obj.obs.get('cell_type', []).unique()) if 'cell_type' in anndata_obj.obs else 'N/A'}")
        
        with data_col4:
            if anndata_obj is not None:
                st.metric("样本数", f"{len(anndata_obj.obs.get('sample', []).unique()) if 'sample' in anndata_obj.obs else 'N/A'}")
        
        # 数据类型标识
        is_spatial = st.session_state.get('is_spatial_data', False)
        if is_spatial:
            st.info("🗺️ 当前数据：空间转录组数据")
        else:
            st.info("🧬 当前数据：单细胞转录组数据")
    else:
        st.info("💡 欢迎使用 LocalSingleCell！请先导入数据开始分析。")
    
    st.markdown("---")
    
    # ========================================
    # 快速开始指南 (可折叠)
    # ========================================
    
    with st.expander("📖 快速开始指南", expanded=False):
        st.markdown("""
        ### 1. 导入数据
        点击上方的「📁 数据管理」卡片，进入数据导入页面：
        - 📁 本地h5ad文件导入
        - 📂 10x单细胞标准输出导入
        - 🔗 SRA号数据下载
        - 🧬 空间转录组数据导入
        
        ### 2. 配置分析
        点击「🔬 分析工具」卡片：
        - 调整质控、归一化、降维等参数
        - 使用AI自然语言描述需求
        - 一键执行分析
        
        ### 3. 查看结果
        点击「📊 结果查看」卡片：
        - UMAP/tSNE降维图
        - 细胞聚类图
        - 标记基因表达图
        
        ### 4. 导出结果
        点击「💾 导出」卡片：
        - 选择要导出的内容
        - 一键打包下载
        """)
    
    st.markdown("---")
    
    # ========================================
    # 技术栈信息
    # ========================================
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("### 🧬 核心库")
        st.markdown("""
        - **Scanpy**: 单细胞分析
        - **Squidpy**: 空间转录组
        - **GSEApy**: 基因富集
        """)
    
    with tech_col2:
        st.markdown("### 📊 可视化")
        st.markdown("""
        - **Plotly**: 交互式图表
        - **Matplotlib**: 基础图表
        - **Seaborn**: 统计可视化
        """)
    
    with tech_col3:
        st.markdown("### 🔧 技术")
        st.markdown("""
        - **Streamlit**: UI框架
        - **本地运行**: 数据安全
        - **开源免费**: 科研友好
        """)
    
    st.markdown("---")
    
    # 注意事项
    st.warning("""
    **注意事项**：
    - 本工具仅供科研使用，不用于临床诊断
    - 所有分析在本地完成，无数据上传到云端
    - 大样本数据可能需要较多内存
    """)


# 页面映射函数 - 将卡片名称映射到实际页面
def get_page_mapping(card_name):
    """将入口卡片名称映射到实际页面名称"""
    mapping = {
        "首页": "首页",
        "数据管理": "数据导入",
        "分析工具": "分析流程配置",  # 可扩展为显示选择器
        "结果查看": "结果可视化",
        "导出": "结果导出",
        "帮助": "帮助文档"
    }
    return mapping.get(card_name, card_name)