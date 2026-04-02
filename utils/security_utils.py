"""
安全工具模块

提供文件上传验证、路径安全检查、资源限制等安全功能。
"""

import os
import re
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, List, Union

# ============================================================
# 常量定义
# ============================================================

# 文件大小限制 (字节)
MAX_FILE_SIZE_MB = 1024
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'h5ad': ['.h5ad', '.h5'],
    '10x': ['.zip', '.tar.gz'],
    'image': ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.svg'],
    'data': ['.csv', '.tsv', '.xlsx']
}

# 文件魔数（文件头签名）
FILE_SIGNATURES = {
    'hdf5': b'\x89HDF',
    'zip': b'PK\x03\x04',
    'gzip': b'\x1f\x8b'
}

# 危险路径模式
DANGEROUS_PATTERNS = [
    r'\.\.',           # 路径遍历
    r'[<>:"|?*]',     # Windows 不允许的字符
    r'[\x00-\x1f]',   # 控制字符
]

# SRA ID 正则表达式
SRA_ID_PATTERN = re.compile(r'^(SRR|ERR|DRR)\d+$', re.IGNORECASE)


# ============================================================
# 文件验证函数
# ============================================================

def validate_file_size(file_path: Union[str, Path], max_size_mb: int = MAX_FILE_SIZE_MB) -> Tuple[bool, str]:
    """
    验证文件大小是否在限制范围内

    Args:
        file_path: 文件路径
        max_size_mb: 最大文件大小（MB）

    Returns:
        (is_valid, message): 验证结果和消息
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return False, f"文件不存在: {file_path}"

    file_size = file_path.stat().st_size
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        size_mb = file_size / (1024 * 1024)
        return False, f"文件大小 ({size_mb:.1f}MB) 超过限制 ({max_size_mb}MB)"

    return True, f"文件大小正常: {file_size / (1024*1024):.1f}MB"


def validate_file_extension(
    filename: str,
    allowed_extensions: List[str]
) -> Tuple[bool, str]:
    """
    验证文件扩展名是否允许

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表（包含点，如 ['.h5ad', '.h5']）

    Returns:
        (is_valid, message): 验证结果和消息
    """
    if not filename:
        return False, "文件名为空"

    # 获取文件扩展名（小写）
    ext = Path(filename).suffix.lower()

    # 标准化允许的扩展名
    normalized_extensions = [e.lower() if e.startswith('.') else f'.{e.lower()}' for e in allowed_extensions]

    if ext not in normalized_extensions:
        return False, f"不支持的文件格式: {ext}。支持的格式: {', '.join(normalized_extensions)}"

    return True, f"文件格式有效: {ext}"


def validate_file_signature(
    file_path: Union[str, Path],
    expected_type: str
) -> Tuple[bool, str]:
    """
    通过文件头验证文件类型

    Args:
        file_path: 文件路径
        expected_type: 期望的文件类型 ('hdf5', 'zip', 'gzip')

    Returns:
        (is_valid, message): 验证结果和消息
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return False, "文件不存在"

    if expected_type not in FILE_SIGNATURES:
        return False, f"未知的文件类型: {expected_type}"

    expected_signature = FILE_SIGNATURES[expected_type]

    try:
        with open(file_path, 'rb') as f:
            actual_signature = f.read(len(expected_signature))

        if actual_signature == expected_signature:
            return True, "文件类型验证通过"
        else:
            return False, f"文件类型不匹配，可能是伪装的文件"

    except Exception as e:
        return False, f"读取文件失败: {str(e)}"


def validate_uploaded_file(
    file_path: Union[str, Path],
    allowed_extensions: List[str],
    max_size_mb: int = MAX_FILE_SIZE_MB,
    check_signature: bool = False,
    expected_type: Optional[str] = None
) -> Tuple[bool, List[str]]:
    """
    综合验证上传文件

    Args:
        file_path: 文件路径
        allowed_extensions: 允许的扩展名
        max_size_mb: 最大文件大小（MB）
        check_signature: 是否检查文件签名
        expected_type: 期望的文件类型（用于签名验证）

    Returns:
        (is_valid, messages): 验证结果和消息列表
    """
    messages = []
    is_valid = True

    # 验证扩展名
    ext_valid, ext_msg = validate_file_extension(str(file_path), allowed_extensions)
    if not ext_valid:
        messages.append(ext_msg)
        is_valid = False

    # 验证文件大小
    size_valid, size_msg = validate_file_size(file_path, max_size_mb)
    if not size_valid:
        messages.append(size_msg)
        is_valid = False

    # 可选：验证文件签名
    if check_signature and expected_type:
        sig_valid, sig_msg = validate_file_signature(file_path, expected_type)
        if not sig_valid:
            messages.append(sig_msg)
            is_valid = False

    return is_valid, messages


# ============================================================
# 路径安全函数
# ============================================================

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的安全文件名
    """
    if not filename:
        return "unnamed_file"

    # 移除路径分隔符
    filename = os.path.basename(filename)

    # 替换危险字符为下划线
    for pattern in DANGEROUS_PATTERNS:
        filename = re.sub(pattern, '_', filename)

    # 移除前后空格和点
    filename = filename.strip('. ')

    # 如果清理后为空，使用默认名称
    if not filename:
        filename = "sanitized_file"

    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext

    return filename


def is_safe_path(base_dir: Union[str, Path], target_path: Union[str, Path]) -> bool:
    """
    检查目标路径是否在基础目录内（防止路径遍历攻击）

    Args:
        base_dir: 基础目录
        target_path: 目标路径

    Returns:
        是否安全
    """
    try:
        base_dir = Path(base_dir).resolve()
        target_path = Path(target_path).resolve()

        # 检查目标路径是否在基础目录内
        return str(target_path).startswith(str(base_dir))
    except Exception:
        return False


def validate_path_traversal(path: str) -> Tuple[bool, str]:
    """
    检查路径是否包含路径遍历攻击

    Args:
        path: 待检查的路径

    Returns:
        (is_safe, message): 安全性和消息
    """
    if not path:
        return False, "路径为空"

    # 检查危险模式
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, path):
            return False, f"路径包含非法字符或模式"

    # 检查路径遍历尝试
    normalized = os.path.normpath(path)
    if '..' in normalized.split(os.sep):
        return False, "路径包含非法的遍历尝试"

    return True, "路径安全"


# ============================================================
# 输入验证函数
# ============================================================

def validate_sra_id(sra_id: str) -> Tuple[bool, str]:
    """
    验证 SRA ID 格式

    Args:
        sra_id: SRA 编号

    Returns:
        (is_valid, message): 验证结果和消息
    """
    if not sra_id:
        return False, "SRA ID 为空"

    sra_id = sra_id.strip().upper()

    if SRA_ID_PATTERN.match(sra_id):
        return True, f"有效的 SRA ID: {sra_id}"
    else:
        return False, f"无效的 SRA ID 格式: {sra_id}。应为 SRR/ERR/DRR 开头后接数字"


def validate_sra_ids(sra_ids: str) -> Tuple[bool, List[str], List[str]]:
    """
    批量验证 SRA ID

    Args:
        sra_ids: SRA 编号字符串（逗号或空格分隔）

    Returns:
        (all_valid, valid_ids, invalid_ids): 验证结果、有效ID列表、无效ID列表
    """
    # 分割输入
    ids = re.split(r'[,\s]+', sra_ids.strip())
    ids = [id.strip() for id in ids if id.strip()]

    valid_ids = []
    invalid_ids = []

    for sra_id in ids:
        is_valid, _ = validate_sra_id(sra_id)
        if is_valid:
            valid_ids.append(sra_id.upper())
        else:
            invalid_ids.append(sra_id)

    return len(invalid_ids) == 0, valid_ids, invalid_ids


def validate_gene_name(gene_name: str) -> Tuple[bool, str]:
    """
    验证基因名称

    Args:
        gene_name: 基因名称

    Returns:
        (is_valid, message): 验证结果和消息
    """
    if not gene_name:
        return False, "基因名称为空"

    # 基因名称通常只包含字母、数字和连字符
    if not re.match(r'^[A-Za-z0-9\-_]+$', gene_name):
        return False, f"基因名称包含非法字符: {gene_name}"

    # 长度限制
    if len(gene_name) > 50:
        return False, f"基因名称过长: {gene_name}"

    return True, f"有效的基因名称: {gene_name}"


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """
    清理用户输入

    Args:
        text: 用户输入文本
        max_length: 最大长度

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除控制字符
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


# ============================================================
# 资源限制函数
# ============================================================

def check_memory_usage(max_percent: float = 80.0) -> Tuple[bool, float, str]:
    """
    检查内存使用情况

    Args:
        max_percent: 最大允许使用百分比

    Returns:
        (is_ok, current_percent, message): 检查结果、当前使用率、消息
    """
    try:
        import psutil
        memory = psutil.virtual_memory()
        current_percent = memory.percent

        if current_percent > max_percent:
            return False, current_percent, f"内存使用率过高: {current_percent:.1f}% (限制: {max_percent}%)"

        return True, current_percent, f"内存使用正常: {current_percent:.1f}%"

    except ImportError:
        return True, 0.0, "无法获取内存信息（psutil 未安装）"


def estimate_memory_requirement(n_cells: int, n_genes: int) -> float:
    """
    估算分析所需内存

    Args:
        n_cells: 细胞数量
        n_genes: 基因数量

    Returns:
        预估内存需求（GB）
    """
    # 稀疏矩阵存储约 4 bytes per non-zero element
    # 假设稀疏度为 5%
    sparsity = 0.05
    non_zero_elements = n_cells * n_genes * sparsity

    # 基础矩阵存储
    matrix_memory = non_zero_elements * 4 / (1024**3)  # GB

    # 分析过程通常需要 3-5 倍内存
    estimated_memory = matrix_memory * 5

    return estimated_memory


def check_disk_space(required_gb: float, path: str = '.') -> Tuple[bool, float, str]:
    """
    检查磁盘空间

    Args:
        required_gb: 需要的空间（GB）
        path: 检查路径

    Returns:
        (is_ok, available_gb, message): 检查结果、可用空间、消息
    """
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        free_gb = free / (1024**3)

        if free_gb < required_gb:
            return False, free_gb, f"磁盘空间不足: 可用 {free_gb:.1f}GB，需要 {required_gb:.1f}GB"

        return True, free_gb, f"磁盘空间充足: 可用 {free_gb:.1f}GB"

    except Exception as e:
        return True, 0.0, f"无法检查磁盘空间: {str(e)}"


# ============================================================
# 文件完整性校验
# ============================================================

def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    计算文件哈希值

    Args:
        file_path: 文件路径
        algorithm: 哈希算法 ('md5', 'sha1', 'sha256')

    Returns:
        文件哈希值
    """
    file_path = Path(file_path)

    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"不支持的哈希算法: {algorithm}")

    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def verify_file_integrity(
    file_path: Union[str, Path],
    expected_hash: str,
    algorithm: str = 'md5'
) -> Tuple[bool, str]:
    """
    验证文件完整性

    Args:
        file_path: 文件路径
        expected_hash: 期望的哈希值
        algorithm: 哈希算法

    Returns:
        (is_valid, message): 验证结果和消息
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return False, f"文件不存在: {file_path}"

    actual_hash = calculate_file_hash(file_path, algorithm)

    if actual_hash.lower() == expected_hash.lower():
        return True, "文件完整性验证通过"
    else:
        return False, f"文件完整性验证失败: 哈希值不匹配"
