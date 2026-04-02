import re
import os


def validate_sra_id(sra_id):
    """
    校验SRA号格式
    
    Args:
        sra_id: SRA号
    
    Returns:
        bool: 是否有效
    """
    # SRA号格式：以SRR/ERR/DRR开头，后接数字
    pattern = r'^(SRR|ERR|DRR)\d+$'
    return bool(re.match(pattern, sra_id))


def validate_file_extension(file_path, allowed_extensions):
    """
    校验文件扩展名
    
    Args:
        file_path: 文件路径
        allowed_extensions: 允许的扩展名列表
    
    Returns:
        bool: 是否有效
    """
    ext = os.path.splitext(file_path)[1].lower()
    return ext in allowed_extensions


def validate_10x_structure(directory):
    """
    校验10x输出目录结构
    
    Args:
        directory: 目录路径
    
    Returns:
        bool: 是否有效
    """
    required_files = ['barcodes.tsv.gz', 'features.tsv.gz', 'matrix.mtx.gz']
    for file in required_files:
        file_path = os.path.join(directory, file)
        if not os.path.exists(file_path):
            return False
    return True


def validate_numeric_range(value, min_value, max_value):
    """
    校验数值范围
    
    Args:
        value: 数值
        min_value: 最小值
        max_value: 最大值
    
    Returns:
        bool: 是否有效
    """
    try:
        value = float(value)
        return min_value <= value <= max_value
    except (ValueError, TypeError):
        return False


def validate_not_empty(value):
    """
    校验非空值
    
    Args:
        value: 值
    
    Returns:
        bool: 是否有效
    """
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple)):
        return bool(len(value))
    return True