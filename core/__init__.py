"""
核心分析模块

提供单细胞和空间转录组分析的核心功能。
"""

# 数据加载
from .data_loader import (
    read_h5ad,
    read_10x_mtx,
    extract_zip,
    check_10x_structure,
    get_data_info
)

# 质控过滤
from .qc_filter import (
    calculate_qc_metrics,
    filter_cells,
    filter_genes,
    calculate_mitochondrial_percent,
    calculate_ribosomal_percent,
    filter_mitochondrial_cells,
    filter_ribosomal_cells
)

# 分析流程
from .analysis_pipeline import run_single_cell_pipeline
from .spatial_pipeline import run_spatial_pipeline, calculate_spatial_neighbors, find_spatial_variable_genes

# 空间数据
from .spatial_loader import read_spatial_h5ad, read_visium_zip, validate_spatial_data, get_spatial_data_info

# 可视化
from .visualization import (
    plot_qc_violin,
    plot_umap,
    plot_tsne,
    plot_gene_expression,
    plot_marker_genes,
    plot_volcano,
    plot_cluster_bar
)

# 富集分析
from .enrichment import run_enrichment, get_marker_genes, plot_enrichment_bubble, plot_enrichment_bar

# 降采样
from .downsampling import (
    get_memory_usage,
    check_memory_available,
    downsample_cells,
    downsample_genes,
    auto_downsample
)

# AI解析
from .ai_parser import AIParser

# SRA处理
from .sra_processor import (
    check_tool_installed,
    download_sra,
    convert_sra_to_fastq,
    process_sra
)

__all__ = [
    # 数据加载
    'read_h5ad',
    'read_10x_mtx',
    'extract_zip',
    'check_10x_structure',
    'get_data_info',
    # 质控
    'calculate_qc_metrics',
    'filter_cells',
    'filter_genes',
    'calculate_mitochondrial_percent',
    'calculate_ribosomal_percent',
    'filter_mitochondrial_cells',
    'filter_ribosomal_cells',
    # 分析流程
    'run_single_cell_pipeline',
    'run_spatial_pipeline',
    'calculate_spatial_neighbors',
    'find_spatial_variable_genes',
    # 空间数据
    'read_spatial_h5ad',
    'read_visium_zip',
    'validate_spatial_data',
    'get_spatial_data_info',
    # 可视化
    'plot_qc_violin',
    'plot_umap',
    'plot_tsne',
    'plot_gene_expression',
    'plot_marker_genes',
    'plot_volcano',
    'plot_cluster_bar',
    # 富集分析
    'run_enrichment',
    'get_marker_genes',
    'plot_enrichment_bubble',
    'plot_enrichment_bar',
    # 降采样
    'get_memory_usage',
    'check_memory_available',
    'downsample_cells',
    'downsample_genes',
    'auto_downsample',
    # AI解析
    'AIParser',
    # SRA处理
    'check_tool_installed',
    'download_sra',
    'convert_sra_to_fastq',
    'process_sra',
]
