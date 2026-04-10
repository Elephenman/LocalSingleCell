import streamlit as st
import hashlib


def render_top_nav():
    """
    NCBI风格顶部导航栏
    """
    # 注入自定义CSS
    st.markdown("""
    <style>
    /* 顶部导航栏样式 */
    .ncbi-navbar {
        background: linear-gradient(135deg, #1a5f7a 0%, #2d8a9e 50%, #159895 100%);
        padding: 0.5rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        border-radius: 0 0 8px 8px;
        margin-bottom: 1rem;
    }
    
    .ncbi-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: white;
        font-size: 1.3rem;
        font-weight: bold;
        text-decoration: none;
    }
    
    .ncbi-logo-icon {
        width: 32px;
        height: 32px;
        background: white;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    .ncbi-search {
        flex: 1;
        max-width: 500px;
        margin: 0 2rem;
        position: relative;
    }
    
    .ncbi-search input {
        width: 100%;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 20px;
        font-size: 0.95rem;
        background: rgba(255,255,255,0.95);
        transition: all 0.3s;
    }
    
    .ncbi-search input:focus {
        outline: none;
        background: white;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.3);
    }
    
    .ncbi-search button {
        position: absolute;
        right: 5px;
        top: 50%;
        transform: translateY(-50%);
        background: #1a5f7a;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .ncbi-nav-actions {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .ncbi-nav-btn {
        background: rgba(255,255,255,0.15);
        border: none;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .ncbi-nav-btn:hover {
        background: rgba(255,255,255,0.25);
    }
    
    /* 主导航菜单 */
    .ncbi-main-nav {
        background: #f8f9fa;
        border-bottom: 2px solid #dee2e6;
        padding: 0;
        margin-bottom: 1rem;
    }
    
    .ncbi-main-nav ul {
        display: flex;
        list-style: none;
        margin: 0;
        padding: 0;
    }
    
    .ncbi-main-nav li {
        padding: 0.8rem 1.2rem;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.2s;
        font-weight: 500;
        color: #495057;
    }
    
    .ncbi-main-nav li:hover {
        background: #e9ecef;
    }
    
    .ncbi-main-nav li.active {
        border-bottom-color: #1a5f7a;
        color: #1a5f7a;
    }
    
    /* 工具箱下拉菜单 */
    .ncbi-dropdown {
        position: relative;
    }
    
    .ncbi-dropdown-content {
        display: none;
        position: absolute;
        background: white;
        min-width: 200px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 8px;
        z-index: 1000;
        top: 100%;
        left: 0;
        margin-top: 0.5rem;
    }
    
    .ncbi-dropdown:hover .ncbi-dropdown-content {
        display: block;
    }
    
    .ncbi-dropdown-item {
        padding: 0.6rem 1rem;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .ncbi-dropdown-item:hover {
        background: #f8f9fa;
    }
    
    /* 面包屑 */
    .ncbi-breadcrumb {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0;
        font-size: 0.9rem;
        color: #6c757d;
    }
    
    .ncbi-breadcrumb a {
        color: #1a5f7a;
        text-decoration: none;
    }
    
    .ncbi-breadcrumb a:hover {
        text-decoration: underline;
    }
    
    /* 状态指示器 */
    .ncbi-status {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    
    .ncbi-status.ready {
        background: #d4edda;
        color: #155724;
    }
    
    .ncbi-status.empty {
        background: #fff3cd;
        color: #856404;
    }
    
    /* 卡片样式 */
    .ncbi-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s;
    }
    
    .ncbi-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .ncbi-card-header {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #1a5f7a;
    }
    
    /* 数据表格样式 */
    .ncbi-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .ncbi-table th {
        background: #f8f9fa;
        padding: 0.75rem;
        text-align: left;
        border-bottom: 2px solid #dee2e6;
        font-weight: 600;
    }
    
    .ncbi-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #dee2e6;
    }
    
    .ncbi-table tr:hover {
        background: #f8f9fa;
    }
    
    /* 帮助按钮 */
    .ncbi-help-btn {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #1a5f7a;
        color: white;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 9999;
    }
    
    .ncbi-help-btn:hover {
        background: #159895;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 顶部导航栏HTML
    navbar_html = """
    <div class="ncbi-navbar">
        <a href="#" class="ncbi-logo" onclick="return false;">
            <div class="ncbi-logo-icon">🔬</div>
            <span>LocalSingleCell</span>
        </a>
        <div class="ncbi-search">
            <input type="text" placeholder="搜索工具、基因名称、数据集..." id="ncbi-search-input">
            <button onclick="alert('搜索功能开发中...')">🔍</button>
        </div>
        <div class="ncbi-nav-actions">
            <button class="ncbi-nav-btn" onclick="alert('帮助文档开发中...')">❓ 帮助</button>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)


def render_main_nav(current_page: str = "首页"):
    """
    渲染主导航菜单（工具箱风格）
    """
    # 初始化session state
    if 'nav_section' not in st.session_state:
        st.session_state.nav_section = "首页"
    
    # 定义导航结构
    nav_items = {
        "首页": "home",
        "数据中心": "data",
        "分析工具": "analysis",
        "空间分析": "spatial",
        "AI分析": "ai",
        "教程": "help"
    }
    
    # CSS for main nav
    st.markdown("""
    <style>
    .main-nav-container {
        background: #f8f9fa;
        border-bottom: 2px solid #1a5f7a;
        padding: 0;
        margin-bottom: 1.5rem;
    }
    .main-nav-ul {
        display: flex;
        list-style: none;
        margin: 0;
        padding: 0;
    }
    .main-nav-item {
        padding: 0.8rem 1.5rem;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.2s;
        font-weight: 500;
        color: #495057;
    }
    .main-nav-item:hover {
        background: #e9ecef;
    }
    .main-nav-item.active {
        border-bottom-color: #1a5f7a;
        color: #1a5f7a;
        background: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 使用columns渲染导航
    cols = st.columns(len(nav_items))
    
    for idx, (label, section) in enumerate(nav_items.items()):
        with cols[idx]:
            is_active = st.session_state.get('nav_section', '首页') == label
            btn_type = "primary" if is_active else "secondary"
            
            if st.button(
                f"**{label}**",
                key=f"nav_{section}",
                use_container_width=True,
                type=btn_type if label == current_page else "tertiary"
            ):
                st.session_state.nav_section = label
                st.rerun()


def render_toolbox_menu(section: str):
    """
    渲染工具箱下拉菜单（侧边）
    """
    # 根据当前section显示对应的工具
    tool_menus = {
        "首页": [
            ("快速导入", "data_import"),
            ("新建分析", "new_analysis"),
            ("查看教程", "tutorial")
        ],
        "数据中心": [
            ("数据导入", "data_import"),
            ("数据浏览", "data_browse"),
            ("数据导出", "data_export")
        ],
        "分析工具": [
            ("质控过滤", "qc"),
            ("降维聚类", "dim_reduce"),
            ("差异分析", "diff_analysis"),
            ("富集分析", "enrichment")
        ],
        "空间分析": [
            ("空间数据", "spatial_data"),
            ("空间可视化", "spatial_viz"),
            ("空间统计", "spatial_stats")
        ],
        "AI分析": [
            ("自然语言分析", "nl_analysis"),
            ("命令历史", "cmd_history")
        ],
        "教程": [
            ("使用指南", "user_guide"),
            ("API文档", "api_doc"),
            ("常见问题", "faq")
        ]
    }
    
    tools = tool_menus.get(section, [])
    
    if tools:
        with st.sidebar:
            st.markdown("### 🧰 工具箱")
            for tool_name, tool_key in tools:
                if st.button(f"▸ {tool_name}", key=f"tool_{tool_key}", use_container_width=True):
                    st.session_state.current_tool = tool_key
                    st.rerun()


def render_status_indicator():
    """
    渲染状态指示器
    """
    is_loaded = st.session_state.get('is_data_loaded', False)
    is_spatial = st.session_state.get('is_spatial_data', False)
    
    # 检查数据状态
    if is_loaded:
        anndata = st.session_state.get('anndata_obj')
        if anndata is not None:
            n_cells = anndata.n_obs
            n_genes = anndata.n_vars
            status_text = f"已加载: {n_cells:,} 细胞 × {n_genes:,} 基因"
            if is_spatial:
                status_text += " (空间数据)"
            st.markdown(f'<div class="ncbi-status ready">✅ {status_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ncbi-status empty">⚠️ 数据未就绪</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ncbi-status empty">📭 未加载数据</div>', unsafe_allow_html=True)


def render_breadcrumb(*items):
    """
    渲染面包屑导航
    """
    if not items:
        return
    
    breadcrumb_html = '<div class="ncbi-breadcrumb">'
    for idx, item in enumerate(items):
        if idx > 0:
            breadcrumb_html += ' <span>›</span> '
        breadcrumb_html += f'<span>{item}</span>'
    breadcrumb_html += '</div>'
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)