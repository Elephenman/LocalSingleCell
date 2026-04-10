import streamlit as st


def show():
    """数据中心首页 - 整合数据导入和浏览"""
    # 数据导入子页面
    sub_page = st.session_state.get('data_subpage', '导入')
    
    # 子页面标签
    st.tabs_list = st.tabs(["📥 数据导入", "🔍 数据浏览", "📤 数据导出"])
    
    # 根据选择渲染对应页面
    if sub_page == "导入":
        try:
            from ui.data_import_page import show as show_import
            show_import()
        except Exception as e:
            st.error(f"加载数据导入页面失败: {e}")
    elif sub_page == "浏览":
        _show_data_browser()
    elif sub_page == "导出":
        _show_data_export()


def _show_data_browser():
    """数据浏览器"""
    st.markdown("### 🔍 数据浏览器")
    
    if not st.session_state.get('is_data_loaded', False):
        st.warning("📭 未加载任何数据。请先在「数据导入」页面加载数据。")
        return
    
    anndata = st.session_state.get('anndata_obj')
    if anndata is None:
        st.warning("⚠️ 数据对象为空")
        return
    
    # 数据概览
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("细胞数", f"{anndata.n_obs:,}")
    with col2:
        st.metric("基因数", f"{anndata.n_vars:,}")
    with col3:
        st.metric("空间数据", "是" if st.session_state.get('is_spatial_data', False) else "否")
    
    # 数据信息
    with st.expander("📊 查看观测信息 (obs)", expanded=True):
        st.dataframe(anndata.obs.head(50), use_container_width=True)
        st.caption(f"共 {anndata.obs.shape[0]} 行 × {anndata.obs.shape[1]} 列")
    
    with st.expander("🧬 查看变量信息 (var)"):
        st.dataframe(anndata.var.head(50), use_container_width=True)
        st.caption(f"共 {anndata.var.shape[0]} 行 × {anndata.var.shape[1]} 列")


def _show_data_export():
    """数据导出"""
    st.markdown("### 📤 数据导出")
    
    if not st.session_state.get('is_analysis_done', False):
        st.warning("⚠️ 请先完成分析后再导出结果。")
        return
    
    export_type = st.selectbox("导出类型", ["分析结果数据", "可视化图像", "完整报告"])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("💡 选择要导出的内容，点击下载即可保存到本地")
    with col2:
        if st.button("📥 下载", type="primary"):
            st.toast("导出功能开发中...")