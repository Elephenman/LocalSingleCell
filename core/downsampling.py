import numpy as np
import scanpy as sc
import psutil
import os


def get_memory_usage():
    """
    获取当前内存使用情况
    
    Returns:
        float: 内存使用百分比
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_percent = psutil.virtual_memory().percent
    return mem_percent


def check_memory_available(threshold_percent=80):
    """
    检查内存是否可用
    
    Args:
        threshold_percent: 内存使用率阈值（百分比）
        
    Returns:
        bool: 内存是否可用
    """
    mem_percent = get_memory_usage()
    return mem_percent < threshold_percent


def downsample_cells(adata, target_cells=5000, random_seed=42):
    """
    细胞数降采样
    
    Args:
        adata: AnnData对象
        target_cells: 目标细胞数
        random_seed: 随机种子
        
    Returns:
        AnnData对象，降采样后的结果
    """
    if adata.n_obs <= target_cells:
        return adata
    
    np.random.seed(random_seed)
    indices = np.random.choice(adata.n_obs, target_cells, replace=False)
    return adata[indices, :].copy()


def downsample_genes(adata, target_genes=10000, by_expression=True, random_seed=42):
    """
    基因数降采样

    Args:
        adata: AnnData对象
        target_genes: 目标基因数
        by_expression: 是否按表达量筛选
        random_seed: 随机种子（仅 by_expression=False 时使用）

    Returns:
        AnnData对象，降采样后的结果
    """
    if adata.n_vars <= target_genes:
        return adata

    if by_expression:
        gene_counts = np.array(adata.X.sum(axis=0)).flatten()
        top_indices = np.argsort(gene_counts)[::-1][:target_genes]
        return adata[:, top_indices].copy()
    else:
        np.random.seed(random_seed)  # 使用传入参数，不再硬编码 42
        indices = np.random.choice(adata.n_vars, target_genes, replace=False)
        return adata[:, indices].copy()


def auto_downsample(adata, max_cells=10000, max_genes=20000, suggest_only=False):
    """
    自动降采样
    
    Args:
        adata: AnnData对象
        max_cells: 最大细胞数
        max_genes: 最大基因数
        suggest_only: 是否仅给出建议而不执行
        
    Returns:
        dict: 降采样建议或结果
        AnnData对象（如果执行了降采样）
    """
    suggestions = {
        'needs_downsampling': False,
        'cell_downsample': False,
        'gene_downsample': False,
        'original_cells': adata.n_obs,
        'original_genes': adata.n_vars,
        'target_cells': max_cells,
        'target_genes': max_genes
    }
    
    result_adata = adata
    
    if adata.n_obs > max_cells:
        suggestions['needs_downsampling'] = True
        suggestions['cell_downsample'] = True
        if not suggest_only:
            result_adata = downsample_cells(result_adata, max_cells)
            suggestions['final_cells'] = result_adata.n_obs
    
    if adata.n_vars > max_genes:
        suggestions['needs_downsampling'] = True
        suggestions['gene_downsample'] = True
        if not suggest_only:
            result_adata = downsample_genes(result_adata, max_genes)
            suggestions['final_genes'] = result_adata.n_vars
    
    return suggestions, result_adata
