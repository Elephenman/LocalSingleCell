import streamlit as st
import yaml
import os
import traceback

# 全局配置
st.set_page_config(
    page_title="LocalSingleCell - 本地化单细胞&空间转录组分析工具",
    page_icon="🔬",
    layout="wide"
)

# ============================================================================
# Phase 1 UI 美化: 加载自定义 CSS
# 主色调: #134273 (NCBI Blue)
# ============================================================================

def load_custom_css():
    """加载自定义CSS样式文件"""
    css_file = os.path.join(os.path.dirname(__file__), '.streamlit', 'custom.css')
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        # 使用 unsafe_allow_html 允许自定义样式
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# 页面配置后立即加载CSS（确保样式在页面渲染前生效）
load_custom_css()

# 创建temp和logs目录
os.makedirs("temp", exist_ok=True)
os.makedirs("logs", exist_ok=True)

try:
    # 导入基础模块
    from utils import config_utils, logger_utils, visual_utils
    
    # 初始化日志
    logger = logger_utils.init_logger()
    
    # 加载配置
    config = config_utils.load_config()
    
    # 配置中文字体
    visual_utils.setup_chinese_font()
    
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
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "首页"
    
    # 导入侧边栏
    from ui.sidebar import sidebar
    
    # 导入UI页面（逐个尝试）
    ui_modules = {}
    
    # 首页
    try:
        from ui import home_page
        ui_modules['home'] = home_page
    except Exception as e:
        st.warning(f"⚠️ home_page 导入失败: {e}")
    
    # 数据导入
    try:
        from ui import data_import_page
        ui_modules['data_import'] = data_import_page
    except Exception as e:
        st.warning(f"⚠️ data_import_page 导入失败: {e}")
    
    # AI分析
    try:
        from ui import ai_analysis_page
        ui_modules['ai_analysis'] = ai_analysis_page
    except Exception as e:
        st.warning(f"⚠️ ai_analysis_page 导入失败: {e}")
    
    # 分析流程配置
    try:
        from ui import pipeline_config_page
        ui_modules['pipeline_config'] = pipeline_config_page
    except Exception as e:
        st.warning(f"⚠️ pipeline_config_page 导入失败: {e}")
    
    # 结果可视化
    try:
        from ui import visualization_page
        ui_modules['visualization'] = visualization_page
    except Exception as e:
        st.warning(f"⚠️ visualization_page 导入失败: {e}")
    
    # 基因富集分析
    try:
        from ui import enrichment_page
        ui_modules['enrichment'] = enrichment_page
    except Exception as e:
        st.warning(f"⚠️ enrichment_page 导入失败: {e}")
    
    # 结果导出
    try:
        from ui import result_export_page
        ui_modules['result_export'] = result_export_page
    except Exception as e:
        st.warning(f"⚠️ result_export_page 导入失败: {e}")
    
    # 帮助文档
    try:
        from ui import help_page
        ui_modules['help'] = help_page
    except Exception as e:
        st.warning(f"⚠️ help_page 导入失败: {e}")
    
    # 空间分析流程配置
    try:
        from ui import spatial_pipeline_config_page
        ui_modules['spatial_pipeline_config'] = spatial_pipeline_config_page
    except Exception as e:
        st.warning(f"⚠️ spatial_pipeline_config_page 导入失败: {e}")
    
    # 空间结果可视化
    try:
        from ui import spatial_visualization_page
        ui_modules['spatial_visualization'] = spatial_visualization_page
    except Exception as e:
        st.warning(f"⚠️ spatial_visualization_page 导入失败: {e}")
    
    # 侧边栏导航
    page = sidebar()
    
    # 处理从首页卡片点击的页面跳转
    # 卡片名称到实际页面名称的映射
    card_to_page_mapping = {
        "首页": "首页",
        "数据导入": "数据导入",
        "分析工具": "分析流程配置",  # 分析工具卡片跳转到分析流程配置
        "结果查看": "结果可视化",    # 结果查看卡片跳转到结果可视化
        "结果导出": "结果导出",
        "帮助文档": "帮助文档"
    }
    
    # 如果session_state中有page，说明是从卡片点击跳转的
    if 'page' in st.session_state:
        card_page = st.session_state.pop('page')
        # 使用映射转换为实际页面名称
        page = card_to_page_mapping.get(card_page, card_page)
    
    # 页面路由
    if page == "首页":
        if 'home' in ui_modules:
            ui_modules['home'].show()
        else:
            st.error("❌ 首页不可用")
    elif page == "数据导入":
        if 'data_import' in ui_modules:
            ui_modules['data_import'].show()
        else:
            st.error("❌ 数据导入页面不可用")
    elif page == "AI自然语言分析":
        if 'ai_analysis' in ui_modules:
            ui_modules['ai_analysis'].show()
        else:
            st.error("❌ AI分析页面不可用")
    elif page == "分析流程配置":
        if 'pipeline_config' in ui_modules:
            ui_modules['pipeline_config'].show()
        else:
            st.error("❌ 分析流程配置页面不可用")
    elif page == "结果可视化":
        if 'visualization' in ui_modules:
            ui_modules['visualization'].show()
        else:
            st.error("❌ 结果可视化页面不可用")
    elif page == "空间分析流程配置":
        if 'spatial_pipeline_config' in ui_modules:
            ui_modules['spatial_pipeline_config'].show()
        else:
            st.error("❌ 空间分析流程配置页面不可用")
    elif page == "空间结果可视化":
        if 'spatial_visualization' in ui_modules:
            ui_modules['spatial_visualization'].show()
        else:
            st.error("❌ 空间结果可视化页面不可用")
    elif page == "基因富集分析":
        if 'enrichment' in ui_modules:
            ui_modules['enrichment'].show()
        else:
            st.error("❌ 基因富集分析页面不可用")
    elif page == "结果导出":
        if 'result_export' in ui_modules:
            ui_modules['result_export'].show()
        else:
            st.error("❌ 结果导出页面不可用")
    elif page == "帮助文档":
        if 'help' in ui_modules:
            ui_modules['help'].show()
        else:
            st.error("❌ 帮助文档页面不可用")

except Exception as e:
    st.error(f"❌ 应用程序启动错误: {e}")
    st.code(traceback.format_exc())
