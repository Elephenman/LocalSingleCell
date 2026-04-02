# =============================================================================
# LocalSingleCell - Performance Monitoring Utilities
# 性能监控工具
# =============================================================================

"""
性能监控工具模块

提供分析流程的性能监控功能，包括：
- 分析耗时统计
- 内存使用监控
- 性能日志记录
- 性能报告生成
"""

import json
import logging
import os
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class PerformanceRecord:
    """性能记录数据类"""

    step_name: str
    start_time: float
    end_time: float
    duration_seconds: float
    memory_start_mb: float
    memory_end_mb: float
    memory_peak_mb: float
    memory_delta_mb: float
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "step_name": self.step_name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
            "duration_seconds": round(self.duration_seconds, 3),
            "memory_start_mb": round(self.memory_start_mb, 2),
            "memory_end_mb": round(self.memory_end_mb, 2),
            "memory_peak_mb": round(self.memory_peak_mb, 2),
            "memory_delta_mb": round(self.memory_delta_mb, 2),
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class MemoryMonitor:
    """内存监控器"""

    def __init__(self, alert_percent: float = 85.0):
        """
        初始化内存监控器

        Args:
            alert_percent: 内存使用告警阈值（百分比）
        """
        self.alert_percent = alert_percent
        self._process = psutil.Process()

    def get_memory_usage(self) -> float:
        """
        获取当前进程内存使用量（MB）

        Returns:
            内存使用量（MB）
        """
        try:
            return self._process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

    def get_system_memory_info(self) -> Dict[str, float]:
        """
        获取系统内存信息

        Returns:
            包含 total, available, used, percent 的字典
        """
        mem = psutil.virtual_memory()
        return {
            "total_mb": mem.total / (1024 * 1024),
            "available_mb": mem.available / (1024 * 1024),
            "used_mb": mem.used / (1024 * 1024),
            "percent": mem.percent,
        }

    def check_memory_alert(self) -> tuple[bool, str]:
        """
        检查内存使用是否超过告警阈值

        Returns:
            (是否需要告警, 告警消息)
        """
        mem_info = self.get_system_memory_info()
        if mem_info["percent"] >= self.alert_percent:
            return True, f"内存使用率 {mem_info['percent']:.1f}% 超过阈值 {self.alert_percent}%"
        return False, ""

    def get_peak_memory(self) -> float:
        """
        获取进程峰值内存使用量（MB）

        Returns:
            峰值内存使用量（MB）
        """
        try:
            return self._process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0


class AnalysisTimer:
    """分析耗时计时器"""

    def __init__(
        self,
        step_name: str,
        memory_monitor: Optional[MemoryMonitor] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化计时器

        Args:
            step_name: 步骤名称
            memory_monitor: 内存监控器实例
            metadata: 额外元数据
        """
        self.step_name = step_name
        self.memory_monitor = memory_monitor or MemoryMonitor()
        self.metadata = metadata or {}
        self._start_time = 0.0
        self._end_time = 0.0
        self._memory_start = 0.0
        self._memory_end = 0.0
        self._memory_peak = 0.0
        self._success = True
        self._error_message = ""

    def __enter__(self) -> "AnalysisTimer":
        """进入上下文"""
        self._start_time = time.time()
        self._memory_start = self.memory_monitor.get_memory_usage()
        self._memory_peak = self._memory_start
        logger.debug(f"[{self.step_name}] 开始执行, 内存: {self._memory_start:.2f}MB")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """退出上下文"""
        self._end_time = time.time()
        self._memory_end = self.memory_monitor.get_memory_usage()
        self._memory_peak = max(self._memory_start, self._memory_end)

        if exc_type is not None:
            self._success = False
            self._error_message = str(exc_val)
            logger.error(f"[{self.step_name}] 执行失败: {self._error_message}")
        else:
            duration = self._end_time - self._start_time
            logger.debug(
                f"[{self.step_name}] 完成, 耗时: {duration:.2f}s, "
                f"内存变化: {self._memory_end - self._memory_start:.2f}MB"
            )

        return False  # 不抑制异常

    def set_error(self, message: str) -> None:
        """设置错误信息"""
        self._success = False
        self._error_message = message

    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        self.metadata[key] = value

    def get_record(self) -> PerformanceRecord:
        """获取性能记录"""
        return PerformanceRecord(
            step_name=self.step_name,
            start_time=self._start_time,
            end_time=self._end_time,
            duration_seconds=self._end_time - self._start_time,
            memory_start_mb=self._memory_start,
            memory_end_mb=self._memory_end,
            memory_peak_mb=self._memory_peak,
            memory_delta_mb=self._memory_end - self._memory_start,
            success=self._success,
            error_message=self._error_message,
            metadata=self.metadata,
        )


class PerformanceLogger:
    """性能日志记录器"""

    def __init__(
        self,
        output_dir: Union[str, Path] = "logs/performance",
        enable_monitoring: bool = True,
        log_memory: bool = True,
        log_timing: bool = True,
        alert_memory_percent: float = 85.0,
    ):
        """
        初始化性能日志记录器

        Args:
            output_dir: 日志输出目录
            enable_monitoring: 是否启用监控
            log_memory: 是否记录内存
            log_timing: 是否记录时间
            alert_memory_percent: 内存告警阈值
        """
        self.output_dir = Path(output_dir)
        self.enable_monitoring = enable_monitoring
        self.log_memory = log_memory
        self.log_timing = log_timing
        self.alert_memory_percent = alert_memory_percent

        self.memory_monitor = MemoryMonitor(alert_percent=alert_memory_percent)
        self._records: List[PerformanceRecord] = []
        self._session_start = time.time()
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 创建输出目录
        if self.enable_monitoring:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def track_step(
        self, step_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> "AnalysisTimer":
        """
        跟踪步骤执行

        Args:
            step_name: 步骤名称
            metadata: 额外元数据

        Yields:
            AnalysisTimer 实例
        """
        if not self.enable_monitoring:
            # 如果监控未启用，返回一个空的上下文管理器
            timer = AnalysisTimer(step_name, metadata=metadata)
            timer._start_time = time.time()
            yield timer
            timer._end_time = time.time()
            return

        timer = AnalysisTimer(
            step_name, memory_monitor=self.memory_monitor, metadata=metadata
        )

        with timer:
            yield timer

        # 记录结果
        self._records.append(timer.get_record())

        # 检查内存告警
        if self.log_memory:
            is_alert, alert_msg = self.memory_monitor.check_memory_alert()
            if is_alert:
                logger.warning(f"[性能告警] {alert_msg}")

    def add_record(self, record: PerformanceRecord) -> None:
        """添加性能记录"""
        self._records.append(record)

    def get_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要

        Returns:
            性能摘要字典
        """
        if not self._records:
            return {"message": "无性能记录"}

        total_duration = sum(r.duration_seconds for r in self._records)
        successful_steps = sum(1 for r in self._records if r.success)
        failed_steps = len(self._records) - successful_steps

        memory_deltas = [r.memory_delta_mb for r in self._records]
        peak_memory = max(r.memory_peak_mb for r in self._records)

        return {
            "session_id": self._session_id,
            "session_start": datetime.fromtimestamp(self._session_start).isoformat(),
            "session_duration_seconds": round(time.time() - self._session_start, 3),
            "total_step_duration_seconds": round(total_duration, 3),
            "total_steps": len(self._records),
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "peak_memory_mb": round(peak_memory, 2),
            "total_memory_delta_mb": round(sum(memory_deltas), 2),
            "steps": [r.to_dict() for r in self._records],
        }

    def save_report(self, filename: Optional[str] = None) -> str:
        """
        保存性能报告

        Args:
            filename: 报告文件名（不含路径）

        Returns:
            报告文件路径
        """
        if filename is None:
            filename = f"performance_{self._session_id}.json"

        report_path = self.output_dir / filename

        summary = self.get_summary()

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"性能报告已保存: {report_path}")
        return str(report_path)

    def clear_records(self) -> None:
        """清除所有记录"""
        self._records.clear()


# 全局性能记录器实例
_global_logger: Optional[PerformanceLogger] = None


def get_performance_logger(
    output_dir: str = "logs/performance",
    enable_monitoring: bool = True,
    **kwargs,
) -> PerformanceLogger:
    """
    获取全局性能记录器实例

    Args:
        output_dir: 输出目录
        enable_monitoring: 是否启用监控
        **kwargs: 其他参数

    Returns:
        PerformanceLogger 实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = PerformanceLogger(
            output_dir=output_dir, enable_monitoring=enable_monitoring, **kwargs
        )
    return _global_logger


def reset_performance_logger() -> None:
    """重置全局性能记录器"""
    global _global_logger
    _global_logger = None


@contextmanager
def track_performance(
    step_name: str, metadata: Optional[Dict[str, Any]] = None
) -> "AnalysisTimer":
    """
    跟踪性能的便捷上下文管理器

    Args:
        step_name: 步骤名称
        metadata: 额外元数据

    Yields:
        AnalysisTimer 实例
    """
    perf_logger = get_performance_logger()
    with perf_logger.track_step(step_name, metadata) as timer:
        yield timer


def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息

    Returns:
        系统信息字典
    """
    try:
        cpu_count = os.cpu_count() or 1
        mem = psutil.virtual_memory()

        return {
            "cpu_count": cpu_count,
            "memory_total_gb": round(mem.total / (1024**3), 2),
            "memory_available_gb": round(mem.available / (1024**3), 2),
            "memory_used_percent": mem.percent,
            "platform": os.name,
            "python_version": str(psutil.sys.version_info),
        }
    except Exception as e:
        logger.warning(f"获取系统信息失败: {e}")
        return {"error": str(e)}


def format_duration(seconds: float) -> str:
    """
    格式化时长

    Args:
        seconds: 秒数

    Returns:
        格式化的时长字符串
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_memory(mb: float) -> str:
    """
    格式化内存大小

    Args:
        mb: MB数

    Returns:
        格式化的内存字符串
    """
    if mb < 1024:
        return f"{mb:.2f}MB"
    else:
        gb = mb / 1024
        return f"{gb:.2f}GB"


# 装饰器：自动跟踪函数性能
def monitor_performance(step_name: Optional[str] = None):
    """
    性能监控装饰器

    Args:
        step_name: 步骤名称（默认使用函数名）

    Example:
        @monitor_performance("数据加载")
        def load_data(path):
            ...
    """

    def decorator(func: Callable) -> Callable:
        name = step_name or func.__name__

        def wrapper(*args, **kwargs):
            perf_logger = get_performance_logger()
            with perf_logger.track_step(name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
