import scanpy as sc
import squidpy as sq
import os
import zipfile
import tempfile
from pathlib import Path


def read_spatial_h5ad(file_path):
    """
    读取空间转录组h5ad文件
    
    Args:
        file_path: h5ad文件路径
    
    Returns:
        AnnData对象，包含空间转录组数据
    """
    adata = sc.read_h5ad(file_path)
    
    # 检查是否包含空间坐标信息
    if 'spatial' not in adata.obsm:
        raise Exception("h5ad文件中未找到空间坐标信息（spatial）")
    
    return adata


def read_visium_zip(zip_path):
    """
    读取10x Visium标准输出zip文件
    
    Args:
        zip_path: zip文件路径
    
    Returns:
        AnnData对象，包含空间转录组数据
    """
    # 解压到临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 查找Visium输出目录结构
        temp_path = Path(temp_dir)
        
        # 尝试常见的Visium目录结构
        possible_paths = [
            temp_path,
            temp_path / "outs",
            next(temp_path.glob("*/outs"), None),
            next(temp_path.glob("*"), None)
        ]
        
        visium_dir = None
        for path in possible_paths:
            if path and path.exists():
                # 检查是否包含必要的文件
                if (path / "filtered_feature_bc_matrix.h5").exists() or \
                   (path / "raw_feature_bc_matrix.h5").exists():
                    visium_dir = path
                    break
        
        if not visium_dir:
            raise Exception("未找到有效的10x Visium输出目录结构")
        
        # 使用Squidpy读取Visium数据
        adata = sq.read.visium(visium_dir)
        
        return adata


def validate_spatial_data(adata):
    """
    验证空间转录组数据的完整性
    
    Args:
        adata: AnnData对象
    
    Returns:
        bool: 数据是否有效
    """
    issues = []
    warnings = []
    
    # 检查空间坐标（必需）
    if 'spatial' not in adata.obsm:
        issues.append("缺少空间坐标信息（spatial）")
    
    # 检查图像数据（可选）
    if 'spatial' not in adata.uns or 'images' not in adata.uns['spatial']:
        warnings.append("缺少组织切片图像")
    
    # 检查比例尺（可选）
    if 'spatial' in adata.uns and 'scalefactors' not in adata.uns['spatial']:
        warnings.append("缺少空间比例尺信息")
    
    # 只要没有致命问题就认为数据有效
    is_valid = len(issues) == 0
    
    # 返回时将警告也包含在issues中，但标记为警告
    all_issues = issues + [f"[警告] {w}" for w in warnings]
    
    return is_valid, all_issues


def get_spatial_data_info(adata):
    """
    获取空间转录组数据的基本信息
    
    Args:
        adata: AnnData对象
    
    Returns:
        dict: 数据信息字典
    """
    info = {
        'n_cells': adata.n_obs,
        'n_genes': adata.n_vars,
        'has_spatial': 'spatial' in adata.obsm,
        'has_image': 'spatial' in adata.uns and 'images' in adata.uns['spatial']
    }
    
    # 获取图像信息
    if info['has_image']:
        images = adata.uns['spatial']['images']
        info['image_types'] = list(images.keys())
        if images:
            first_img = list(images.values())[0]
            info['image_shape'] = first_img.shape if hasattr(first_img, 'shape') else 'unknown'
    
    # 获取空间坐标信息
    if info['has_spatial']:
        coords = adata.obsm['spatial']
        info['coord_range'] = {
            'x_min': float(coords[:, 0].min()),
            'x_max': float(coords[:, 0].max()),
            'y_min': float(coords[:, 1].min()),
            'y_max': float(coords[:, 1].max())
        }
    
    return info
