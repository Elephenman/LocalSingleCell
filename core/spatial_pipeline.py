import scanpy as sc
import squidpy as sq
import numpy as np
from core import qc_filter
from typing import Callable, Optional


def run_spatial_pipeline(adata, config, progress_callback: Optional[Callable[[int, str], None]] = None):
    """
    运行空间转录组分析全流程

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

    # 1. 基础质控（与单细胞分析相同）(0-15%)
    update_progress(0, "正在进行空间数据质控...")
    adata = qc_filter.calculate_qc_metrics(adata)
    adata = qc_filter.calculate_mitochondrial_percent(
        adata, 
        mitochondrial_prefix=config['qc']['mitochondrial']['prefix']
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

    # 6. 细胞聚类 (75-85%)
    update_progress(78, "正在进行细胞聚类...")
    sc.tl.leiden(
        adata,
        resolution=config['clustering']['resolution']
    )
    n_clusters = len(adata.obs['leiden'].unique())
    update_progress(85, f"聚类完成：发现{n_clusters}个细胞亚群")

    # 7. 空间专属分析 (85-95%)
    if 'spatial' in config and config['spatial']['apply']:
        update_progress(87, "正在进行空间邻居图构建...")
        # 空间邻居图构建
        sq.gr.spatial_neighbors(
            adata,
            coord_type=config['spatial']['coord_type'],
            n_rings=config['spatial']['n_rings'],
            delaunay=config['spatial']['delaunay']
        )
        update_progress(90, "空间邻居图构建完成")

        # 空间可变基因分析
        if config['spatial']['spatial_variable_genes']['apply']:
            update_progress(91, "正在进行空间可变基因分析...")
            # 获取高变基因列表
            genes = None
            if config['normalization']['hvg']['apply'] and 'highly_variable' in adata.var:
                genes = adata.var_names[adata.var['highly_variable']].tolist()

            sq.gr.spatial_autocorr(
                adata,
                mode=config['spatial']['spatial_variable_genes']['mode'],
                genes=genes
            )
            update_progress(93, "空间可变基因分析完成")

        # 共定位分析
        if config['spatial']['colocalization']['apply']:
            update_progress(94, "正在进行共定位分析...")
            sq.gr.co_occurrence(
                adata,
                cluster_key='leiden',
                n_splits=config['spatial']['colocalization']['n_splits']
            )
            update_progress(95, "共定位分析完成")

        # 配体-受体分析
        if config['spatial']['ligand_receptor']['apply']:
            # 这里需要配体-受体数据库，暂时跳过
            pass

    # 8. 差异基因分析 (95-100%)
    if config['differential']['apply']:
        update_progress(96, "正在进行差异基因分析...")
        sc.tl.rank_genes_groups(
            adata,
            groupby='leiden',
            method=config['differential']['method'],
            n_genes=200,
            min_pct=config['differential']['min_pct']
        )
        update_progress(100, "差异基因分析完成")

    update_progress(100, "空间转录组分析流程全部完成！")
    return adata, result


def calculate_spatial_neighbors(adata, coord_type='grid', n_rings=1, delaunay=False):
    """
    计算空间邻居图
    
    Args:
        adata: AnnData对象
        coord_type: 坐标类型，'grid'或'generic'
        n_rings: 邻居环数
        delaunay: 是否使用Delaunay三角剖分
    
    Returns:
        AnnData对象
    """
    sq.gr.spatial_neighbors(
        adata,
        coord_type=coord_type,
        n_rings=n_rings,
        delaunay=delaunay
    )
    return adata


def find_spatial_variable_genes(adata, mode='moran', genes=None):
    """
    识别空间可变基因
    
    Args:
        adata: AnnData对象
        mode: 自相关模式，'moran'或'geary'
        genes: 要分析的基因列表，None表示所有基因
    
    Returns:
        AnnData对象
    """
    sq.gr.spatial_autocorr(
        adata,
        mode=mode,
        genes=genes
    )
    return adata


def analyze_colocalization(adata, cluster_key='leiden', n_splits=1):
    """
    分析细胞类型共定位
    
    Args:
        adata: AnnData对象
        cluster_key: 聚类标签列名
        n_splits: 分割数
    
    Returns:
        AnnData对象
    """
    sq.gr.co_occurrence(
        adata,
        cluster_key=cluster_key,
        n_splits=n_splits
    )
    return adata
