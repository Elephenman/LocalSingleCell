import yaml
import os


def load_config(config_path=None):
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，默认为当前目录的config.yaml
    
    Returns:
        dict: 配置参数字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise Exception(f"加载配置文件失败: {str(e)}")


def save_config(config, config_path=None):
    """
    保存配置文件
    
    Args:
        config: 配置参数字典
        config_path: 配置文件路径，默认为当前目录的config.yaml
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise Exception(f"保存配置文件失败: {str(e)}")


def update_config(config, updates):
    """
    更新配置参数
    
    Args:
        config: 原始配置参数字典
        updates: 要更新的参数字典
    
    Returns:
        dict: 更新后的配置参数字典
    """
    def _update_recursive(config, updates):
        for key, value in updates.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                _update_recursive(config[key], value)
            else:
                config[key] = value
    
    updated_config = config.copy()
    _update_recursive(updated_config, updates)
    return updated_config