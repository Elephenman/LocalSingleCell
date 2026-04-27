import streamlit as st
import traceback
from utils import logger_utils

# 初始化日志
logger = logger_utils.init_logger(__name__)


def get_user_friendly_error(e):
    """
    获取用户友好的错误提示
    
    Args:
        e: 异常对象
    
    Returns:
        str: 用户友好的错误提示
    """
    # 记录原始异常
    logger.error(f"原始异常: {str(e)}")
    
    # 常见异常的友好提示
    error_map = {
        'FileNotFoundError': '文件不存在',
        'PermissionError': '权限不足',
        'ValueError': '数值输入错误',
        'TypeError': '类型错误',
        'ImportError': '导入模块失败',
        'ModuleNotFoundError': '模块未找到',
        'KeyError': '键值错误',
        'IndexError': '索引错误',
        'ZeroDivisionError': '除零错误',
    }
    
    # 获取异常类型名称
    error_type = type(e).__name__
    
    # 返回友好提示
    if error_type in error_map:
        return f"{error_map[error_type]}: {str(e)}"
    else:
        return f"操作失败: {str(e)}"


def catch_exception(func):
    """
    异常捕获装饰器
    
    Args:
        func: 被装饰的函数
    
    Returns:
        function: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise Exception(get_user_friendly_error(e)) from e
    return wrapper


def handle_exception(e, context="操作"):
    """
    处理异常，在Streamlit中显示友好的错误信息
    
    Args:
        e: 异常对象
        context: 错误上下文描述
    """
    # 记录异常
    logger.error(f"{context}时发生错误: {str(e)}")
    logger.error(traceback.format_exc())
    
    # 在Streamlit中显示错误
    st.error(f"❌ {context}失败: {get_user_friendly_error(e)}")
    
    # 显示详细的调试信息（可折叠）
    with st.expander("🔧 详细错误信息（供调试用）"):
        st.code(traceback.format_exc())