import streamlit as st
import yaml
import os
import tempfile
from utils import config_utils, exception_utils
from core import qc_filter
from ui.components.param_editor import ParameterEditor
from core.config.param_manager import get_param_manager

# 向后兼容开关 - True使用新组件，False使用原手写UI
USE_NEW_PARAM_EDITOR = True


def render_param_section_with_default_toggle(section: str, section_name: str, expanded: bool = True):
    """
    渲染带"使用默认/自定义"切换的参数区块
    每步分析显示"使用默认"和"自定义"选项
    默认参数直接显示推荐值，用户无需修改可直接下一步
    需要自定义时点击展开详细面板
    """
    pm = get_param_manager()
    section_collapsed_key = f"section_collapsed_{section}"
    
    # 获取session_state中的折叠状态
    is_customized = not st.session_state.get(section_collapsed_key, False)
    
    with st.expander(f"步骤{section}：{section_name}", expanded=True):
        # 选择模式：使用默认 / 自定义
        col1, col2 = st.columns([1, 4])
        
        with col1:
            use_default = not is_customized
            mode = st.radio(
                "参数模式",
                ["使用默认", "自定义"],
                index=0 if use_default else 1,
                key=f"mode_{section}",
                horizontal=True
            )
        
        with col2:
            if mode == "使用默认":
                st.session_state[section_collapsed_key] = True
            else:
                st.session_state[section_collapsed_key] = False
        
        st.divider()
        
        # 渲染参数
        if st.session_state.get(section_collapsed_key, True):
            # 使用默认模式 - 显示推荐值，不可编辑
            _render_default_view(section, pm)
        else:
            # 自定义模式 - 展开详细面板
            _render_custom_view(section, pm)
        
        return st.session_state.get(f"config_{section}", {})


def _render_default_view(section: str, pm):
    """渲染默认模式：显示推荐值，不可编辑"""
    st.info(f"📋 使用推荐参数配置（可直接进入下一步）")
    
    # 获取该section的默认参数
    section_schema = {
        "1": {"key": "qc", "name": "质控与过滤", "params": ["qc.gene_filter.min_cells", "qc.cell_filter.min_genes", "qc.cell_filter.max_genes", "qc.cell_filter.min_umi", "qc.cell_filter.max_umi", "qc.mitochondrial.apply", "qc.ribosomal.apply"]},
        "2": {"key": "normalization", "name": "归一化与高变基因筛选", "params": ["normalization.method", "normalization.target_sum", "normalization.hvg.apply", "normalization.scaling.apply"]},
        "3": {"key": "dimension_reduction", "name": "降维分析", "params": ["dimension_reduction.pca.n_comps", "dimension_reduction.umap.apply", "dimension_reduction.tsne.apply"]},
        "4": {"key": "clustering", "name": "细胞聚类分析", "params": ["clustering.n_pcs", "clustering.n_neighbors", "clustering.resolution"]},
        "5": {"key": "differential", "name": "差异基因分析", "params": ["differential.apply"]},
    }
    
    section_info = section_info = section_schema.get(str(section), {})
    params = section_info.get("params", [])
    
    # 显示默认参数值
    if params:
        with st.container():
            cols = st.columns(2)
            for i, param_path in enumerate(params):
                col = cols[i % 2]
                with col:
                    value = pm.get(param_path)
                    param_name = param_path.split(".")[-1]
                    st.metric(label=param_name, value=value)
    
    # 保存默认配置到session_state
    config = st.session_state.get('pipeline_config', {})
    default_section = section_info.get("key", section)
    if default_section in config:
        st.session_state[f"config_{section}"] = config[default_section]
    else:
        st.session_state[f"config_{section}"] = {}


def _render_custom_view(section: str, pm):
    """渲染自定义模式：可编辑参数"""
    # 导入schema定义
    from core.config.parameter_schema import PARAMETER_SCHEMAS
    
    # 根据步骤选择对应的schema
    section_map = {
        "1": "qc",
        "2": "normalization", 
        "3": "dimension_reduction",
        "4": "clustering",
        "5": "differential",
    }
    
    schema_key = section_map.get(str(section), section)
    section_schema = PARAMETER_SCHEMAS.get(schema_key, {})
    
    if not section_schema:
        st.warning(f"未找到 {schema_key} 的参数定义")
        return {}
    
    results = {}
    children = section_schema.get('children', {})
    
    # 渲染所有参数
    def render_params(schema_dict, prefix=""):
        for key, info in schema_dict.items():
            if 'children' in info:
                # 分组
                with st.expander(info.get('display_name', key), expanded=True):
                    render_params(info['children'], f"{prefix}{key}.")
            else:
                # 单个参数
                path = f"{prefix}{key}"
                param_type = info.get('type', 'str')
                display_name = info.get('display_name', path.split('.')[-1])
                help_text = info.get('description', '')
                default_val = pm.get(path, info.get('default'))
                
                # 根据类型渲染不同输入控件
                current_val = st.session_state.get('pipeline_config', {})
                # 嵌套获取值
                keys = path.split('.')
                val = current_val
                for k in keys:
                    if isinstance(val, dict):
                        val = val.get(k)
                    else:
                        val = default_val
                        break
                
                if param_type == 'bool':
                    val = st.checkbox(
                        display_name,
                        value=val if val is not None else default_val,
                        help=help_text,
                        key=f"param_{path}"
                    )
                elif param_type == 'int':
                    min_v = info.get('min')
                    max_v = info.get('max')
                    kwargs = {"value": val if val is not None else default_val, "step": 1, "key": f"param_{path}"}
                    if min_v is not None: kwargs["min_value"] = min_v
                    if max_v is not None: kwargs["max_value"] = max_v
                    val = st.number_input(display_name, help=help_text, **kwargs)
                    val = int(val)
                elif param_type == 'float':
                    min_v = info.get('min')
                    max_v = info.get('max')
                    kwargs = {"value": float(val if val is not None else default_val), "step": 0.1, "key": f"param_{path}"}
                    if min_v is not None: kwargs["min_value"] = float(min_v)
                    if max_v is not None: kwargs["max_value"] = float(max_v)
                    val = st.number_input(display_name, help=help_text, **kwargs)
                    val = float(val)
                elif param_type == 'select':
                    options = info.get('options', [])
                    index = 0
                    current = val if val is not None else default_val
                    if current in options:
                        index = options.index(current)
                    val = st.selectbox(display_name, options=options, index=index, help=help_text, key=f"param_{path}")
                elif param_type == 'multiselect':
                    options = info.get('options', [])
                    val = st.multiselect(display_name, options=options, default=val if val else default_val, help=help_text, key=f"param_{path}")
                else:
                    val = st.text_input(display_name, value=str(val if val is not None else default_val), help=help_text, key=f"param_{path}")
                
                results[path] = val
    
    render_params(children)
    st.session_state[f"config_{section}"] = results
    
    # 添加预览质控结果按钮（仅QC步骤）
    if section == "1" and st.button("🔍 预览质控结果", key="preview_qc"):
        try:
            _preview_qc_results()
        except Exception as e:
            st.error(f"预览失败: {exception_utils.get_user_friendly_error(e)}")
    
    return results


def _preview_qc_results():
    """预览质控结果"""
    config = st.session_state.get('pipeline_config', {})
    adata = st.session_state.anndata_obj.copy()
    
    # 计算质控指标
    adata = qc_filter.calculate_qc_metrics(adata)
    adata = qc_filter.calculate_mitochondrial_percent(adata, config.get('qc', {}).get('mitochondrial', {}).get('prefix', 'MT-'))
    adata = qc_filter.calculate_ribosomal_percent(adata, config.get('qc', {}).get('ribosomal', {}).get('prefix', 'RP[SL]'))
    
    pre_qc_cells = adata.n_obs
    pre_qc_genes = adata.n_vars
    
    # 执行过滤
    if config.get('qc', {}).get('gene_filter', {}).get('apply', True):
        min_cells = config.get('qc', {}).get('gene_filter', {}).get('min_cells', 3)
        adata = qc_filter.filter_genes(adata, min_cells)
    
    qc_cell_filter = config.get('qc', {}).get('cell_filter', {})
    adata = qc_filter.filter_cells(
        adata,
        min_genes=qc_cell_filter.get('min_genes', 200),
        max_genes=qc_cell_filter.get('max_genes', 6000),
        min_umi=qc_cell_filter.get('min_umi', 500),
        max_umi=qc_cell_filter.get('max_umi', 20000)
    )
    
    if config.get('qc', {}).get('mitochondrial', {}).get('apply', True):
        max_mt = config.get('qc', {}).get('mitochondrial', {}).get('max_percent', 20)
        adata = qc_filter.filter_mitochondrial_cells(adata, max_mt)
    
    if config.get('qc', {}).get('ribosomal', {}).get('apply', False):
        max_ribo = config.get('qc', {}).get('ribosomal', {}).get('max_percent', 50)
        adata = qc_filter.filter_ribosomal_cells(adata, max_ribo)
    
    post_qc_cells = adata.n_obs
    post_qc_genes = adata.n_vars
    
    st.markdown("### 质控结果预览")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("质控前细胞数", pre_qc_cells)
    with col2:
        st.metric("质控前基因数", pre_qc_genes)
    with col3:
        st.metric("质控后细胞数", post_qc_cells, delta=post_qc_cells - pre_qc_cells)
    with col4:
        st.metric("质控后基因数", post_qc_genes, delta=post_qc_genes - pre_qc_genes)


# ============================================================================
# 旧的参数配置方式 - 向后兼容
# ============================================================================

def _render_old_qc_section(config):
    """旧版QC参数配置 - 向后兼容"""
    st.subheader("质控与过滤参数")
    
    # 基因过滤
    st.markdown("#### 基因过滤")
    gene_filter_apply = st.checkbox("过滤在少于3个细胞中表达的基因", value=config['qc']['gene_filter']['apply'])
    if gene_filter_apply:
        min_cells = st.number_input("最小细胞数", min_value=1, value=config['qc']['gene_filter']['min_cells'])
        config['qc']['gene_filter']['min_cells'] = min_cells
    config['qc']['gene_filter']['apply'] = gene_filter_apply
    
    # 细胞过滤-基因数
    st.markdown("#### 细胞过滤-基因数")
    min_genes = st.slider("每个细胞最少检测到的基因数", min_value=10, max_value=1000, step=10, value=config['qc']['cell_filter']['min_genes'])
    max_genes = st.slider("每个细胞最多检测到的基因数", min_value=1000, max_value=20000, step=100, value=config['qc']['cell_filter']['max_genes'])
    config['qc']['cell_filter']['min_genes'] = min_genes
    config['qc']['cell_filter']['max_genes'] = max_genes
    
    # 细胞过滤-UMI数
    st.markdown("#### 细胞过滤-UMI数")
    min_umi = st.slider("每个细胞最少UMI总数", min_value=100, max_value=5000, step=100, value=config['qc']['cell_filter']['min_umi'])
    max_umi = st.slider("每个细胞最多UMI总数", min_value=5000, max_value=100000, step=1000, value=config['qc']['cell_filter']['max_umi'])
    config['qc']['cell_filter']['min_umi'] = min_umi
    config['qc']['cell_filter']['max_umi'] = max_umi
    
    # 细胞过滤-线粒体基因比例
    st.markdown("#### 细胞过滤-线粒体基因比例")
    mito_apply = st.checkbox("过滤线粒体基因比例过高的细胞", value=config['qc']['mitochondrial']['apply'])
    if mito_apply:
        mito_prefix = st.text_input("线粒体基因前缀", value=config['qc']['mitochondrial']['prefix'])
        max_mt_percent = st.slider("最大线粒体基因比例（%）", min_value=5, max_value=50, step=1, value=config['qc']['mitochondrial']['max_percent'])
        config['qc']['mitochondrial']['prefix'] = mito_prefix
        config['qc']['mitochondrial']['max_percent'] = max_mt_percent
    config['qc']['mitochondrial']['apply'] = mito_apply
    
    # 细胞过滤-核糖体基因比例
    st.markdown("#### 细胞过滤-核糖体基因比例")
    ribo_apply = st.checkbox("过滤核糖体基因比例过高的细胞", value=config['qc']['ribosomal']['apply'])
    if ribo_apply:
        ribo_prefix = st.text_input("核糖体基因前缀", value=config['qc']['ribosomal']['prefix'])
        max_ribo_percent = st.slider("最大核糖体基因比例（%）", min_value=10, max_value=100, step=1, value=config['qc']['ribosomal']['max_percent'])
        config['qc']['ribosomal']['prefix'] = ribo_prefix
        config['qc']['ribosomal']['max_percent'] = max_ribo_percent
    config['qc']['ribosomal']['apply'] = ribo_apply
    
    # 预览质控结果按钮
    if st.button("预览质控结果"):
        try:
            _preview_qc_results_old(config)
        except Exception as e:
            st.error(f"预览质控结果失败: {exception_utils.get_user_friendly_error(e)}")
    
    return config


def _preview_qc_results_old(config):
    """旧版预览质控结果"""
    adata = st.session_state.anndata_obj.copy()
    
    # 计算质控指标
    adata = qc_filter.calculate_qc_metrics(adata)
    adata = qc_filter.calculate_mitochondrial_percent(adata, config['qc']['mitochondrial']['prefix'])
    adata = qc_filter.calculate_ribosomal_percent(adata, config['qc']['ribosomal']['prefix'])
    
    pre_qc_cells = adata.n_obs
    pre_qc_genes = adata.n_vars
    
    # 执行过滤
    if config['qc']['gene_filter']['apply']:
        adata = qc_filter.filter_genes(adata, config['qc']['gene_filter']['min_cells'])
    
    adata = qc_filter.filter_cells(
        adata,
        min_genes=config['qc']['cell_filter']['min_genes'],
        max_genes=config['qc']['cell_filter']['max_genes'],
        min_umi=config['qc']['cell_filter']['min_umi'],
        max_umi=config['qc']['cell_filter']['max_umi']
    )
    
    if config['qc']['mitochondrial']['apply']:
        adata = qc_filter.filter_mitochondrial_cells(adata, config['qc']['mitochondrial']['max_percent'])
    
    if config['qc']['ribosomal']['apply']:
        adata = qc_filter.filter_ribosomal_cells(adata, config['qc']['ribosomal']['max_percent'])
    
    post_qc_cells = adata.n_obs
    post_qc_genes = adata.n_vars
    
    st.markdown("### 质控结果预览")
    st.info(f"质控前细胞数: {pre_qc_cells}, 基因数: {pre_qc_genes}")
    st.info(f"质控后细胞数: {post_qc_cells}, 基因数: {post_qc_genes}")
    st.info(f"过滤掉的细胞数: {pre_qc_cells - post_qc_cells}")
    st.info(f"过滤掉的基因数: {pre_qc_genes - post_qc_genes}")


def _render_old_normalization_section(config):
    """旧版归一化参数配置"""
    st.subheader("归一化与高变基因筛选参数")
    
    st.markdown("#### 归一化设置")
    norm_method = st.selectbox(
        "归一化方法",
        ["Scanpy标准归一化（总计数归一化+对数转换）", "CPM归一化"],
        index=0 if config['normalization']['method'] == 'scanpy' else 1
    )
    config['normalization']['method'] = 'scanpy' if norm_method.startswith('Scanpy') else 'cpm'
    
    if config['normalization']['method'] == 'scanpy':
        target_sum = st.number_input("目标总计数", min_value=1000, value=int(config['normalization']['target_sum']))
        config['normalization']['target_sum'] = target_sum
    
    st.markdown("#### 高变基因筛选")
    hvg_apply = st.checkbox("筛选高变基因", value=config['normalization']['hvg']['apply'])
    if hvg_apply:
        hvg_method = st.selectbox(
            "筛选方法",
            ["Seurat_v3", "CellRanger", "Seurat"],
            index=["Seurat_v3", "CellRanger", "Seurat"].index(config['normalization']['hvg']['method'])
        )
        n_top_genes = st.slider("高变基因数量", min_value=500, max_value=5000, step=100, value=config['normalization']['hvg']['n_top_genes'])
        config['normalization']['hvg']['method'] = hvg_method
        config['normalization']['hvg']['n_top_genes'] = n_top_genes
    config['normalization']['hvg']['apply'] = hvg_apply
    
    st.markdown("#### 数据标准化")
    scaling_apply = st.checkbox("对数据进行z-score标准化", value=config['normalization']['scaling']['apply'])
    if scaling_apply:
        max_value = st.number_input("标准化后缩放到最大值", min_value=1, value=int(config['normalization']['scaling']['max_value']))
        config['normalization']['scaling']['max_value'] = max_value
    config['normalization']['scaling']['apply'] = scaling_apply
    
    return config


def _render_old_dimred_section(config):
    """旧版降维参数配置"""
    st.subheader("降维分析参数")
    
    st.markdown("#### PCA分析")
    n_comps = st.slider("PCA主成分数量", min_value=10, max_value=100, step=5, value=config['dimension_reduction']['pca']['n_comps'])
    use_hvg = st.checkbox("使用高变基因进行PCA分析", value=config['dimension_reduction']['pca']['use_hvg'])
    config['dimension_reduction']['pca']['n_comps'] = n_comps
    config['dimension_reduction']['pca']['use_hvg'] = use_hvg
    
    st.markdown("#### UMAP降维")
    umap_apply = st.checkbox("执行UMAP降维", value=config['dimension_reduction']['umap']['apply'])
    if umap_apply:
        n_neighbors = st.slider("UMAP邻居数", min_value=5, max_value=50, step=1, value=config['dimension_reduction']['umap']['n_neighbors'])
        min_dist = st.slider("UMAP最小距离", min_value=0.1, max_value=1.0, step=0.1, value=config['dimension_reduction']['umap']['min_dist'])
        config['dimension_reduction']['umap']['n_neighbors'] = n_neighbors
        config['dimension_reduction']['umap']['min_dist'] = min_dist
    config['dimension_reduction']['umap']['apply'] = umap_apply
    
    st.markdown("#### tSNE降维")
    tsne_apply = st.checkbox("执行tSNE降维", value=config['dimension_reduction']['tsne']['apply'])
    if tsne_apply:
        perplexity = st.slider("tSNE困惑度", min_value=5, max_value=100, step=5, value=config['dimension_reduction']['tsne']['perplexity'])
        config['dimension_reduction']['tsne']['perplexity'] = perplexity
    config['dimension_reduction']['tsne']['apply'] = tsne_apply
    
    return config


def _render_old_clustering_section(config):
    """旧版聚类参数配置"""
    st.subheader("细胞聚类分析参数")
    
    st.markdown("#### 邻居图构建")
    n_pcs = st.slider("构建邻居图使用的PCA主成分数量", min_value=10, max_value=50, step=5, value=config['clustering']['n_pcs'])
    n_neighbors = st.slider("邻居数量", min_value=5, max_value=50, step=1, value=config['clustering']['n_neighbors'])
    config['clustering']['n_pcs'] = n_pcs
    config['clustering']['n_neighbors'] = n_neighbors
    
    st.markdown("#### 聚类算法")
    resolution = st.slider("聚类分辨率", min_value=0.1, max_value=2.0, step=0.1, value=config['clustering']['resolution'])
    config['clustering']['method'] = 'leiden'
    config['clustering']['resolution'] = resolution
    st.info("使用Leiden聚类算法。分辨率越大，聚类数量越多；分辨率越小，聚类数量越少")
    
    return config


def _render_old_differential_section(config):
    """旧版差异分析参数配置"""
    st.subheader("差异基因分析参数")
    
    diff_apply = st.checkbox("执行聚类差异基因分析", value=config['differential']['apply'])
    if diff_apply:
        diff_method = st.selectbox(
            "差异检验方法",
            ["Wilcoxon秩和检验", "t检验", "logistic回归"],
            index=["Wilcoxon秩和检验", "t检验", "logistic回归"].index(config['differential']['method']) if config['differential']['method'] in ["wilcoxon", "t-test", "logreg"] else 0
        )
        p_adjust_cutoff = st.slider("调整后p值最大值（p.adjust）", min_value=0.001, max_value=0.1, step=0.001, value=config['differential']['p_adjust_cutoff'])
        log2fc_min = st.slider("最小log2倍变化（log2FC）", min_value=0.1, max_value=2.0, step=0.05, value=config['differential']['log2fc_min'])
        min_pct = st.checkbox("仅保留在至少25%的细胞中表达的基因", value=config['differential']['min_pct'] >= 0.25)
        
        config['differential']['method'] = 'wilcoxon' if diff_method == 'Wilcoxon秩和检验' else 't-test' if diff_method == 't检验' else 'logreg'
        config['differential']['p_adjust_cutoff'] = p_adjust_cutoff
        config['differential']['log2fc_min'] = log2fc_min
        config['differential']['min_pct'] = 0.25 if min_pct else 0.0
    config['differential']['apply'] = diff_apply
    
    return config


# ============================================================================
# 主页面函数
# ============================================================================

def show():
    """
    分析流程配置页面 - 支持新旧两种参数配置方式
    """
    # 页面前置校验
    if not st.session_state.get('is_data_loaded', False):
        st.warning("请先导入数据")
        return
    
    st.title("🔧 分析流程配置")
    
    # 全局功能按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("一键恢复所有默认参数"):
            default_config = config_utils.load_config()
            st.session_state.pipeline_config = default_config.copy()
            # 重置所有折叠状态
            for key in st.session_state.keys():
                if key.startswith("section_collapsed_"):
                    st.session_state[key] = True
            st.success("已恢复默认参数")
            st.rerun()
    
    with col2:
        if st.button("保存参数配置"):
            config = st.session_state.pipeline_config
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
                yaml.dump(config, tmp, default_flow_style=False, allow_unicode=True)
                tmp_path = tmp.name
            
            with open(tmp_path, 'rb') as f:
                st.download_button(
                    label="下载配置文件",
                    data=f,
                    file_name="pipeline_config.yaml",
                    mime="application/yaml"
                )
            os.unlink(tmp_path)
    
    with col3:
        uploaded_config = st.file_uploader("加载参数配置", type=["yaml", "yml"])
        if uploaded_config is not None:
            try:
                config = yaml.safe_load(uploaded_config)
                st.session_state.pipeline_config = config
                st.success("已加载配置文件")
                st.rerun()
            except Exception as e:
                st.error(f"加载配置文件失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 获取当前配置
    config = st.session_state.pipeline_config
    
    # 根据开关选择渲染方式
    if USE_NEW_PARAM_EDITOR:
        # 新版参数配置 - 使用 ParameterEditor
        _render_new_pipeline(config)
    else:
        # 旧版参数配置 - 保留原有手写UI
        _render_old_pipeline(config)


def _render_new_pipeline(config):
    """新版参数配置流程"""
    # 初始化section状态
    if 'section_collapsed_1' not in st.session_state:
        st.session_state.section_collapsed_1 = True
    if 'section_collapsed_2' not in st.session_state:
        st.session_state.section_collapsed_2 = True
    if 'section_collapsed_3' not in st.session_state:
        st.session_state.section_collapsed_3 = True
    if 'section_collapsed_4' not in st.session_state:
        st.session_state.section_collapsed_4 = True
    if 'section_collapsed_5' not in st.session_state:
        st.session_state.section_collapsed_5 = True
    
    # 步骤1：质控与过滤
    render_param_section_with_default_toggle("1", "质控与过滤")
    
    # 步骤2：归一化与高变基因筛选
    render_param_section_with_default_toggle("2", "归一化与高变基因筛选")
    
    # 步骤3：降维分析
    render_param_section_with_default_toggle("3", "降维分析")
    
    # 步骤4：细胞聚类分析
    render_param_section_with_default_toggle("4", "细胞聚类分析")
    
    # 步骤5：差异基因分析
    render_param_section_with_default_toggle("5", "差异基因分析")
    
    # 页面底部功能
    st.markdown("---")
    _render_config_overview()


def _render_old_pipeline(config):
    """旧版参数配置流程 - 向后兼容"""
    # 步骤1：质控与过滤
    with st.expander("步骤1：质控与过滤", expanded=True):
        config = _render_old_qc_section(config)
    
    # 步骤2：归一化与高变基因筛选
    with st.expander("步骤2：归一化与高变基因筛选"):
        config = _render_old_normalization_section(config)
    
    # 步骤3：降维分析
    with st.expander("步骤3：降维分析"):
        config = _render_old_dimred_section(config)
    
    # 步骤4：细胞聚类分析
    with st.expander("步骤4：细胞聚类分析"):
        config = _render_old_clustering_section(config)
    
    # 步骤5：差异基因分析
    with st.expander("步骤5：差异基因分析"):
        config = _render_old_differential_section(config)
    
    # 更新session_state
    st.session_state.pipeline_config = config
    
    # 页面底部功能
    st.markdown("---")
    _render_config_overview()


def _render_config_overview():
    """显示参数总览"""
    st.subheader("参数总览")
    config = st.session_state.pipeline_config
    st.json(config)
    
    # 保存配置并执行分析按钮
    if st.button("💾 保存配置并执行分析", type="primary"):
        try:
            # 跳转到结果可视化页面
            st.session_state.page = "结果可视化"
            
            # 执行分析
            from core import analysis_pipeline
            
            with st.spinner("正在执行分析..."):
                adata, result = analysis_pipeline.run_single_cell_pipeline(
                    st.session_state.anndata_obj,
                    config
                )
                
                st.session_state.anndata_obj = adata
                st.session_state.analysis_result = result
                st.session_state.is_analysis_done = True
                
                st.success("分析完成！")
                st.rerun()
        except Exception as e:
            st.error(f"执行分析失败: {exception_utils.get_user_friendly_error(e)}")