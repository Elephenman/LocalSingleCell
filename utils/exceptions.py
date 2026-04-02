"""
自定义异常类模块

定义项目专用的异常类层次结构，提供精确的错误诊断和用户友好的提示。
"""

from typing import Optional, Any


# ============================================================
# 基础异常类
# ============================================================

class LocalSingleCellError(Exception):
    """
    LocalSingleCell 基础异常类

    所有项目自定义异常的基类。

    Attributes:
        error_code: 错误代码
        user_message: 用户友好的错误消息
        details: 详细错误信息
    """

    error_code: str = "E000"
    default_message: str = "发生未知错误"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.user_message = message or self.default_message
        self.error_code = error_code or self.error_code
        self.details = details
        super().__init__(self.user_message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.user_message}"

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'error_code': self.error_code,
            'message': self.user_message,
            'details': str(self.details) if self.details else None
        }


# ============================================================
# 数据相关异常
# ============================================================

class DataLoadError(LocalSingleCellError):
    """数据加载错误"""
    error_code = "E100"
    default_message = "数据加载失败"


class FileNotFoundError(DataLoadError):
    """文件未找到错误"""
    error_code = "E101"
    default_message = "文件不存在，请检查文件路径"


class InvalidFileFormatError(DataLoadError):
    """文件格式无效错误"""
    error_code = "E102"
    default_message = "文件格式不支持或已损坏"


class FileSizeExceededError(DataLoadError):
    """文件大小超限错误"""
    error_code = "E103"
    default_message = "文件大小超过限制"


class DataValidationError(DataLoadError):
    """数据验证失败错误"""
    error_code = "E104"
    default_message = "数据验证失败，请检查数据格式"


class UnsupportedDataTypeError(DataLoadError):
    """不支持的数据类型错误"""
    error_code = "E105"
    default_message = "不支持的数据类型"


# ============================================================
# 分析相关异常
# ============================================================

class AnalysisError(LocalSingleCellError):
    """分析过程错误"""
    error_code = "E200"
    default_message = "分析过程发生错误"


class QCError(AnalysisError):
    """质控错误"""
    error_code = "E201"
    default_message = "质控过程发生错误"


class NormalizationError(AnalysisError):
    """归一化错误"""
    error_code = "E202"
    default_message = "归一化过程发生错误"


class DimensionReductionError(AnalysisError):
    """降维错误"""
    error_code = "E203"
    default_message = "降维分析过程发生错误"


class ClusteringError(AnalysisError):
    """聚类错误"""
    error_code = "E204"
    default_message = "聚类分析过程发生错误"


class DifferentialExpressionError(AnalysisError):
    """差异分析错误"""
    error_code = "E205"
    default_message = "差异基因分析过程发生错误"


class EnrichmentError(AnalysisError):
    """富集分析错误"""
    error_code = "E206"
    default_message = "富集分析过程发生错误"


class SpatialAnalysisError(AnalysisError):
    """空间分析错误"""
    error_code = "E207"
    default_message = "空间转录组分析过程发生错误"


# ============================================================
# 配置相关异常
# ============================================================

class ConfigurationError(LocalSingleCellError):
    """配置错误"""
    error_code = "E300"
    default_message = "配置错误"


class ConfigFileNotFoundError(ConfigurationError):
    """配置文件未找到错误"""
    error_code = "E301"
    default_message = "配置文件不存在"


class InvalidConfigError(ConfigurationError):
    """配置无效错误"""
    error_code = "E302"
    default_message = "配置参数无效"


class MissingConfigKeyError(ConfigurationError):
    """配置键缺失错误"""
    error_code = "E303"
    default_message = "缺少必需的配置参数"


# ============================================================
# 验证相关异常
# ============================================================

class ValidationError(LocalSingleCellError):
    """验证错误"""
    error_code = "E400"
    default_message = "输入验证失败"


class InvalidParameterError(ValidationError):
    """参数无效错误"""
    error_code = "E401"
    default_message = "参数值无效"


class ParameterOutOfRangeError(ValidationError):
    """参数超出范围错误"""
    error_code = "E402"
    default_message = "参数值超出有效范围"


class InvalidSRAIdError(ValidationError):
    """SRA ID 无效错误"""
    error_code = "E403"
    default_message = "SRA ID 格式无效"


class InvalidGeneNameError(ValidationError):
    """基因名称无效错误"""
    error_code = "E404"
    default_message = "基因名称无效"


# ============================================================
# 资源相关异常
# ============================================================

class ResourceLimitError(LocalSingleCellError):
    """资源限制错误"""
    error_code = "E500"
    default_message = "资源限制错误"


class MemoryLimitError(ResourceLimitError):
    """内存不足错误"""
    error_code = "E501"
    default_message = "内存不足，请尝试降采样或使用更小的数据集"


class DiskSpaceError(ResourceLimitError):
    """磁盘空间不足错误"""
    error_code = "E502"
    default_message = "磁盘空间不足"


class TimeoutError(ResourceLimitError):
    """超时错误"""
    error_code = "E503"
    default_message = "操作超时"


class AnalysisCancelledError(ResourceLimitError):
    """分析取消错误"""
    error_code = "E504"
    default_message = "分析已被用户取消"


# ============================================================
# 依赖相关异常
# ============================================================

class DependencyError(LocalSingleCellError):
    """依赖错误"""
    error_code = "E600"
    default_message = "依赖缺失或版本不兼容"


class ToolNotFoundError(DependencyError):
    """工具未找到错误"""
    error_code = "E601"
    default_message = "必要的外部工具未安装"


class VersionMismatchError(DependencyError):
    """版本不匹配错误"""
    error_code = "E602"
    default_message = "依赖版本不兼容"


# ============================================================
# 安全相关异常
# ============================================================

class SecurityError(LocalSingleCellError):
    """安全错误"""
    error_code = "E700"
    default_message = "安全检查失败"


class PathTraversalError(SecurityError):
    """路径遍历错误"""
    error_code = "E701"
    default_message = "检测到非法的路径访问"


class FileSignatureError(SecurityError):
    """文件签名错误"""
    error_code = "E702"
    default_message = "文件类型验证失败，可能是伪装的文件"


class MaliciousInputError(SecurityError):
    """恶意输入错误"""
    error_code = "E703"
    default_message = "检测到潜在的恶意输入"


# ============================================================
# 异常工厂函数
# ============================================================

def create_exception_from_error(original_error: Exception, context: str = "") -> LocalSingleCellError:
    """
    从原始异常创建自定义异常

    Args:
        original_error: 原始异常
        context: 错误上下文

    Returns:
        自定义异常实例
    """
    error_type = type(original_error)
    error_message = str(original_error)

    # 映射标准异常到自定义异常
    exception_map = {
        FileNotFoundError: FileNotFoundError,
        PermissionError: DataLoadError,
        MemoryError: MemoryLimitError,
        ValueError: ValidationError,
        KeyError: ValidationError,
        TypeError: ValidationError,
    }

    # 获取对应的异常类
    exception_class = exception_map.get(error_type, LocalSingleCellError)

    # 创建异常实例
    message = f"{context}: {error_message}" if context else error_message
    return exception_class(message=message, details=original_error)


# ============================================================
# 错误消息映射
# ============================================================

ERROR_MESSAGES = {
    # 数据加载错误
    "E100": "数据加载失败，请检查数据格式和完整性",
    "E101": "文件不存在，请检查文件路径是否正确",
    "E102": "文件格式不支持或已损坏，请上传有效的 .h5ad 或 10x 格式文件",
    "E103": "文件大小超过限制，请上传较小的文件或启用降采样",
    "E104": "数据验证失败，请确保数据格式正确",
    "E105": "不支持的数据类型，请上传单细胞或空间转录组数据",

    # 分析错误
    "E200": "分析过程发生错误，请查看日志了解详情",
    "E201": "质控过程发生错误，请检查质控参数设置",
    "E202": "归一化过程发生错误",
    "E203": "降维分析过程发生错误，请检查PCA参数",
    "E204": "聚类分析过程发生错误，请尝试调整分辨率参数",
    "E205": "差异基因分析过程发生错误",
    "E206": "富集分析过程发生错误，请检查基因列表",
    "E207": "空间转录组分析过程发生错误",

    # 配置错误
    "E300": "配置错误，请检查配置文件",
    "E301": "配置文件不存在，将使用默认配置",
    "E302": "配置参数无效，请检查参数值",
    "E303": "缺少必需的配置参数",

    # 验证错误
    "E400": "输入验证失败，请检查输入值",
    "E401": "参数值无效",
    "E402": "参数值超出有效范围",
    "E403": "SRA ID 格式无效，应为 SRR/ERR/DRR 开头后接数字",
    "E404": "基因名称无效",

    # 资源错误
    "E500": "资源限制错误",
    "E501": "内存不足，建议启用降采样或使用更小的数据集",
    "E502": "磁盘空间不足，请清理磁盘空间后重试",
    "E503": "操作超时，请尝试简化分析流程",
    "E504": "分析已被用户取消",

    # 依赖错误
    "E600": "依赖缺失或版本不兼容",
    "E601": "必要的外部工具未安装，请查看帮助文档",
    "E602": "依赖版本不兼容，请更新依赖",

    # 安全错误
    "E700": "安全检查失败",
    "E701": "检测到非法的路径访问",
    "E702": "文件类型验证失败",
    "E703": "检测到潜在的恶意输入",
}


def get_error_message(error_code: str) -> str:
    """
    获取错误消息

    Args:
        error_code: 错误代码

    Returns:
        错误消息
    """
    return ERROR_MESSAGES.get(error_code, "未知错误")
