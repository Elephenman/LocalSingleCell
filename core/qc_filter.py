import scanpy as sc
import numpy as np
import scipy.sparse


def calculate_qc_metrics(adata):
    """
    计算质控指标
    
    Args:
        adata: AnnData对象
    
    Returns:
        AnnData对象，添加了质控指标
    """
    # 计算基本质控指标
    sc.pp.calculate_qc_metrics(adata, inplace=True)
    
    return adata


def filter_genes(adata, min_cells=3):
    """
    过滤低表达基因
    
    Args:
        adata: AnnData对象
        min_cells: 基因至少在多少个细胞中表达
    
    Returns:
        AnnData对象，过滤后的结果
    """
    sc.pp.filter_genes(adata, min_cells=min_cells)
    return adata


def filter_cells(adata, min_genes=200, max_genes=6000, min_umi=500, max_umi=20000):
    """
    过滤低质量细胞
    
    Args:
        adata: AnnData对象
        min_genes: 每个细胞最少检测到的基因数
        max_genes: 每个细胞最多检测到的基因数
        min_umi: 每个细胞最少UMI总数
        max_umi: 每个细胞最多UMI总数
    
    Returns:
        AnnData对象，过滤后的结果
    """
    # 过滤基因数
    adata = adata[(adata.obs['n_genes_by_counts'] >= min_genes) & 
                  (adata.obs['n_genes_by_counts'] <= max_genes), :]
    
    # 过滤UMI数
    adata = adata[(adata.obs['total_counts'] >= min_umi) & 
                  (adata.obs['total_counts'] <= max_umi), :]
    
    return adata


def calculate_mitochondrial_percent(adata, mitochondrial_prefix="MT-"):
    """
    计算线粒体基因比例
    
    Args:
        adata: AnnData对象
        mitochondrial_prefix: 线粒体基因前缀
    
    Returns:
        AnnData对象，添加了线粒体基因比例
    """
    # 计算线粒体基因比例（兼容稀疏矩阵，避免 np.sum 返回 np.matrix）
    mt_mask = adata.var_names.str.startswith(mitochondrial_prefix)
    if mt_mask.sum() > 0:
        mt_counts = np.asarray(adata[:, mt_mask].X.sum(axis=1)).flatten()
    else:
        mt_counts = np.zeros(adata.n_obs)
    adata.obs['mt_percent'] = mt_counts / adata.obs['total_counts'].values * 100
    
    return adata


def calculate_ribosomal_percent(adata, ribosomal_prefix="RP[SL]"):
    """
    计算核糖体基因比例
    
    Args:
        adata: AnnData对象
        ribosomal_prefix: 核糖体基因前缀（正则表达式）
    
    Returns:
        AnnData对象，添加了核糖体基因比例
    """
    import re
    # 计算核糖体基因比例（兼容稀疏矩阵）
    ribo_genes = [gene for gene in adata.var_names if re.match(ribosomal_prefix, gene)]
    if ribo_genes:
        ribo_counts = np.asarray(adata[:, ribo_genes].X.sum(axis=1)).flatten()
        adata.obs['ribo_percent'] = ribo_counts / adata.obs['total_counts'].values * 100
    else:
        adata.obs['ribo_percent'] = 0
    
    return adata


def filter_mitochondrial_cells(adata, max_mt_percent=20):
    """
    过滤线粒体基因比例过高的细胞
    
    Args:
        adata: AnnData对象
        max_mt_percent: 最大线粒体基因比例
    
    Returns:
        AnnData对象，过滤后的结果
    """
    adata = adata[adata.obs['mt_percent'] <= max_mt_percent, :]
    return adata


def filter_ribosomal_cells(adata, max_ribo_percent=50):
    """
    过滤核糖体基因比例过高的细胞
    
    Args:
        adata: AnnData对象
        max_ribo_percent: 最大核糖体基因比例
    
    Returns:
        AnnData对象，过滤后的结果
    """
    adata = adata[adata.obs['ribo_percent'] <= max_ribo_percent, :]
    return adata