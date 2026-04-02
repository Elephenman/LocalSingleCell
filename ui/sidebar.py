import streamlit as st


def sidebar():
    """
    侧边栏导航
    
    Returns:
        str: 选中的页面名称
    """
    # 侧边栏标题
    st.sidebar.title("LocalSingleCell")
    st.sidebar.subheader("本地化单细胞&空间转录组分析工具")
    
    # 判断是否是空间数据
    is_spatial = st.session_state.get('is_spatial_data', False)
    
    # 导航菜单
    if is_spatial:
        # 空间转录组导航
        page = st.sidebar.radio(
            "导航菜单",
            [
                "首页",
                "数据导入",
                "AI自然语言分析",
                "空间分析流程配置",
                "空间结果可视化",
                "基因富集分析",
                "结果导出",
                "帮助文档"
            ],
            index=0,
            format_func=lambda x: {
                "首页": "🏡 首页",
                "数据导入": "📁 数据导入",
                "AI自然语言分析": "🤖 AI自然语言分析",
                "空间分析流程配置": "⚙️ 空间分析流程配置",
                "空间结果可视化": "🗺️ 空间结果可视化",
                "基因富集分析": "🔬 基因富集分析",
                "结果导出": "💾 结果导出",
                "帮助文档": "❓ 帮助文档"
            }[x]
        )
    else:
        # 单细胞转录组导航
        page = st.sidebar.radio(
            "导航菜单",
            [
                "首页",
                "数据导入",
                "AI自然语言分析",
                "分析流程配置",
                "结果可视化",
                "基因富集分析",
                "结果导出",
                "帮助文档"
            ],
            index=0,
            format_func=lambda x: {
                "首页": "🏡 首页",
                "数据导入": "📁 数据导入",
                "AI自然语言分析": "🤖 AI自然语言分析",
                "分析流程配置": "⚙️ 分析流程配置",
                "结果可视化": "📊 结果可视化",
                "基因富集分析": "🔬 基因富集分析",
                "结果导出": "💾 结果导出",
                "帮助文档": "❓ 帮助文档"
            }[x]
        )
    
    # 侧边栏底部信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 关于")
    st.sidebar.markdown("版本: 3.1.0")
    st.sidebar.markdown("开源项目")
    st.sidebar.markdown("© 2026 LocalSingleCell")
    
    # 如果有page在session_state中，优先使用（用于页面跳转）
    if 'page' in st.session_state:
        page = st.session_state.page
        del st.session_state.page
    
    return page