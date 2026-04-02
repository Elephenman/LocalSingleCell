"""
数据加载模块

提供单细胞和空间转录组数据的加载功能。
"""

import anndata as ad
import scanpy as sc
import zipfile
import os
import tempfile
from pathlib import Path
from typing import Union, Tuple, Optional

from utils.exceptions import DataLoadError, InvalidFileFormatError


def read_h5ad(file_path: Union[str, Path]) -> ad.AnnData:
    """
    读取h5ad文件

    Args:
        file_path: h5ad文件路径

    Returns:
        AnnData对象

    Raises:
        DataLoadError: 文件读取失败
        FileNotFoundError: 文件不存在
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        adata = ad.read_h5ad(file_path)
        return adata
    except Exception as e:
        raise DataLoadError(
            message=f"读取h5ad文件失败: {str(e)}",
            error_code="E102",
            details=e
        )


def read_10x_mtx(
    matrix_dir: Union[str, Path],
    var_names: str = 'gene_symbols',
    cache: bool = False
) -> ad.AnnData:
    """
    读取10x标准输出矩阵

    Args:
        matrix_dir: 矩阵目录路径，应包含 barcodes.tsv.gz, features.tsv.gz, matrix.mtx.gz
        var_names: 变量名类型，'gene_symbols' 或 'gene_ids'
        cache: 是否使用缓存

    Returns:
        AnnData对象

    Raises:
        DataLoadError: 文件读取失败
    """
    matrix_dir = Path(matrix_dir)

    if not matrix_dir.exists():
        raise FileNotFoundError(f"目录不存在: {matrix_dir}")

    try:
        adata = sc.read_10x_mtx(
            matrix_dir,
            var_names=var_names,
            cache=cache
        )
        return adata
    except Exception as e:
        raise DataLoadError(
            message=f"读取10x矩阵失败: {str(e)}",
            error_code="E102",
            details=e
        )


def extract_zip(
    zip_path: Union[str, Path],
    extract_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    解压zip文件

    Args:
        zip_path: zip文件路径
        extract_dir: 解压目录，默认为临时目录

    Returns:
        解压后的目录路径

    Raises:
        DataLoadError: 解压失败
    """
    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"文件不存在: {zip_path}")

    if extract_dir is None:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = Path(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return Path(extract_dir)
    except zipfile.BadZipFile as e:
        raise InvalidFileFormatError(
            message="无效的zip文件格式",
            error_code="E102",
            details=e
        )
    except Exception as e:
        raise DataLoadError(
            message=f"解压zip文件失败: {str(e)}",
            details=e
        )


def check_10x_structure(directory: Union[str, Path]) -> Tuple[bool, str]:
    """
    检查10x输出目录结构

    Args:
        directory: 目录路径

    Returns:
        (is_valid, message): 是否符合10x标准结构和提示信息
    """
    directory = Path(directory)

    if not directory.exists():
        return False, f"目录不存在: {directory}"

    # 检查必需文件
    required_files = ['barcodes.tsv.gz', 'features.tsv.gz', 'matrix.mtx.gz']
    # 也支持旧版10x格式
    alt_required_files = ['barcodes.tsv', 'genes.tsv', 'matrix.mtx']

    missing_files = []

    # 检查新版格式
    for file in required_files:
        file_path = directory / file
        if not file_path.exists():
            missing_files.append(file)

    if not missing_files:
        return True, "10x格式验证通过"

    # 检查旧版格式
    missing_alt = []
    for file in alt_required_files:
        file_path = directory / file
        if not file_path.exists():
            missing_alt.append(file)

    if not missing_alt:
        return True, "10x格式验证通过（旧版格式）"

    return False, f"缺少必需文件: {', '.join(missing_files)}"


def get_data_info(adata: ad.AnnData) -> dict:
    """
    获取AnnData对象的基本信息

    Args:
        adata: AnnData对象

    Returns:
        包含数据信息的字典
    """
    info = {
        'n_cells': adata.n_obs,
        'n_genes': adata.n_vars,
        'obs_columns': list(adata.obs.columns),
        'var_columns': list(adata.var.columns),
        'obsm_keys': list(adata.obsm.keys()) if adata.obsm else [],
        'uns_keys': list(adata.uns.keys()) if adata.uns else [],
    }

    # 添加质控信息（如果存在）
    if 'n_genes_by_counts' in adata.obs.columns:
        info['genes_per_cell'] = {
            'min': int(adata.obs['n_genes_by_counts'].min()),
            'max': int(adata.obs['n_genes_by_counts'].max()),
            'mean': float(adata.obs['n_genes_by_counts'].mean()),
        }

    if 'total_counts' in adata.obs.columns:
        info['counts_per_cell'] = {
            'min': int(adata.obs['total_counts'].min()),
            'max': int(adata.obs['total_counts'].max()),
            'mean': float(adata.obs['total_counts'].mean()),
        }

    return info
