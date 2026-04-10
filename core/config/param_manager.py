# =============================================================================
# 参数管理器 - 统一管理所有分析参数
# 负责加载、验证、保存参数
# =============================================================================

import os
import yaml
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from core.config.parameter_schema import PARAMETER_SCHEMAS, get_default_value


class ParameterManager:
    """
    参数管理器 - 单例模式
    统一管理所有模块的参数配置
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._config_path = self._get_config_path()
        self._defaults: Dict[str, Any] = {}
        self._load_config()
    
    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        # 项目根目录的config.yaml
        root = Path(__file__).parent.parent.parent
        return str(root / "config.yaml")
    
    def _load_config(self) -> None:
        """从配置文件加载参数"""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self._config = {}
        self._defaults = self._config.copy()
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self._load_config()
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        获取参数值
        path: 点分隔的参数路径，如 "qc.cell_filter.min_genes"
        default: 默认值（仅当配置文件中不存在时使用）
        """
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                # 参数不存在时，从默认schema中获取
                default_from_schema = self._get_default_from_schema(path)
                if default_from_schema is not None:
                    return default_from_schema
                return default
        
        return value
    
    def _get_default_from_schema(self, path: str) -> Any:
        """从schema中获取默认值"""
        keys = path.split('.')
        schema = PARAMETER_SCHEMAS
        
        for key in keys:
            if isinstance(schema, dict) and 'children' in schema:
                schema = schema['children']
                if key in schema:
                    schema = schema[key]
                else:
                    return None
            else:
                return None
        
        if isinstance(schema, dict):
            return schema.get('default')
        return None
    
    def set(self, path: str, value: Any) -> None:
        """
        设置参数值
        path: 点分隔的参数路径
        value: 参数值
        """
        keys = path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取整个配置节"""
        return self._config.get(section, {})
    
    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """设置整个配置节"""
        self._config[section] = values
    
    def save(self, path: Optional[str] = None) -> None:
        """
        保存配置到文件
        path: 保存路径，默认使用原始配置文件路径
        """
        save_path = path or self._config_path
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            raise
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def reset(self, path: Optional[str] = None) -> None:
        """
        重置参数为默认值
        path: 可选，指定要重置的参数路径
        """
        if path is None:
            # 重置所有
            self._config = self._defaults.copy()
        else:
            # 重置特定参数
            default_value = self._get_default_from_schema(path)
            if default_value is not None:
                self.set(path, default_value)
    
    def validate(self, path: str, value: Any) -> tuple[bool, Optional[str]]:
        """
        验证参数值是否合法
        返回: (是否有效, 错误消息)
        """
        schema_info = self._get_schema_info(path)
        if not schema_info:
            return True, None
        
        schema = schema_info.get('schema', {})
        param_type = schema.get('type')
        
        # 类型检查
        if param_type == 'int':
            if not isinstance(value, int):
                return False, f"参数 {path} 应该是整数"
            if 'min' in schema and value < schema['min']:
                return False, f"参数 {path} 不能小于 {schema['min']}"
            if 'max' in schema and value > schema['max']:
                return False, f"参数 {path} 不能大于 {schema['max']}"
        
        elif param_type == 'float':
            if not isinstance(value, (int, float)):
                return False, f"参数 {path} 应该是数字"
            if 'min' in schema and value < schema['min']:
                return False, f"参数 {path} 不能小于 {schema['min']}"
            if 'max' in schema and value > schema['max']:
                return False, f"参数 {path} 不能大于 {schema['max']}"
        
        elif param_type == 'bool':
            if not isinstance(value, bool):
                return False, f"参数 {path} 应该是布尔值"
        
        elif param_type == 'str':
            if not isinstance(value, str):
                return False, f"参数 {path} 应该是字符串"
        
        return True, None
    
    def _get_schema_info(self, path: str) -> Optional[Dict[str, Any]]:
        """获取参数路径对应的schema信息"""
        keys = path.split('.')
        schema = PARAMETER_SCHEMAS
        
        for key in keys:
            if isinstance(schema, dict) and 'children' in schema:
                schema = schema['children']
                if key in schema:
                    schema = schema[key]
                else:
                    return None
            else:
                return None
        
        return {'schema': schema, 'path': path}
    
    def get_section_params(self, section: str) -> List[Dict[str, Any]]:
        """
        获取某个配置节下的所有参数信息
        返回: 参数信息列表，每项包含 path, display_name, type, default, value
        """
        section_schema = PARAMETER_SCHEMAS.get(section, {})
        children = section_schema.get('children', {})
        params = []
        
        def collect_params(schema: Dict, prefix: str = ""):
            for key, info in schema.items():
                if 'children' in info:
                    # 嵌套结构
                    new_prefix = f"{prefix}{key}." if prefix else f"{prefix}{key}."
                    collect_params(info['children'], new_prefix)
                else:
                    path = f"{prefix}{key}"
                    params.append({
                        'path': path,
                        'display_name': info.get('display_name', key),
                        'type': info.get('type', 'str'),
                        'default': info.get('default'),
                        'value': self.get(path, info.get('default')),
                        'description': info.get('description', ''),
                        'options': info.get('options'),  # for select/multiselect
                        'min': info.get('min'),
                        'max': info.get('max'),
                    })
        
        collect_params(children)
        return params


# 全局单例
_param_manager: Optional[ParameterManager] = None


def get_param_manager() -> ParameterManager:
    """获取全局参数管理器实例"""
    global _param_manager
    if _param_manager is None:
        _param_manager = ParameterManager()
    return _param_manager


def get(section: str, key: str = None, default: Any = None) -> Any:
    """
    便捷函数：获取参数
    get("qc.cell_filter.min_genes")
    get("qc")  # 获取整个qc节
    """
    pm = get_param_manager()
    if key is None:
        return pm.get_section(section)
    return pm.get(f"{section}.{key}", default)


def set(section: str, key: str, value: Any) -> None:
    """便捷函数：设置参数"""
    pm = get_param_manager()
    pm.set(f"{section}.{key}", value)


def save() -> None:
    """便捷函数：保存参数"""
    pm = get_param_manager()
    pm.save()