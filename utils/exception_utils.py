"""
异常处理工具模块

提供异常捕获、转换和用户友好提示功能。
"""

import streamlit as st
import traceback
import logging
from typing import Optional, Callable, Any

from utils import logger_utils
from utils.exceptions import (
    LocalSingleCellError,
    DataLoadError,
    AnalysisError,
    ConfigurationError,
    ValidationError,
    ResourceLimitError,
    DependencyError,
    SecurityError,
    create_exception_from_error,
    get_error_message
)

# 初始化日志
logger = logger_utils.init_logger(__name__)


# ============================================================
# 错误消息映射
# ============================================================

ERROR_MESSAGE_MAP = {
    # Python 标准异常 -> 中文友好消息
    FileNotFoundError: "文件不存在，请检查文件路径是否正确",
    PermissionError: "权限不足，请检查文件访问权限",
    MemoryError: "内存不足，建议启用降采样或使用更小的数据集",
    ValueError: "参数值无效",
    TypeError: "参数类型错误",
    KeyError: "键值不存在",
    IndexError: "索引超出范围",
    ImportError: "模块导入失败，请检查依赖是否安装",
    ModuleNotFoundError: "模块未找到，请安装所需依赖",
    ZeroDivisionError: "除零错误",
    RuntimeError: "运行时错误",
    TimeoutError: "操作超时",
    KeyboardInterrupt: "操作被用户中断",
}

# 错误类型到自定义异常的映射
EXCEPTION_TYPE_MAP = {
    FileNotFoundError: DataLoadError,
    PermissionError: DataLoadError,
    MemoryError: ResourceLimitError,
    ValueError: ValidationError,
    TypeError: ValidationError,
    KeyError: ValidationError,
    TimeoutError: ResourceLimitError,
}


# ============================================================
# 核心函数
# ============================================================

def get_user_friendly_error(e: Exception) -> str:
    """
    获取用户友好的错误提示

    Args:
        e: 异常对象

    Returns:
        str: 用户友好的错误提示（中文）
    """
    # 记录原始异常
    logger.error(f"原始异常: {type(e).__name__}: {str(e)}")

    # 如果是自定义异常，直接返回其消息
    if isinstance(e, LocalSingleCellError):
        return f"[{e.error_code}] {e.user_message}"

    # 获取异常类型
    error_type = type(e)

    # 查找映射的消息
    if error_type in ERROR_MESSAGE_MAP:
        base_message = ERROR_MESSAGE_MAP[error_type]
        detail = str(e) if str(e) else ""
        if detail and detail not in base_message:
            return f"{base_message}: {detail}"
        return base_message

    # 未知的异常类型
    return f"操作失败: {str(e)}"


def convert_to_custom_exception(
    e: Exception,
    context: str = "",
    raise_custom: bool = False
) -> LocalSingleCellError:
    """
    将标准异常转换为自定义异常

    Args:
        e: 原始异常
        context: 错误上下文
        raise_custom: 是否抛出自定义异常

    Returns:
        自定义异常实例
    """
    # 如果已经是自定义异常，直接返回
    if isinstance(e, LocalSingleCellError):
        return e

    # 创建自定义异常
    custom_exception = create_exception_from_error(e, context)

    if raise_custom:
        raise custom_exception

    return custom_exception


def handle_exception(
    e: Exception,
    context: str = "操作",
    show_details: bool = True,
    reraise: bool = False
) -> None:
    """
    处理异常，在Streamlit中显示友好的错误信息

    Args:
        e: 异常对象
        context: 错误上下文描述
        show_details: 是否显示详细错误信息
        reraise: 是否重新抛出异常
    """
    # 获取用户友好的错误消息
    user_message = get_user_friendly_error(e)

    # 记录异常
    logger.error(f"{context}时发生错误: {str(e)}")
    logger.error(traceback.format_exc())

    # 在Streamlit中显示错误
    st.error(f"❌ {context}失败: {user_message}")

    # 显示详细的调试信息（可折叠）
    if show_details:
        with st.expander("🔧 详细错误信息（供调试用）"):
            st.code(traceback.format_exc())

            # 如果是自定义异常，显示错误代码
            if isinstance(e, LocalSingleCellError):
                st.info(f"错误代码: {e.error_code}")

    # 如果需要重新抛出
    if reraise:
        raise


def handle_exception_silent(e: Exception, context: str = "") -> str:
    """
    静默处理异常，仅返回错误消息

    Args:
        e: 异常对象
        context: 错误上下文

    Returns:
        错误消息
    """
    logger.error(f"{context}: {str(e)}")
    return get_user_friendly_error(e)


# ============================================================
# 装饰器
# ============================================================

def catch_exception(
    show_error: bool = True,
    reraise: bool = False,
    default_return: Any = None
):
    """
    异常捕获装饰器

    Args:
        show_error: 是否在Streamlit中显示错误
        reraise: 是否重新抛出异常
        default_return: 发生异常时的默认返回值

    Returns:
        装饰器函数

    Example:
        @catch_exception(show_error=True, reraise=False)
        def my_function():
            # ... code ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录错误
                logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                logger.error(traceback.format_exc())

                # 转换为自定义异常
                custom_exception = convert_to_custom_exception(e, func.__name__)

                # 显示错误
                if show_error:
                    try:
                        st.error(f"❌ {get_user_friendly_error(custom_exception)}")
                    except Exception:
                        pass  # Streamlit 可能不可用

                # 重新抛出或返回默认值
                if reraise:
                    raise custom_exception

                return default_return

        return wrapper
    return decorator


def catch_analysis_exception(func: Callable) -> Callable:
    """
    分析流程专用异常捕获装饰器

    专门用于捕获分析流程中的异常，提供更详细的错误信息。
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MemoryError:
            raise ResourceLimitError(
                message="内存不足，建议启用降采样功能",
                error_code="E501"
            )
        except ValueError as e:
            raise ValidationError(
                message=f"参数错误: {str(e)}",
                error_code="E401",
                details=e
            )
        except Exception as e:
            if isinstance(e, LocalSingleCellError):
                raise
            raise AnalysisError(
                message=f"分析过程发生错误: {str(e)}",
                error_code="E200",
                details=e
            )

    return wrapper


# ============================================================
# 上下文管理器
# ============================================================

class ErrorContext:
    """
    错误处理上下文管理器

    Example:
        with ErrorContext("数据加载"):
            # ... code that might raise ...
            pass
    """

    def __init__(
        self,
        context: str = "操作",
        show_error: bool = True,
        reraise: bool = False
    ):
        self.context = context
        self.show_error = show_error
        self.reraise = reraise
        self.error: Optional[Exception] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            handle_exception(
                exc_val,
                context=self.context,
                show_details=self.show_error,
                reraise=self.reraise
            )
            return not self.reraise  # 抑制异常除非要求重新抛出
        return False


# ============================================================
# 辅助函数
# ============================================================

def log_exception(e: Exception, context: str = "") -> None:
    """
    仅记录异常，不显示

    Args:
        e: 异常对象
        context: 错误上下文
    """
    context_str = f"{context}: " if context else ""
    logger.error(f"{context_str}{type(e).__name__}: {str(e)}")
    logger.debug(traceback.format_exc())


def is_recoverable_error(e: Exception) -> bool:
    """
    判断错误是否可恢复

    Args:
        e: 异常对象

    Returns:
        是否可恢复
    """
    # 不可恢复的错误类型
    non_recoverable = (
        MemoryError,
        KeyboardInterrupt,
        SystemExit,
    )

    if isinstance(e, non_recoverable):
        return False

    # 自定义异常中可恢复的类型
    recoverable_custom = (
        ValidationError,
        DataLoadError,
    )

    if isinstance(e, recoverable_custom):
        return True

    # 默认不可恢复
    return False


def get_error_suggestion(error_code: str) -> Optional[str]:
    """
    根据错误代码获取解决建议

    Args:
        error_code: 错误代码

    Returns:
        解决建议
    """
    suggestions = {
        "E101": "请检查文件路径是否正确，确保文件存在",
        "E102": "请确保上传的是有效的 .h5ad 文件或 10x 格式数据",
        "E103": "请上传较小的文件或在配置中启用降采样功能",
        "E501": "建议启用降采样功能或减少分析的基因数量",
        "E502": "请清理磁盘空间后重试",
        "E601": "请参考帮助文档安装所需的外部工具",
    }

    return suggestions.get(error_code)
