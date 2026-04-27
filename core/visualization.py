import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd
import numpy as np
import scanpy as sc


def plot_qc_violin(adata, save_path=None):
    """
    绘制质控指标小提琴图
    
    Args:
        adata: AnnData对象
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 基因数分布
    sns.violinplot(y=adata.obs['n_genes_by_counts'], ax=axes[0])
    axes[0].set_title('每个细胞的基因数')
    axes[0].set_ylabel('基因数')
    
    # UMI数分布
    sns.violinplot(y=adata.obs['total_counts'], ax=axes[1])
    axes[1].set_title('每个细胞的UMI数')
    axes[1].set_ylabel('UMI数')
    
    # 线粒体基因比例分布
    sns.violinplot(y=adata.obs['mt_percent'], ax=axes[2])
    axes[2].set_title('每个细胞的线粒体基因比例')
    axes[2].set_ylabel('线粒体基因比例(%)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_umap(adata, color='leiden', save_path=None):
    """
    绘制UMAP降维图

    Args:
        adata: AnnData对象
        color: 着色依据
        save_path: 保存路径

    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    sc.pl.umap(adata, color=color, show=False, ax=ax)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_tsne(adata, color='leiden', save_path=None):
    """
    绘制tSNE降维图

    Args:
        adata: AnnData对象
        color: 着色依据
        save_path: 保存路径

    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    sc.pl.tsne(adata, color=color, show=False, ax=ax)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_gene_expression(adata, gene, save_path=None):
    """
    绘制基因表达散点图

    Args:
        adata: AnnData对象
        gene: 基因名
        save_path: 保存路径

    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    if 'X_umap' in adata.obsm:
        sc.pl.umap(adata, color=gene, show=False, ax=ax)
    elif 'X_tsne' in adata.obsm:
        sc.pl.tsne(adata, color=gene, show=False, ax=ax)
    else:
        sc.pl.pca(adata, color=gene, show=False, ax=ax)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_marker_genes(adata, markers, save_path=None):
    """
    绘制标记基因热图

    Args:
        adata: AnnData对象
        markers: 标记基因列表
        save_path: 保存路径

    Returns:
        matplotlib Figure对象
    """
    sc.pl.heatmap(adata, var_names=markers, groupby='leiden', show=False)
    fig = plt.gcf()
    # heatmap 返回 axes dict，无法直接传入 ax，使用 gcf() 获取当前图

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_volcano(adata, save_path=None):
    """
    绘制差异基因火山图
    
    Args:
        adata: AnnData对象
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    # 提取差异基因结果
    try:
        de_genes = sc.get.rank_genes_groups_df(adata, group=None)
    except Exception as e:
        raise Exception(f"无法获取差异基因结果: {str(e)}")
    
    # 计算-log10(p值)
    de_genes['-log10(padj)'] = -np.log10(de_genes['padj'] + 1e-300)
    
    # 创建火山图
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制所有基因
    ax.scatter(
        de_genes['logfoldchanges'],
        de_genes['-log10(padj)'],
        alpha=0.5,
        s=50
    )
    
    # 标记显著差异基因
    sig_genes = de_genes[(de_genes['padj'] < 0.05) & (abs(de_genes['logfoldchanges']) > 0.5)]
    ax.scatter(
        sig_genes['logfoldchanges'],
        sig_genes['-log10(padj)'],
        color='red',
        alpha=0.8,
        s=50
    )
    
    # 添加阈值线
    ax.axhline(y=-np.log10(0.05), color='gray', linestyle='--')
    ax.axvline(x=-0.5, color='gray', linestyle='--')
    ax.axvline(x=0.5, color='gray', linestyle='--')
    
    ax.set_title('差异基因火山图')
    ax.set_xlabel('log2(倍数变化)')
    ax.set_ylabel('-log10(调整后p值)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_cluster_bar(adata, save_path=None):
    """
    绘制聚类细胞数量柱状图
    
    Args:
        adata: AnnData对象
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    cluster_key = 'leiden'
    cluster_counts = adata.obs[cluster_key].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    cluster_counts.plot(kind='bar', ax=ax)
    
    ax.set_title('各聚类细胞数量')
    ax.set_xlabel('聚类')
    ax.set_ylabel('细胞数量')
    
    # 添加百分比标签
    total_cells = cluster_counts.sum()
    for i, count in enumerate(cluster_counts):
        percent = (count / total_cells) * 100
        ax.text(i, count + 0.05 * total_cells, f'{percent:.1f}%', ha='center')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig