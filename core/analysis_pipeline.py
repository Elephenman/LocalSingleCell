import scanpy as sc
import numpy as np
from core import qc_filter
from typing import Callable, Optional


def run_single_cell_pipeline(adata, config, progress_callback: Optional[Callable[[int, str], None]] = None):
    """
    运行单细胞分析全流程

    Args:
        adata: AnnData对象
        config: 分析参数配置
        progress_callback: 进度回调函数，接收 (progress_percent, status_message)

    Returns:
        AnnData对象，包含分析结果
        dict: 分析结果摘要
    """
    result = {}

    # 定义进度更新辅助函数
    def update_progress(percent, message):
        if progress_callback:
            progress_callback(percent, message)

    # 设置随机种子
    np.random.seed(config['random_seed'])

    # 1. 质控 (0-15%)
    update_progress(0, "正在进行质控分析...")
    adata = qc_filter.calculate_qc_metrics(adata)
    
    # 计算线粒体基因比例
    adata = qc_filter.calculate_mitochondrial_percent(
        adata, 
        mitochondrial_prefix=config['qc']['mitochondrial']['prefix']
    )
    
    # 计算核糖体基因比例
    adata = qc_filter.calculate_ribosomal_percent(
        adata, 
        ribosomal_prefix=config['qc']['ribosomal']['prefix']
    )
    
    # 记录质控前的细胞数和基因数
    result['pre_qc'] = {
        'n_cells': adata.n_obs,
        'n_genes': adata.n_vars
    }
    
    # 基因过滤
    if config['qc']['gene_filter']['apply']:
        adata = qc_filter.filter_genes(
            adata, 
            min_cells=config['qc']['gene_filter']['min_cells']
        )
    
    # 细胞过滤
    adata = qc_filter.filter_cells(
        adata,
        min_genes=config['qc']['cell_filter']['min_genes'],
        max_genes=config['qc']['cell_filter']['max_genes'],
        min_umi=config['qc']['cell_filter']['min_umi'],
        max_umi=config['qc']['cell_filter']['max_umi']
    )
    
    # 线粒体基因过滤
    if config['qc']['mitochondrial']['apply']:
        adata = qc_filter.filter_mitochondrial_cells(
            adata, 
            max_mt_percent=config['qc']['mitochondrial']['max_percent']
        )
    
    # 核糖体基因过滤
    if config['qc']['ribosomal']['apply']:
        adata = qc_filter.filter_ribosomal_cells(
            adata, 
            max_ribo_percent=config['qc']['ribosomal']['max_percent']
        )
    
    # 记录质控后的细胞数和基因数
    result['post_qc'] = {
        'n_cells': adata.n_obs,
        'n_genes': adata.n_vars
    }
    update_progress(15, f"质控完成：{result['post_qc']['n_cells']}个细胞")

    # 2. 归一化 (15-30%)
    update_progress(20, "正在进行归一化...")
    if config['normalization']['method'] == 'scanpy':
        sc.pp.normalize_total(
            adata,
            target_sum=config['normalization']['target_sum']
        )
        sc.pp.log1p(adata)
    elif config['normalization']['method'] == 'cpm':
        sc.pp.normalize_total(adata, target_sum=1e6)
    update_progress(30, "归一化完成")

    # 3. 高变基因筛选 (30-45%)
    update_progress(35, "正在筛选高变基因...")
    if config['normalization']['hvg']['apply']:
        sc.pp.highly_variable_genes(
            adata,
            n_top_genes=config['normalization']['hvg']['n_top_genes'],
            flavor=config['normalization']['hvg']['method']
        )
    update_progress(45, "高变基因筛选完成")

    # 4. 数据标准化 (45-55%)
    update_progress(50, "正在进行数据标准化...")
    if config['normalization']['scaling']['apply']:
        sc.pp.scale(
            adata,
            max_value=config['normalization']['scaling']['max_value']
        )
    update_progress(55, "数据标准化完成")

    # 5. 降维分析 (55-75%)
    update_progress(60, "正在进行PCA降维...")
    # PCA
    sc.tl.pca(
        adata,
        n_comps=config['dimension_reduction']['pca']['n_comps'],
        use_highly_variable=config['dimension_reduction']['pca']['use_hvg']
    )
    update_progress(65, "PCA降维完成")

    # UMAP
    if config['dimension_reduction']['umap']['apply']:
        update_progress(68, "正在进行UMAP降维...")
        sc.pp.neighbors(
            adata,
            n_pcs=config['clustering']['n_pcs'],
            n_neighbors=config['clustering']['n_neighbors']
        )
        sc.tl.umap(
            adata,
            n_neighbors=config['dimension_reduction']['umap']['n_neighbors'],
            min_dist=config['dimension_reduction']['umap']['min_dist']
        )
        update_progress(72, "UMAP降维完成")

    # tSNE
    if config['dimension_reduction']['tsne']['apply']:
        update_progress(73, "正在进行tSNE降维...")
        sc.tl.tsne(
            adata,
            perplexity=config['dimension_reduction']['tsne']['perplexity'],
            use_rep='X_pca'
        )
        update_progress(75, "tSNE降维完成")

    # 6. 细胞聚类 (75-85%)
    update_progress(78, "正在进行细胞聚类...")
    sc.tl.leiden(
        adata,
        resolution=config['clustering']['resolution']
    )
    n_clusters = len(adata.obs['leiden'].unique())
    update_progress(85, f"聚类完成：发现{n_clusters}个细胞亚群")

    # 7. 差异基因分析 (85-100%)
    if config['differential']['apply']:
        update_progress(88, "正在进行差异基因分析...")
        # 为每个聚类计算标记基因
        sc.tl.rank_genes_groups(
            adata,
            groupby='leiden',
            method=config['differential']['method'],
            n_genes=200,
            min_pct=config['differential']['min_pct']
        )
        update_progress(100, "差异基因分析完成")

    update_progress(100, "分析流程全部完成！")
    return adata, result