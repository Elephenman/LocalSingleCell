import streamlit as st
import json
from typing import Dict, Any
import logging

from core.ai_parser import AIParser
from utils.exception_utils import handle_exception
from utils.logger_utils import init_logger

logger = init_logger(__name__)


def show():
    """
    AI自然语言分析页面
    """
    st.title("🤖 AI自然语言分析")
    
    # 页面前置校验
    if not st.session_state.get('is_data_loaded', False):
        st.warning("⚠️ 请先导入数据后再使用AI分析功能")
        st.info("请前往「数据导入」页面上传您的单细胞或空间转录组数据")
        
        # 快速跳转按钮
        if st.button("📁 前往数据导入页面"):
            st.session_state.page = "数据导入"
            st.rerun()
        return
    
    try:
        # 初始化AI解析器
        config = st.session_state.get('global_config', {})
        ai_parser = AIParser(config)
        
        # 检测数据类型
        data_type = 'single_cell'
        if st.session_state.get('is_spatial_data', False):
            data_type = 'spatial'
        
        st.markdown("---")
        
        # 步骤1：输入自然语言需求
        st.subheader("📝 输入您的分析需求")
        
        # 示例需求按钮
        st.markdown("### 💡 快速选择示例需求")
        example_col1, example_col2, example_col3 = st.columns(3)
        
        with example_col1:
            if st.button("🎯 基础单细胞分析", use_container_width=True):
                st.session_state.ai_draft = "帮我做一个基础的单细胞分析，用默认参数，包括质控、归一化、PCA、UMAP、Leiden聚类（分辨率0.5）、差异基因分析和GO富集分析"
        
        with example_col2:
            if st.button("🔍 严格质控分析", use_container_width=True):
                st.session_state.ai_draft = "过滤线粒体比例超过10%的细胞，最少300个基因，最多5000个基因，用Leiden算法，分辨率0.8聚类，找每个聚类的标记基因，做GO和KEGG富集分析"
        
        with example_col3:
            if data_type == 'spatial':
                if st.button("🗺️ 空间转录组分析", use_container_width=True):
                    st.session_state.ai_draft = "空间转录组分析，找空间可变基因，做空间聚类，生成空间基因表达图和UMAP图"
            else:
                if st.button("📊 完整分析流程", use_container_width=True):
                    st.session_state.ai_draft = "完整分析流程，过滤线粒体比例超过15%的细胞，最少200个基因，用分辨率0.6聚类，找差异基因，做GO、KEGG和Reactome富集分析，生成UMAP图、火山图、气泡图和热图"
        
        # 更多示例（可折叠）
        with st.expander("📚 更多示例需求"):
            st.markdown("#### 质控相关")
            more_ex1, more_ex2 = st.columns(2)
            with more_ex1:
                if st.button("• 宽松质控标准"):
                    st.session_state.ai_draft = "宽松质控，线粒体比例可以到30%，最少100个基因"
            with more_ex2:
                if st.button("• 过滤核糖体基因"):
                    st.session_state.ai_draft = "过滤核糖体基因比例超过40%的细胞，线粒体比例不超过15%"
            
            st.markdown("#### 聚类相关")
            more_ex3, more_ex4 = st.columns(2)
            with more_ex3:
                if st.button("• Louvain聚类"):
                    st.session_state.ai_draft = "用Louvain算法聚类，分辨率1.0"
            with more_ex4:
                if st.button("• 高分辨率聚类"):
                    st.session_state.ai_draft = "高分辨率聚类，分辨率1.5，找更细的细胞亚群"
            
            st.markdown("#### 富集分析相关")
            more_ex5, more_ex6 = st.columns(2)
            with more_ex5:
                if st.button("• 小鼠富集分析"):
                    st.session_state.ai_draft = "做小鼠的GO和KEGG富集分析"
            with more_ex6:
                if st.button("• 仅KEGG富集"):
                    st.session_state.ai_draft = "只做KEGG富集分析"
        
        st.markdown("---")
        
        # 自定义输入区域
        st.markdown("### ✏️ 自定义需求描述")
        
        # 获取默认值
        default_value = ""
        if 'example_requirement' in st.session_state:
            default_value = st.session_state.example_requirement
            del st.session_state.example_requirement
        elif 'ai_draft' in st.session_state:
            default_value = st.session_state.ai_draft
            del st.session_state.ai_draft
        
        user_input = st.text_area(
            "请用自然语言描述您的分析需求（可以直接修改上面选择的示例）",
            value=default_value,
            placeholder="例如：帮我分析这个数据，过滤线粒体比例超过20%的细胞，分辨率0.5聚类，找标记基因，做GO和KEGG富集分析...",
            height=120
        )
        
        st.markdown("---")
        
        # 步骤2：解析需求
        col_parse1, col_parse2 = st.columns([1, 1])
        
        with col_parse1:
            parse_button = st.button("🔍 解析需求", type="primary", disabled=not user_input, use_container_width=True)
        
        with col_parse2:
            if st.button("🗑️ 清空重新输入", type="secondary", use_container_width=True):
                st.session_state.pop('ai_parsed', None)
                st.session_state.pop('ai_parsed_config', None)
                st.session_state.pop('ai_parsed_viz', None)
                st.session_state.pop('ai_user_input', None)
                st.rerun()
        
        if parse_button:
            with st.spinner("🤖 AI正在解析您的需求，请稍候..."):
                try:
                    # 使用内置解析器解析需求
                    pipeline_config, viz_config = ai_parser.parse_requirement(user_input, data_type)
                    
                    # 验证参数
                    is_valid, validation_msg = ai_parser.validate_parameters(pipeline_config)
                    
                    if not is_valid:
                        st.error(f"❌ 参数验证失败: {validation_msg}")
                        logger.warning(f"AI参数验证失败: {validation_msg}")
                        st.info("💡 请尝试用更明确的语言描述您的需求，或使用示例需求进行修改")
                        return
                    
                    # 存储解析结果到session_state
                    st.session_state['ai_parsed_config'] = pipeline_config
                    st.session_state['ai_parsed_viz'] = viz_config
                    st.session_state['ai_user_input'] = user_input
                    st.session_state['ai_parsed'] = True
                    
                    st.success("✅ 需求解析成功！请查看下方的参数预览")
                    logger.info("AI需求解析成功")
                    st.balloons()
                    
                except Exception as e:
                    handle_exception(e, "解析需求时出错")
        
        st.markdown("---")
        
        # 步骤3：显示解析结果预览
        if st.session_state.get('ai_parsed', False):
            st.subheader("📋 解析结果预览")
            
            # 用更友好的方式显示参数
            with st.expander("🔬 质控参数", expanded=True):
                qc_config = st.session_state['ai_parsed_config'].get('qc', {})
                qc_col1, qc_col2, qc_col3 = st.columns(3)
                
                with qc_col1:
                    st.metric("过滤线粒体", "启用" if qc_config.get('filter_mito', True) else "禁用")
                    st.metric("最大线粒体比例", f"{qc_config.get('max_mito_ratio', 20)}%")
                
                with qc_col2:
                    st.metric("最小基因数", qc_config.get('min_genes', 200))
                    st.metric("最大基因数", qc_config.get('max_genes', 6000))
                
                with qc_col3:
                    st.metric("最小UMI数", qc_config.get('min_umi', 500))
                    st.metric("最大UMI数", qc_config.get('max_umi', 20000))
            
            with st.expander("🎯 聚类参数", expanded=True):
                clustering_config = st.session_state['ai_parsed_config'].get('clustering', {})
                clust_col1, clust_col2 = st.columns(2)
                
                with clust_col1:
                    st.metric("聚类算法", clustering_config.get('algorithm', 'leiden').upper())
                    st.metric("使用PCA主成分数", clustering_config.get('n_pcs', 30))
                
                with clust_col2:
                    st.metric("聚类分辨率", clustering_config.get('resolution', 0.5))
                    st.metric("邻居数量", clustering_config.get('n_neighbors', 15))
            
            with st.expander("📊 差异表达参数", expanded=False):
                de_config = st.session_state['ai_parsed_config'].get('differential_expression', {})
                de_col1, de_col2 = st.columns(2)
                
                with de_col1:
                    st.metric("差异分析", "启用" if de_config.get('run_de', True) else "禁用")
                    st.metric("检验方法", de_config.get('method', 'wilcoxon').upper())
                
                with de_col2:
                    st.metric("p值阈值", de_config.get('p_adjust_cutoff', 0.05))
                    st.metric("log2FC阈值", de_config.get('log2fc_cutoff', 0.25))
            
            with st.expander("🔬 富集分析参数", expanded=False):
                enrichment_config = st.session_state['ai_parsed_config'].get('enrichment', {})
                if enrichment_config:
                    enrich_col1, enrich_col2 = st.columns(2)
                    
                    with enrich_col1:
                        st.metric("富集分析", "启用" if enrichment_config.get('run_enrichment', False) else "禁用")
                        st.metric("物种", enrichment_config.get('species', 'human'))
                    
                    with enrich_col2:
                        databases = enrichment_config.get('databases', [])
                        st.write("选择的数据库:")
                        for db in databases:
                            st.write(f"  • {db.upper()}")
                else:
                    st.info("未配置富集分析")
            
            with st.expander("🎨 可视化配置", expanded=False):
                viz_config = st.session_state['ai_parsed_viz']
                st.json(viz_config, expanded=True)
            
            st.markdown("---")
            
            # 步骤4：确认并执行
            st.subheader("✅ 确认并执行")
            
            col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 1])
            
            with col_confirm1:
                if st.button("✏️ 手动调整参数", type="secondary", use_container_width=True):
                    # 跳转到参数配置页面
                    st.session_state['pipeline_config'] = st.session_state['ai_parsed_config']
                    st.session_state.page = "空间分析流程配置" if data_type == 'spatial' else "分析流程配置"
                    st.rerun()
            
            with col_confirm2:
                if st.button("🔄 重新解析", type="secondary", use_container_width=True):
                    st.session_state.pop('ai_parsed', None)
                    st.session_state.pop('ai_parsed_config', None)
                    st.session_state.pop('ai_parsed_viz', None)
                    st.rerun()
            
            with col_confirm3:
                if st.button("🚀 一键执行分析", type="primary", use_container_width=True):
                    execute_ai_analysis(ai_parser, data_type)
        
        st.markdown("---")
        
        # 帮助信息
        with st.expander("💡 使用提示和技巧", expanded=False):
            st.markdown("""
            ### AI分析功能说明
            
            本功能通过内置的规则解析器将您的自然语言需求转换为分析参数。所有解析都在本地完成，无数据上传到云端。
            
            ### 📝 描述需求的技巧
            
            **质控过滤：**
            - ✅ "过滤线粒体比例超过15%的细胞"
            - ✅ "最少基因数设为500，最多6000"
            - ✅ "同时过滤线粒体和核糖体基因"
            
            **聚类分析：**
            - ✅ "使用Leiden算法，分辨率0.8"
            - ✅ "用Louvain聚类，分辨率1.0"
            - ✅ "高分辨率聚类，找更多细胞亚群"
            
            **降维可视化：**
            - ✅ "做UMAP和tSNE降维"
            - ✅ "PCA主成分数设为30"
            
            **差异基因分析：**
            - ✅ "找每个聚类的标记基因"
            - ✅ "p值阈值设为0.01"
            - ✅ "log2FC至少1.5"
            
            **富集分析：**
            - ✅ "做GO和KEGG富集分析"
            - ✅ "做小鼠的富集分析"
            - ✅ "只做Reactome富集"
            
            **可视化：**
            - ✅ "生成UMAP图和火山图"
            - ✅ "出气泡图和热图"
            
            ### ⚠️ 注意事项
            
            - 如果需要更精细的参数控制，请点击「手动调整参数」跳转到参数配置页面
            - 解析完成后请仔细检查参数是否符合预期
            - 可以先使用示例需求，然后在输入框中进行修改
            - 如果解析结果不理想，尝试用更明确的语言重新描述
            """)
            
    except Exception as e:
        handle_exception(e, "AI分析页面加载失败")


def execute_ai_analysis(ai_parser: AIParser, data_type: str):
    """
    执行AI解析后的分析流程
    
    Args:
        ai_parser: AI解析器实例
        data_type: 数据类型 ('single_cell' 或 'spatial')
    """
    try:
        # 更新session_state中的配置
        st.session_state['pipeline_config'] = st.session_state['ai_parsed_config']
        
        st.success("✅ 参数已确认，正在启动分析流程...")
        logger.info("启动AI解析后的分析流程")
        
        # 立即执行分析
        from core.analysis_pipeline import run_single_cell_pipeline
        from core.spatial_pipeline import run_spatial_pipeline
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            if data_type == 'spatial' and st.session_state.get('is_spatial_data', False):
                # 执行空间转录组分析
                status_text.text("🚀 正在执行空间转录组分析...")
                result = run_spatial_pipeline(
                    st.session_state['anndata_obj'],
                    st.session_state['pipeline_config'],
                    progress_callback=lambda p, s: (progress_bar.progress(p), status_text.text(s))
                )
            else:
                # 执行单细胞分析
                status_text.text("🚀 正在执行单细胞转录组分析...")
                result = run_single_cell_pipeline(
                    st.session_state['anndata_obj'],
                    st.session_state['pipeline_config'],
                    progress_callback=lambda p, s: (progress_bar.progress(p), status_text.text(s))
                )
            
            # 保存结果
            st.session_state['anndata_obj'] = result['adata']
            st.session_state['analysis_result'] = result
            st.session_state['is_analysis_done'] = True
            
            progress_bar.progress(100)
            status_text.text("✅ 分析完成！")
            
            st.success("🎉 分析完成！正在跳转到可视化页面...")
            
            # 清除AI解析状态
            for key in ['ai_parsed', 'ai_parsed_config', 'ai_parsed_viz', 'ai_user_input']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # 跳转到可视化页面
            st.session_state.page = "空间结果可视化" if data_type == 'spatial' else "结果可视化"
            
            # 延迟跳转
            import time
            time.sleep(1.5)
            st.rerun()
            
        except Exception as e:
            progress_bar.progress(0)
            handle_exception(e, "执行分析流程时出错")
            
    except Exception as e:
        handle_exception(e, "执行AI分析时出错")
