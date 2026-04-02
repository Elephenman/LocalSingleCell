import streamlit as st
import yaml
import os
from ui.sidebar import sidebar
from ui import (
    data_import_page, 
    pipeline_config_page, 
    visualization_page, 
    enrichment_page, 
    result_export_page, 
    help_page,
    spatial_pipeline_config_page,
    spatial_visualization_page,
    ai_analysis_page
)
from utils import config_utils, logger_utils, visual_utils

# 全局配置
st.set_page_config(
    page_title="LocalSingleCell - 本地化单细胞&空间转录组分析工具",
    page_icon="🔬",
    layout="wide"
)

# 初始化日志
logger = logger_utils.init_logger()

# 加载配置
config = config_utils.load_config()

# 初始化全局状态
if 'anndata_obj' not in st.session_state:
    st.session_state.anndata_obj = None
if 'is_data_loaded' not in st.session_state:
    st.session_state.is_data_loaded = False
if 'is_spatial_data' not in st.session_state:
    st.session_state.is_spatial_data = False
if 'is_analysis_done' not in st.session_state:
    st.session_state.is_analysis_done = False
if 'pipeline_config' not in st.session_state:
    st.session_state.pipeline_config = config.copy()
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = {}
if 'enrichment_result' not in st.session_state:
    st.session_state.enrichment_result = {}
if 'global_config' not in st.session_state:
    st.session_state.global_config = config.copy()

# 配置中文字体
visual_utils.setup_chinese_font()

# 侧边栏导航
page = sidebar()

# 页面路由
if page == "数据导入":
    data_import_page.show()
elif page == "AI自然语言分析":
    ai_analysis_page.show()
elif page == "分析流程配置":
    pipeline_config_page.show()
elif page == "结果可视化":
    visualization_page.show()
elif page == "空间分析流程配置":
    spatial_pipeline_config_page.show()
elif page == "空间结果可视化":
    spatial_visualization_page.show()
elif page == "基因富集分析":
    enrichment_page.show()
elif page == "结果导出":
    result_export_page.show()
elif page == "帮助文档":
    help_page.show()