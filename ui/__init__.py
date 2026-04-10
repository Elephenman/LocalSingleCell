"""
UI页面模块

提供Streamlit界面页面组件。
"""

# 页面展示函数
from .home_page import show as show_home
from .data_import_page import show as show_data_import
from .pipeline_config_page import show as show_pipeline_config
from .visualization_page import show as show_visualization
from .enrichment_page import show as show_enrichment
from .result_export_page import show as show_result_export
from .help_page import show as show_help
from .ai_analysis_page import show as show_ai_analysis
from .spatial_pipeline_config_page import show as show_spatial_pipeline_config
from .spatial_visualization_page import show as show_spatial_visualization

# 侧边栏
from .sidebar import sidebar

__all__ = [
    'show_home',
    'show_data_import',
    'show_pipeline_config',
    'show_visualization',
    'show_enrichment',
    'show_result_export',
    'show_help',
    'show_ai_analysis',
    'show_spatial_pipeline_config',
    'show_spatial_visualization',
    'sidebar',
]
