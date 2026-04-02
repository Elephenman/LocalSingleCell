import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from core import visualization
from utils import exception_utils


def show():
    """
    结果可视化页面
    """
    # 页面前置校验
    if not st.session_state.is_analysis_done:
        st.warning("请先完成分析流程")
        return
    
    st.title("结果可视化")
    
    # 获取AnnData对象
    adata = st.session_state.anndata_obj
    
    # 标签页
    tab1, tab2, tab3, tab4 = st.tabs(["质控结果可视化", "降维聚类可视化", "标记基因可视化", "差异基因可视化"])
    
    # 标签页1：质控结果可视化
    with tab1:
        st.subheader("质控结果可视化")
        
        # 选择图表类型
        st.markdown("#### 选择图表类型")
        show_violin = st.checkbox("质控指标小提琴图", value=True)
        show_scatter = st.checkbox("基因数vs UMI总数散点图", value=True)
        show_histogram = st.checkbox("线粒体基因比例分布直方图", value=True)
        
        # 图表配置
        st.markdown("#### 图表配置")
        figsize = st.slider("图表大小", min_value=5, max_value=20, step=1, value=10)
        
        # 生成图表按钮
        if st.button("生成图表", key="qc_plot"):
            try:
                # 生成质控指标小提琴图
                if show_violin:
                    st.markdown("### 质控指标小提琴图")
                    fig = visualization.plot_qc_violin(adata)
                    st.pyplot(fig)
                    plt.close()
                
                # 生成基因数vs UMI总数散点图
                if show_scatter:
                    st.markdown("### 基因数vs UMI总数散点图")
                    fig, ax = plt.subplots(figsize=(figsize, figsize))
                    ax.scatter(adata.obs['n_genes_by_counts'], adata.obs['total_counts'], alpha=0.5)
                    ax.set_xlabel('基因数')
                    ax.set_ylabel('UMI总数')
                    ax.set_title('基因数vs UMI总数散点图')
                    st.pyplot(fig)
                    plt.close()
                
                # 生成线粒体基因比例分布直方图
                if show_histogram:
                    st.markdown("### 线粒体基因比例分布直方图")
                    fig, ax = plt.subplots(figsize=(figsize, figsize))
                    ax.hist(adata.obs['mt_percent'], bins=50)
                    ax.set_xlabel('线粒体基因比例(%)')
                    ax.set_ylabel('细胞数量')
                    ax.set_title('线粒体基因比例分布直方图')
                    st.pyplot(fig)
                    plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页2：降维聚类可视化
    with tab2:
        st.subheader("降维聚类可视化")
        
        # 基础配置
        st.markdown("#### 基础配置")
        
        # 选择降维类型
        dim_options = []
        if 'X_umap' in adata.obsm:
            dim_options.append('UMAP')
        if 'X_tsne' in adata.obsm:
            dim_options.append('tSNE')
        if 'X_pca' in adata.obsm:
            dim_options.append('PCA')
        
        if dim_options:
            dim_type = st.selectbox("降维类型", dim_options, index=0)
        else:
            st.error("未找到降维结果")
            return
        
        # 选择颜色分组依据
        color_options = list(adata.obs.columns)
        color_by = st.selectbox("颜色分组依据", color_options, index=color_options.index('leiden') if 'leiden' in color_options else 0)
        
        # 图表配置
        st.markdown("#### 图表配置")
        point_size = st.slider("点大小", min_value=1, max_value=10, step=1, value=5)
        alpha = st.slider("透明度", min_value=0.1, max_value=1.0, step=0.1, value=0.5)
        show_labels = st.checkbox("显示聚类标签", value=False)
        
        # 生成图表按钮
        if st.button("生成图表", key="dim_plot"):
            try:
                # 生成降维聚类散点图
                st.markdown(f"### {dim_type}降维聚类散点图")
                if dim_type == 'UMAP':
                    fig = visualization.plot_umap(adata, color=color_by)
                elif dim_type == 'tSNE':
                    fig = visualization.plot_tsne(adata, color=color_by)
                else:  # PCA
                    import scanpy as sc
                    sc.pl.pca(adata, color=color_by, show=False)
                    fig = plt.gcf()
                st.pyplot(fig)
                plt.close()
                
                # 生成聚类细胞数量柱状图
                st.markdown("### 聚类细胞数量柱状图")
                fig = visualization.plot_cluster_bar(adata)
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页3：标记基因可视化
    with tab3:
        st.subheader("标记基因可视化")
        
        # 基础配置
        st.markdown("#### 基础配置")
        
        # 选择降维类型
        dim_options = []
        if 'X_umap' in adata.obsm:
            dim_options.append('UMAP')
        if 'X_tsne' in adata.obsm:
            dim_options.append('tSNE')
        if 'X_pca' in adata.obsm:
            dim_options.append('PCA')
        
        if dim_options:
            dim_type = st.selectbox("降维类型", dim_options, index=0)
        else:
            st.error("未找到降维结果")
            return
        
        # 选择聚类
        cluster_key = 'leiden'
        clusters = sorted(adata.obs[cluster_key].unique())
        selected_clusters = st.multiselect("选择聚类", clusters, default=clusters)
        
        # 自定义基因输入
        custom_genes = st.text_input("自定义基因名（多个用逗号分隔）")
        
        # 标记基因排序方式
        sort_by = st.selectbox("标记基因排序方式", ["按log2FC降序", "按p值升序"], index=0)
        
        # 每个聚类展示的Top标记基因数量
        top_n = st.slider("每个聚类展示的Top标记基因数量", min_value=1, max_value=20, step=1, value=5)
        
        # 生成图表按钮
        if st.button("生成图表", key="marker_plot"):
            try:
                # 处理自定义基因
                gene_list = []
                if custom_genes:
                    gene_list = [gene.strip() for gene in custom_genes.split(',') if gene.strip()]
                
                # 如果没有自定义基因，获取标记基因
                if not gene_list:
                    import scanpy as sc
                    marker_genes = []
                    for cluster in selected_clusters:
                        # 获取该聚类的标记基因
                        df = sc.get.rank_genes_groups_df(adata, group=str(cluster))
                        # 过滤显著差异基因
                        sig_genes = df[df['padj'] < 0.05]
                        # 按选择的方式排序
                        if sort_by == "按log2FC降序":
                            sig_genes = sig_genes.sort_values('logfoldchanges', ascending=False)
                        else:
                            sig_genes = sig_genes.sort_values('padj', ascending=True)
                        # 取前top_n个
                        top_genes = sig_genes.head(top_n)['names'].tolist()
                        marker_genes.extend(top_genes)
                    # 去重
                    gene_list = list(set(marker_genes))
                
                # 生成基因表达降维散点图
                st.markdown("### 基因表达降维散点图")
                for gene in gene_list:
                    if gene in adata.var_names:
                        st.markdown(f"#### {gene}")
                        fig = visualization.plot_gene_expression(adata, gene)
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.warning(f"基因 {gene} 不存在")
                
                # 生成标记基因热图
                if gene_list:
                    st.markdown("### 标记基因热图")
                    fig = visualization.plot_marker_genes(adata, gene_list)
                    st.pyplot(fig)
                    plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")
    
    # 标签页4：差异基因可视化
    with tab4:
        st.subheader("差异基因可视化")
        
        # 基础配置
        st.markdown("#### 基础配置")
        
        # 选择聚类对比
        cluster_key = 'leiden'
        clusters = sorted(adata.obs[cluster_key].unique())
        cluster_choice = st.selectbox("选择聚类对比", ["所有聚类vs其他"] + clusters, index=0)
        
        # 差异基因阈值
        p_adjust_cutoff = st.slider("差异基因显著性阈值 (p.adjust)", min_value=0.001, max_value=0.1, step=0.001, value=0.05)
        log2fc_cutoff = st.slider("差异基因log2FC阈值", min_value=0.1, max_value=2.0, step=0.05, value=0.5)
        
        # 生成图表按钮
        if st.button("生成图表", key="diff_plot"):
            try:
                # 生成差异基因火山图
                st.markdown("### 差异基因火山图")
                fig = visualization.plot_volcano(adata)
                st.pyplot(fig)
                plt.close()
                
                # 生成差异基因上下调数量柱状图
                st.markdown("### 差异基因上下调数量柱状图")
                import scanpy as sc
                import pandas as pd
                import seaborn as sns
                
                # 收集每个聚类的差异基因信息
                cluster_key = 'leiden'
                clusters = sorted(adata.obs[cluster_key].unique())
                
                up_down_counts = []
                for cluster in clusters:
                    df = sc.get.rank_genes_groups_df(adata, group=str(cluster))
                    sig_genes = df[df['padj'] < p_adjust_cutoff]
                    up_genes = sig_genes[sig_genes['logfoldchanges'] > log2fc_cutoff]
                    down_genes = sig_genes[sig_genes['logfoldchanges'] < -log2fc_cutoff]
                    up_down_counts.append({
                        'cluster': cluster,
                        'up': len(up_genes),
                        'down': len(down_genes)
                    })
                
                # 创建DataFrame
                counts_df = pd.DataFrame(up_down_counts)
                
                # 转换为长格式
                counts_long = counts_df.melt(id_vars='cluster', var_name='type', value_name='count')
                
                # 绘制柱状图
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.barplot(x='cluster', y='count', hue='type', data=counts_long, ax=ax)
                ax.set_title('差异基因上下调数量')
                ax.set_xlabel('聚类')
                ax.set_ylabel('基因数量')
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"生成图表失败: {exception_utils.get_user_friendly_error(e)}")