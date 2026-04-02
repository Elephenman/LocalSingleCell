import streamlit as st
import yaml
import os
import tempfile
from utils import config_utils, exception_utils
from core import qc_filter


def show():
    """
    分析流程配置页面
    """
    # 页面前置校验
    if not st.session_state.get('is_data_loaded', False):
        st.warning("请先导入数据")
        return
    
    st.title("分析流程配置")
    
    # 全局功能按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("一键恢复所有默认参数"):
            # 加载默认配置
            default_config = config_utils.load_config()
            st.session_state.pipeline_config = default_config.copy()
            st.success("已恢复默认参数")
            st.rerun()
    
    with col2:
        if st.button("保存参数配置"):
            # 保存配置为yaml文件
            config = st.session_state.pipeline_config
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
                yaml.dump(config, tmp, default_flow_style=False, allow_unicode=True)
                tmp_path = tmp.name
            
            # 提供下载
            with open(tmp_path, 'rb') as f:
                st.download_button(
                    label="下载配置文件",
                    data=f,
                    file_name="pipeline_config.yaml",
                    mime="application/yaml"
                )
            
            # 清理临时文件
            os.unlink(tmp_path)
    
    with col3:
        uploaded_config = st.file_uploader("加载参数配置", type=["yaml", "yml"])
        if uploaded_config is not None:
            try:
                # 读取上传的配置文件
                config = yaml.safe_load(uploaded_config)
                st.session_state.pipeline_config = config
                st.success("已加载配置文件")
                st.rerun()
            except Exception as e:
                st.error(f"加载配置文件失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 获取当前配置
    config = st.session_state.pipeline_config
    
    # 步骤1：质控与过滤
    with st.expander("步骤1：质控与过滤", expanded=True):
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
                # 复制AnnData对象进行临时计算
                adata = st.session_state.anndata_obj.copy()
                
                # 计算质控指标
                adata = qc_filter.calculate_qc_metrics(adata)
                adata = qc_filter.calculate_mitochondrial_percent(adata, config['qc']['mitochondrial']['prefix'])
                adata = qc_filter.calculate_ribosomal_percent(adata, config['qc']['ribosomal']['prefix'])
                
                # 记录质控前的细胞数和基因数
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
                
                # 记录质控后的细胞数和基因数
                post_qc_cells = adata.n_obs
                post_qc_genes = adata.n_vars
                
                # 显示结果
                st.markdown("### 质控结果预览")
                st.info(f"质控前细胞数: {pre_qc_cells}, 基因数: {pre_qc_genes}")
                st.info(f"质控后细胞数: {post_qc_cells}, 基因数: {post_qc_genes}")
                st.info(f"过滤掉的细胞数: {pre_qc_cells - post_qc_cells}")
                st.info(f"过滤掉的基因数: {pre_qc_genes - post_qc_genes}")
                
            except Exception as e:
                st.error(f"预览质控结果失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 步骤2：归一化与高变基因筛选
    with st.expander("步骤2：归一化与高变基因筛选"):
        st.subheader("归一化与高变基因筛选参数")
        
        # 归一化设置
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
        
        # 高变基因筛选
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
        
        # 数据标准化
        st.markdown("#### 数据标准化")
        scaling_apply = st.checkbox("对数据进行z-score标准化", value=config['normalization']['scaling']['apply'])
        if scaling_apply:
            max_value = st.number_input("标准化后缩放到最大值", min_value=1, value=int(config['normalization']['scaling']['max_value']))
            config['normalization']['scaling']['max_value'] = max_value
        config['normalization']['scaling']['apply'] = scaling_apply
    
    # 步骤3：降维分析
    with st.expander("步骤3：降维分析"):
        st.subheader("降维分析参数")
        
        # PCA分析
        st.markdown("#### PCA分析")
        n_comps = st.slider("PCA主成分数量", min_value=10, max_value=100, step=5, value=config['dimension_reduction']['pca']['n_comps'])
        use_hvg = st.checkbox("使用高变基因进行PCA分析", value=config['dimension_reduction']['pca']['use_hvg'])
        config['dimension_reduction']['pca']['n_comps'] = n_comps
        config['dimension_reduction']['pca']['use_hvg'] = use_hvg
        
        # UMAP降维
        st.markdown("#### UMAP降维")
        umap_apply = st.checkbox("执行UMAP降维", value=config['dimension_reduction']['umap']['apply'])
        if umap_apply:
            n_neighbors = st.slider("UMAP邻居数", min_value=5, max_value=50, step=1, value=config['dimension_reduction']['umap']['n_neighbors'])
            min_dist = st.slider("UMAP最小距离", min_value=0.1, max_value=1.0, step=0.1, value=config['dimension_reduction']['umap']['min_dist'])
            config['dimension_reduction']['umap']['n_neighbors'] = n_neighbors
            config['dimension_reduction']['umap']['min_dist'] = min_dist
        config['dimension_reduction']['umap']['apply'] = umap_apply
        
        # tSNE降维
        st.markdown("#### tSNE降维")
        tsne_apply = st.checkbox("执行tSNE降维", value=config['dimension_reduction']['tsne']['apply'])
        if tsne_apply:
            perplexity = st.slider("tSNE困惑度", min_value=5, max_value=100, step=5, value=config['dimension_reduction']['tsne']['perplexity'])
            config['dimension_reduction']['tsne']['perplexity'] = perplexity
        config['dimension_reduction']['tsne']['apply'] = tsne_apply
    
    # 步骤4：细胞聚类分析
    with st.expander("步骤4：细胞聚类分析"):
        st.subheader("细胞聚类分析参数")
        
        # 邻居图构建
        st.markdown("#### 邻居图构建")
        n_pcs = st.slider("构建邻居图使用的PCA主成分数量", min_value=10, max_value=50, step=5, value=config['clustering']['n_pcs'])
        n_neighbors = st.slider("邻居数量", min_value=5, max_value=50, step=1, value=config['clustering']['n_neighbors'])
        config['clustering']['n_pcs'] = n_pcs
        config['clustering']['n_neighbors'] = n_neighbors
        
        # 聚类算法
        st.markdown("#### 聚类算法")
        resolution = st.slider("聚类分辨率", min_value=0.1, max_value=2.0, step=0.1, value=config['clustering']['resolution'])
        config['clustering']['method'] = 'leiden'
        config['clustering']['resolution'] = resolution
        st.info("使用Leiden聚类算法。分辨率越大，聚类数量越多；分辨率越小，聚类数量越少")
    
    # 步骤5：差异基因分析
    with st.expander("步骤5：差异基因分析"):
        st.subheader("差异基因分析参数")
        
        # 执行差异基因分析
        diff_apply = st.checkbox("执行聚类差异基因分析", value=config['differential']['apply'])
        if diff_apply:
            diff_method = st.selectbox(
                "差异检验方法",
                ["Wilcoxon秩和检验", "t检验", "logistic回归"],
                index=["Wilcoxon秩和检验", "t检验", "logistic回归"].index(config['differential']['method'])
            )
            p_adjust_cutoff = st.slider("调整后p值最大值（p.adjust）", min_value=0.001, max_value=0.1, step=0.001, value=config['differential']['p_adjust_cutoff'])
            log2fc_min = st.slider("最小log2倍变化（log2FC）", min_value=0.1, max_value=2.0, step=0.05, value=config['differential']['log2fc_min'])
            min_pct = st.checkbox("仅保留在至少25%的细胞中表达的基因", value=config['differential']['min_pct'] >= 0.25)
            
            config['differential']['method'] = 'wilcoxon' if diff_method == 'Wilcoxon秩和检验' else 't-test' if diff_method == 't检验' else 'logreg'
            config['differential']['p_adjust_cutoff'] = p_adjust_cutoff
            config['differential']['log2fc_min'] = log2fc_min
            config['differential']['min_pct'] = 0.25 if min_pct else 0.0
        config['differential']['apply'] = diff_apply
    
    # 页面底部功能
    st.markdown("---")
    st.subheader("参数总览")
    
    # 显示当前配置
    st.json(config)
    
    # 保存配置并执行分析按钮
    if st.button("保存配置并执行分析"):
        try:
            # 更新全局状态
            st.session_state.pipeline_config = config
            
            # 跳转到结果可视化页面
            st.session_state.page = "结果可视化"
            
            # 执行分析
            from core import analysis_pipeline
            
            with st.spinner("正在执行分析..."):
                adata, result = analysis_pipeline.run_single_cell_pipeline(
                    st.session_state.anndata_obj,
                    config
                )
                
                # 更新全局状态
                st.session_state.anndata_obj = adata
                st.session_state.analysis_result = result
                st.session_state.is_analysis_done = True
                
                st.success("分析完成！")
                st.rerun()
        except Exception as e:
            st.error(f"执行分析失败: {exception_utils.get_user_friendly_error(e)}")