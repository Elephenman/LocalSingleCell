"""
配置工具模块

提供配置文件的加载、保存、更新和验证功能。
"""

import yaml
import os
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path

from utils.exceptions import ConfigurationError, InvalidConfigError, MissingConfigKeyError


# ============================================================
# 默认配置值
# ============================================================

DEFAULT_CONFIG = {
    'random_seed': 42,
    'qc': {
        'gene_filter': {
            'apply': True,
            'min_cells': 3
        },
        'cell_filter': {
            'min_genes': 200,
            'max_genes': 6000,
            'min_umi': 500,
            'max_umi': 20000
        },
        'mitochondrial': {
            'apply': True,
            'prefix': 'MT-',
            'max_percent': 20
        },
        'ribosomal': {
            'apply': False,
            'prefix': 'RP[SL]',
            'max_percent': 50
        }
    },
    'normalization': {
        'method': 'scanpy',
        'target_sum': 1e4,
        'hvg': {
            'apply': True,
            'n_top_genes': 2000,
            'method': 'seurat_v3'
        },
        'scaling': {
            'apply': True,
            'max_value': 10
        }
    },
    'dimension_reduction': {
        'pca': {
            'n_comps': 50,
            'use_hvg': True
        },
        'umap': {
            'apply': True,
            'n_neighbors': 15,
            'min_dist': 0.5
        },
        'tsne': {
            'apply': False,
            'perplexity': 30
        }
    },
    'clustering': {
        'n_pcs': 30,
        'n_neighbors': 15,
        'resolution': 0.5
    },
    'differential': {
        'apply': True,
        'method': 'wilcoxon',
        'min_pct': 0.25
    }
}

# 必需的配置键
REQUIRED_KEYS = [
    'random_seed',
    'qc',
    'normalization',
    'dimension_reduction',
    'clustering'
]

# 参数范围定义
PARAMETER_RANGES = {
    ('random_seed',): {'type': int, 'min': 0},
    ('qc', 'gene_filter', 'min_cells'): {'type': int, 'min': 0},
    ('qc', 'cell_filter', 'min_genes'): {'type': int, 'min': 0, 'max': 100000},
    ('qc', 'cell_filter', 'max_genes'): {'type': int, 'min': 0, 'max': 100000},
    ('qc', 'mitochondrial', 'max_percent'): {'type': (int, float), 'min': 0, 'max': 100},
    ('normalization', 'target_sum'): {'type': (int, float), 'min': 0},
    ('normalization', 'hvg', 'n_top_genes'): {'type': int, 'min': 100, 'max': 10000},
    ('dimension_reduction', 'pca', 'n_comps'): {'type': int, 'min': 5, 'max': 100},
    ('dimension_reduction', 'umap', 'n_neighbors'): {'type': int, 'min': 2, 'max': 100},
    ('dimension_reduction', 'umap', 'min_dist'): {'type': (int, float), 'min': 0, 'max': 1},
    ('clustering', 'n_pcs'): {'type': int, 'min': 5, 'max': 100},
    ('clustering', 'n_neighbors'): {'type': int, 'min': 2, 'max': 100},
    ('clustering', 'resolution'): {'type': (int, float), 'min': 0.1, 'max': 5.0},
}


# ============================================================
# 配置加载函数
# ============================================================

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径，默认为当前目录的config.yaml

    Returns:
        dict: 配置参数字典

    Raises:
        ConfigurationError: 配置加载失败
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config.yaml'
        )

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 验证配置
            is_valid, errors = validate_config(config)
            if not is_valid:
                # 尝试填充默认值
                config = fill_missing_defaults(config)
                # 重新验证
                is_valid, errors = validate_config(config)
                if not is_valid:
                    raise InvalidConfigError(
                        message=f"配置验证失败: {'; '.join(errors)}",
                        details=errors
                    )

            return config
        else:
            # 配置文件不存在，返回默认配置
            return DEFAULT_CONFIG.copy()

    except yaml.YAMLError as e:
        raise ConfigurationError(
            message=f"配置文件格式错误: {str(e)}",
            error_code="E302",
            details=e
        )
    except Exception as e:
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError(
            message=f"加载配置文件失败: {str(e)}",
            details=e
        )


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    保存配置文件

    Args:
        config: 配置参数字典
        config_path: 配置文件路径，默认为当前目录的config.yaml

    Raises:
        ConfigurationError: 配置保存失败
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config.yaml'
        )

    try:
        # 保存前验证
        is_valid, errors = validate_config(config)
        if not is_valid:
            raise InvalidConfigError(
                message=f"配置验证失败: {'; '.join(errors)}",
                details=errors
            )

        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    except Exception as e:
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError(
            message=f"保存配置文件失败: {str(e)}",
            details=e
        )


# ============================================================
# 配置更新函数
# ============================================================

def update_config(
    config: Dict[str, Any],
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    更新配置参数

    Args:
        config: 原始配置参数字典
        updates: 要更新的参数字典

    Returns:
        dict: 更新后的配置参数字典
    """
    def _update_recursive(target: dict, source: dict) -> None:
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                _update_recursive(target[key], value)
            else:
                target[key] = value

    # 深拷贝配置
    import copy
    updated_config = copy.deepcopy(config)
    _update_recursive(updated_config, updates)

    return updated_config


def fill_missing_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    填充缺失的默认配置值

    Args:
        config: 原始配置

    Returns:
        填充后的配置
    """
    def _fill_recursive(target: dict, defaults: dict) -> None:
        for key, default_value in defaults.items():
            if key not in target:
                target[key] = default_value
            elif isinstance(default_value, dict) and isinstance(target.get(key), dict):
                _fill_recursive(target[key], default_value)

    import copy
    result = copy.deepcopy(config)
    _fill_recursive(result, DEFAULT_CONFIG)

    return result


# ============================================================
# 配置验证函数
# ============================================================

def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证配置文件

    Args:
        config: 配置参数字典

    Returns:
        (is_valid, error_messages): 验证结果和错误消息列表
    """
    errors = []

    # 1. 检查必需键
    for key in REQUIRED_KEYS:
        if key not in config:
            errors.append(f"缺少必需配置项: {key}")

    # 2. 检查参数类型和范围
    for path, constraints in PARAMETER_RANGES.items():
        value = get_nested_value(config, path)

        if value is not None:
            # 类型检查
            expected_type = constraints.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f"配置项 {'.'.join(map(str, path))} 类型错误: "
                    f"期望 {expected_type.__name__}, 实际 {type(value).__name__}"
                )
                continue

            # 范围检查
            min_val = constraints.get('min')
            max_val = constraints.get('max')

            if min_val is not None and value < min_val:
                errors.append(
                    f"配置项 {'.'.join(map(str, path))} 值 {value} 小于最小值 {min_val}"
                )

            if max_val is not None and value > max_val:
                errors.append(
                    f"配置项 {'.'.join(map(str, path))} 值 {value} 大于最大值 {max_val}"
                )

    # 3. 检查逻辑一致性
    logical_errors = validate_logical_consistency(config)
    errors.extend(logical_errors)

    return len(errors) == 0, errors


def validate_logical_consistency(config: Dict[str, Any]) -> List[str]:
    """
    验证配置的逻辑一致性

    Args:
        config: 配置参数字典

    Returns:
        错误消息列表
    """
    errors = []

    # 检查 min_genes <= max_genes
    try:
        cell_filter = config.get('qc', {}).get('cell_filter', {})
        min_genes = cell_filter.get('min_genes', 0)
        max_genes = cell_filter.get('max_genes', float('inf'))
        if min_genes > max_genes:
            errors.append(
                f"最小基因数 ({min_genes}) 不能大于最大基因数 ({max_genes})"
            )

        min_umi = cell_filter.get('min_umi', 0)
        max_umi = cell_filter.get('max_umi', float('inf'))
        if min_umi > max_umi:
            errors.append(
                f"最小UMI数 ({min_umi}) 不能大于最大UMI数 ({max_umi})"
            )
    except Exception:
        pass

    # 检查 PCA 主成分数
    try:
        pca_comps = config.get('dimension_reduction', {}).get('pca', {}).get('n_comps', 50)
        clustering_pcs = config.get('clustering', {}).get('n_pcs', 30)
        if clustering_pcs > pca_comps:
            errors.append(
                f"聚类使用的PCA主成分数 ({clustering_pcs}) 不能大于PCA计算的主成分数 ({pca_comps})"
            )
    except Exception:
        pass

    return errors


def get_nested_value(config: Dict[str, Any], path: Tuple[str, ...]) -> Any:
    """
    获取嵌套配置值

    Args:
        config: 配置字典
        path: 配置路径元组

    Returns:
        配置值，如果不存在返回 None
    """
    value = config
    for key in path:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def set_nested_value(config: Dict[str, Any], path: Tuple[str, ...], value: Any) -> None:
    """
    设置嵌套配置值

    Args:
        config: 配置字典
        path: 配置路径元组
        value: 要设置的值
    """
    target = config
    for key in path[:-1]:
        if key not in target:
            target[key] = {}
        target = target[key]
    target[path[-1]] = value


# ============================================================
# 配置辅助函数
# ============================================================

def get_config_value(config: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    获取配置值（支持默认值）

    Args:
        config: 配置字典
        *keys: 配置键路径
        default: 默认值

    Returns:
        配置值或默认值
    """
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个配置（后面的配置覆盖前面的）

    Args:
        *configs: 配置字典列表

    Returns:
        合并后的配置
    """
    result = {}

    for config in configs:
        result = update_config(result, config)

    return result


def config_to_flat_dict(config: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    将嵌套配置转换为扁平字典

    Args:
        config: 嵌套配置字典
        parent_key: 父键前缀
        sep: 键分隔符

    Returns:
        扁平字典
    """
    items = []

    for key, value in config.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(config_to_flat_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def flat_dict_to_config(flat_dict: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    将扁平字典转换为嵌套配置

    Args:
        flat_dict: 扁平字典
        sep: 键分隔符

    Returns:
        嵌套配置字典
    """
    result = {}

    for key, value in flat_dict.items():
        keys = key.split(sep)
        target = result

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value

    return result
