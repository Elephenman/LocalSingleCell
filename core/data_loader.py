import anndata as ad
import scanpy as sc
import zipfile
import os
import tempfile


def read_h5ad(file_path):
    """
    读取h5ad文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        AnnData对象
    """
    try:
        adata = ad.read_h5ad(file_path)
        return adata
    except Exception as e:
        raise Exception(f"读取h5ad文件失败: {str(e)}")


def read_10x_mtx(matrix_dir):
    """
    读取10x标准输出矩阵
    
    Args:
        matrix_dir: 矩阵目录路径
    
    Returns:
        AnnData对象
    """
    try:
        adata = sc.read_10x_mtx(
            matrix_dir,
            var_names='gene_symbols',
            cache=False
        )
        return adata
    except Exception as e:
        raise Exception(f"读取10x矩阵失败: {str(e)}")


def extract_zip(zip_path, extract_dir):
    """
    解压zip文件
    
    Args:
        zip_path: zip文件路径
        extract_dir: 解压目录
    
    Returns:
        解压后的目录路径
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir
    except Exception as e:
        raise Exception(f"解压zip文件失败: {str(e)}")


def check_10x_structure(directory):
    """
    检查10x输出目录结构
    
    Args:
        directory: 目录路径
    
    Returns:
        bool: 是否符合10x标准结构
    """
    required_files = ['barcodes.tsv.gz', 'features.tsv.gz', 'matrix.mtx.gz']
    for file in required_files:
        file_path = os.path.join(directory, file)
        if not os.path.exists(file_path):
            return False
    return True