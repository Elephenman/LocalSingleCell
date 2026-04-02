import matplotlib.pyplot as plt
import seaborn as sns
import squidpy as sq
import scanpy as sc
import numpy as np


def plot_spatial_scatter(adata, color=None, library_id=None, spot_size=None, alpha=1.0, save_path=None):
    """
    绘制空间散点图
    
    Args:
        adata: AnnData对象
        color: 着色依据的列名或基因名
        library_id: 文库ID
        spot_size: 点大小
        alpha: 透明度
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    sq.pl.spatial_scatter(
        adata,
        color=color,
        library_id=library_id,
        spot_size=spot_size,
        alpha=alpha,
        ax=ax,
        show=False
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_spatial_segment(adata, color=None, library_id=None, seg_cell_id=None, spot_size=None, save_path=None):
    """
    绘制空间分割图
    
    Args:
        adata: AnnData对象
        color: 着色依据的列名或基因名
        library_id: 文库ID
        seg_cell_id: 分割细胞ID
        spot_size: 点大小
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    sq.pl.spatial_segment(
        adata,
        color=color,
        library_id=library_id,
        seg_cell_id=seg_cell_id,
        spot_size=spot_size,
        ax=ax,
        show=False
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_genes_spatial(adata, genes, ncols=4, spot_size=None, img=False, img_key='hires', img_alpha=0.5, save_path=None):
    """
    绘制多个基因的空间表达图
    
    Args:
        adata: AnnData对象
        genes: 基因列表
        ncols: 列数
        spot_size: 点大小
        img: 是否显示组织图像
        img_key: 图像键
        img_alpha: 图像透明度
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    n_genes = len(genes)
    nrows = (n_genes + ncols - 1) // ncols
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 5 * nrows))
    if nrows == 1 and ncols == 1:
        axes = [[axes]]
    elif nrows == 1:
        axes = [axes]
    elif ncols == 1:
        axes = [[ax] for ax in axes]
    
    for i, gene in enumerate(genes):
        row = i // ncols
        col = i % ncols
        ax = axes[row][col]
        
        if gene in adata.var_names:
            sq.pl.spatial_scatter(
                adata,
                color=gene,
                spot_size=spot_size,
                ax=ax,
                show=False,
                title=gene,
                img=img,
                img_key=img_key,
                img_alpha=img_alpha
            )
        else:
            ax.text(0.5, 0.5, f'Gene {gene} not found', ha='center', va='center')
            ax.set_title(gene)
    
    # 隐藏多余的子图
    for i in range(n_genes, nrows * ncols):
        row = i // ncols
        col = i % ncols
        axes[row][col].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_spatial_variable_genes(adata, n_top=10, save_path=None):
    """
    绘制空间可变基因
    
    Args:
        adata: AnnData对象
        n_top: 显示的Top基因数量
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    # 检查是否有空间自相关结果
    if 'moranI' in adata.uns:
        # 获取空间可变基因
        genes = adata.uns['moranI'].sort_values('I', ascending=False).head(n_top)['gene'].tolist()
        
        # 绘制
        sq.pl.spatial_scatter(
            adata,
            color=genes[:4],  # 最多显示4个基因
            ncols=2,
            show=False
        )
        fig = plt.gcf()
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, '请先运行空间可变基因分析', ha='center', va='center', fontsize=12)
        ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_co_occurrence(adata, cluster_key='leiden', save_path=None):
    """
    绘制共定位分析结果
    
    Args:
        adata: AnnData对象
        cluster_key: 聚类标签列名
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 检查是否有共定位结果
    if 'co_occurrence' in adata.uns:
        sq.pl.co_occurrence(
            adata,
            cluster_key=cluster_key,
            ax=ax,
            show=False
        )
    else:
        ax.text(0.5, 0.5, '请先运行共定位分析', ha='center', va='center', fontsize=12)
        ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_spatial_cluster_composition(adata, cluster_key='leiden', save_path=None):
    """
    绘制空间聚类组成
    
    Args:
        adata: AnnData对象
        cluster_key: 聚类标签列名
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 空间散点图
    sq.pl.spatial_scatter(
        adata,
        color=cluster_key,
        ax=ax1,
        show=False
    )
    ax1.set_title('空间聚类分布')
    
    # 聚类细胞数量柱状图
    cluster_counts = adata.obs[cluster_key].value_counts().sort_index()
    cluster_counts.plot(kind='bar', ax=ax2)
    ax2.set_title('各聚类细胞数量')
    ax2.set_xlabel('聚类')
    ax2.set_ylabel('细胞数量')
    
    # 添加百分比标签
    total_cells = cluster_counts.sum()
    for i, count in enumerate(cluster_counts):
        percent = (count / total_cells) * 100
        ax2.text(i, count + 0.05 * total_cells, f'{percent:.1f}%', ha='center')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_image_with_overlay(adata, color=None, library_id=None, image_key='hires', alpha=0.5, save_path=None):
    """
    绘制带有组织图像覆盖的空间图
    
    Args:
        adata: AnnData对象
        color: 着色依据
        library_id: 文库ID
        image_key: 图像键
        alpha: 图像透明度
        save_path: 保存路径
    
    Returns:
        matplotlib Figure对象
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    sq.pl.spatial_scatter(
        adata,
        color=color,
        library_id=library_id,
        img=True,
        img_alpha=alpha,
        img_key=image_key,
        ax=ax,
        show=False
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
