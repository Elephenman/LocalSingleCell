import scanpy as sc
import numpy as np
from core import qc_filter


def run_single_cell_pipeline(adata, config):
    """
    运行单细胞分析全流程
    
    Args:
        adata: AnnData对象
        config: 分析参数配置
    
    Returns:
        AnnData对象，包含分析结果
        dict: 分析结果摘要
    """
    result = {}
    
    # 设置随机种子
    np.random.seed(config['random_seed'])
    
    # 1. 质控
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
    
    # 2. 归一化（先保存原始计数矩阵，供 scVI 等下游工具使用）
    adata.layers["counts"] = adata.X.copy()
    
    if config['normalization']['method'] == 'scanpy':
        sc.pp.normalize_total(
            adata, 
            target_sum=config['normalization']['target_sum']
        )
        sc.pp.log1p(adata)
    elif config['normalization']['method'] == 'cpm':
        sc.pp.normalize_total(adata, target_sum=1e6)
    
    # 3. 高变基因筛选
    if config['normalization']['hvg']['apply']:
        sc.pp.highly_variable_genes(
            adata,
            n_top_genes=config['normalization']['hvg']['n_top_genes'],
            flavor=config['normalization']['hvg']['method']
        )
    
    # 4. 数据标准化
    if config['normalization']['scaling']['apply']:
        sc.pp.scale(
            adata,
            max_value=config['normalization']['scaling']['max_value']
        )
    
    # 5. 降维分析
    # PCA
    sc.tl.pca(
        adata,
        n_comps=config['dimension_reduction']['pca']['n_comps'],
        use_highly_variable=config['dimension_reduction']['pca']['use_hvg']
    )
    
    # UMAP
    if config['dimension_reduction']['umap']['apply']:
        sc.pp.neighbors(
            adata,
            n_pcs=config['clustering']['n_pcs'],
            n_neighbors=config['clustering']['n_neighbors']
        )
        # 注意：n_neighbors 已在 sc.pp.neighbors 中设置，sc.tl.umap 无需重复传入
        sc.tl.umap(
            adata,
            min_dist=config['dimension_reduction']['umap']['min_dist']
        )
    
    # tSNE
    if config['dimension_reduction']['tsne']['apply']:
        sc.tl.tsne(
            adata,
            perplexity=config['dimension_reduction']['tsne']['perplexity'],
            use_rep='X_pca'
        )
    
    # 6. 细胞聚类
    sc.tl.leiden(
        adata,
        resolution=config['clustering']['resolution']
    )
    
    # 7. 差异基因分析
    if config['differential']['apply']:
        # 为每个聚类计算标记基因
        sc.tl.rank_genes_groups(
            adata,
            groupby='leiden',
            method=config['differential']['method'],
            n_genes=200,
            min_pct=config['differential']['min_pct']
        )
    
    return adata, result