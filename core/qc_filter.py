"""
质控过滤模块

提供单细胞数据的质控指标计算和过滤功能。
"""

import scanpy as sc
import numpy as np
import re
from typing import Union, Optional
from anndata import AnnData


def calculate_qc_metrics(adata: AnnData) -> AnnData:
    """
    计算质控指标

    Args:
        adata: AnnData对象

    Returns:
        AnnData对象，添加了质控指标到obs和var中
    """
    # 计算基本质控指标
    sc.pp.calculate_qc_metrics(adata, inplace=True)

    return adata


def filter_genes(
    adata: AnnData,
    min_cells: int = 3
) -> AnnData:
    """
    过滤低表达基因

    Args:
        adata: AnnData对象
        min_cells: 基因至少在多少个细胞中表达，默认3

    Returns:
        AnnData对象，过滤后的结果
    """
    sc.pp.filter_genes(adata, min_cells=min_cells)
    return adata


def filter_cells(
    adata: AnnData,
    min_genes: int = 200,
    max_genes: int = 6000,
    min_umi: int = 500,
    max_umi: int = 20000
) -> AnnData:
    """
    过滤低质量细胞

    Args:
        adata: AnnData对象
        min_genes: 每个细胞最少检测到的基因数，默认200
        max_genes: 每个细胞最多检测到的基因数，默认6000
        min_umi: 每个细胞最少UMI总数，默认500
        max_umi: 每个细胞最多UMI总数，默认20000

    Returns:
        AnnData对象，过滤后的结果
    """
    # 过滤基因数
    adata = adata[
        (adata.obs['n_genes_by_counts'] >= min_genes) &
        (adata.obs['n_genes_by_counts'] <= max_genes), :
    ]

    # 过滤UMI数
    adata = adata[
        (adata.obs['total_counts'] >= min_umi) &
        (adata.obs['total_counts'] <= max_umi), :
    ]

    return adata


def calculate_mitochondrial_percent(
    adata: AnnData,
    mitochondrial_prefix: str = "MT-"
) -> AnnData:
    """
    计算线粒体基因比例

    Args:
        adata: AnnData对象
        mitochondrial_prefix: 线粒体基因前缀，默认"MT-"

    Returns:
        AnnData对象，添加了线粒体基因比例到obs['mt_percent']中
    """
    # 计算线粒体基因比例
    adata.obs['mt_percent'] = np.sum(
        adata[:, adata.var_names.str.startswith(mitochondrial_prefix)].X, axis=1
    ) / adata.obs['total_counts'] * 100

    return adata


def calculate_ribosomal_percent(
    adata: AnnData,
    ribosomal_prefix: str = "RP[SL]"
) -> AnnData:
    """
    计算核糖体基因比例

    Args:
        adata: AnnData对象
        ribosomal_prefix: 核糖体基因前缀（正则表达式），默认"RP[SL]"

    Returns:
        AnnData对象，添加了核糖体基因比例到obs['ribo_percent']中
    """
    # 计算核糖体基因比例
    ribo_genes = [gene for gene in adata.var_names if re.match(ribosomal_prefix, gene)]
    if ribo_genes:
        adata.obs['ribo_percent'] = np.sum(
            adata[:, ribo_genes].X, axis=1
        ) / adata.obs['total_counts'] * 100
    else:
        adata.obs['ribo_percent'] = 0

    return adata


def filter_mitochondrial_cells(
    adata: AnnData,
    max_mt_percent: float = 20.0
) -> AnnData:
    """
    过滤线粒体基因比例过高的细胞

    Args:
        adata: AnnData对象
        max_mt_percent: 最大线粒体基因比例，默认20.0

    Returns:
        AnnData对象，过滤后的结果
    """
    adata = adata[adata.obs['mt_percent'] <= max_mt_percent, :]
    return adata


def filter_ribosomal_cells(
    adata: AnnData,
    max_ribo_percent: float = 50.0
) -> AnnData:
    """
    过滤核糖体基因比例过高的细胞

    Args:
        adata: AnnData对象
        max_ribo_percent: 最大核糖体基因比例，默认50.0

    Returns:
        AnnData对象，过滤后的结果
    """
    adata = adata[adata.obs['ribo_percent'] <= max_ribo_percent, :]
    return adata
