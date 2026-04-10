# =============================================================================
# 参数编辑器组件 - 根据Schema自动生成Streamlit UI
# =============================================================================

import streamlit as st
from typing import Any, Callable, Dict, List, Optional, Union
from core.config.parameter_schema import PARAMETER_SCHEMAS
from core.config.param_manager import ParameterManager, get_param_manager


class ParameterEditor:
    """
    参数编辑器 - 根据Schema自动生成Streamlit UI组件
    支持多种类型的参数输入：bool, int, float, str, select, multiselect, float_list
    """
    
    def __init__(self, param_manager: Optional[ParameterManager] = None):
        """
        初始化参数编辑器
        param_manager: 参数管理器实例，默认使用全局实例
        """
        self.pm = param_manager or get_param_manager()
        self.changed = False
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """获取嵌套字典中的值"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _render_bool(self, path: str, schema: Dict) -> bool:
        """渲染布尔类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', False))
        
        value = st.checkbox(
            label,
            value=default,
            help=help_text,
            key=f"param_{path}"
        )
        return value
    
    def _render_int(self, path: str, schema: Dict) -> int:
        """渲染整数类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', 0))
        min_val = schema.get('min')
        max_val = schema.get('max')
        
        if min_val is not None and max_val is not None:
            value = st.number_input(
                label,
                min_value=min_val,
                max_value=max_val,
                value=default,
                step=1,
                help=help_text,
                key=f"param_{path}"
            )
        else:
            value = st.number_input(
                label,
                value=default,
                step=1,
                help=help_text,
                key=f"param_{path}"
            )
        return int(value)
    
    def _render_float(self, path: str, schema: Dict) -> float:
        """渲染浮点数类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', 0.0))
        min_val = schema.get('min')
        max_val = schema.get('max')
        
        # 计算合适的步长
        step = 0.1
        if min_val is not None and max_val is not None:
            if max_val - min_val > 10:
                step = 1.0
            elif max_val - min_val > 1:
                step = 0.1
            else:
                step = 0.01
        
        value = st.number_input(
            label,
            min_value=float(min_val) if min_val is not None else None,
            max_value=float(max_val) if max_val is not None else None,
            value=float(default),
            step=step,
            help=help_text,
            key=f"param_{path}"
        )
        return float(value)
    
    def _render_float_list(self, path: str, schema: Dict) -> List[float]:
        """渲染浮点数列表类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', [10, 8]))
        
        col1, col2 = st.columns(2)
        with col1:
            val1 = st.number_input(
                f"{label} (宽)",
                value=float(default[0]) if default and len(default) > 0 else 10.0,
                step=1.0,
                key=f"param_{path}_0"
            )
        with col2:
            val2 = st.number_input(
                f"{label} (高)",
                value=float(default[1]) if default and len(default) > 1 else 8.0,
                step=1.0,
                key=f"param_{path}_1"
            )
        return [val1, val2]
    
    def _render_str(self, path: str, schema: Dict) -> str:
        """渲染字符串类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', ''))
        
        value = st.text_input(
            label,
            value=str(default),
            help=help_text,
            key=f"param_{path}"
        )
        return value
    
    def _render_select(self, path: str, schema: Dict) -> str:
        """渲染单选类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', ''))
        options = schema.get('options', [])
        
        if not options:
            return default
        
        # 找到default在options中的索引
        try:
            index = options.index(default) if default in options else 0
        except (ValueError, TypeError):
            index = 0
        
        value = st.selectbox(
            label,
            options=options,
            index=index,
            help=help_text,
            key=f"param_{path}"
        )
        return value
    
    def _render_multiselect(self, path: str, schema: Dict) -> List[str]:
        """渲染多选类型参数"""
        label = schema.get('display_name', path.split('.')[-1])
        help_text = schema.get('description', '')
        default = self.pm.get(path, schema.get('default', []))
        options = schema.get('options', [])
        
        if not options:
            return default if isinstance(default, list) else [default] if default else []
        
        # 确保default是列表
        if not isinstance(default, list):
            default = [default] if default else []
        
        value = st.multiselect(
            label,
            options=options,
            default=default,
            help=help_text,
            key=f"param_{path}"
        )
        return value
    
    def _render_param(self, path: str, schema: Dict) -> Any:
        """根据类型渲染参数组件"""
        param_type = schema.get('type', 'str')
        
        if param_type == 'bool':
            return self._render_bool(path, schema)
        elif param_type == 'int':
            return self._render_int(path, schema)
        elif param_type == 'float':
            return self._render_float(path, schema)
        elif param_type == 'float_list':
            return self._render_float_list(path, schema)
        elif param_type == 'str':
            return self._render_str(path, schema)
        elif param_type == 'select':
            return self._render_select(path, schema)
        elif param_type == 'multiselect':
            return self._render_multiselect(path, schema)
        else:
            return self._render_str(path, schema)
    
    def render_section(self, section: str) -> Dict[str, Any]:
        """
        渲染整个配置节
        返回: 所有参数的新值字典
        """
        section_schema = PARAMETER_SCHEMAS.get(section, {})
        children = section_schema.get('children', {})
        results = {}
        
        # 渲染配置节标题和描述
        st.subheader(section_schema.get('display_name', section))
        if section_schema.get('description'):
            st.caption(section_schema.get('description'))
        
        def render_children(schema: Dict, prefix: str = ""):
            for key, info in schema.items():
                if 'children' in info:
                    # 分组渲染
                    with st.expander(info.get('display_name', key), expanded=True):
                        render_children(info['children'], f"{prefix}{key}.")
                else:
                    # 渲染参数
                    path = f"{prefix}{key}"
                    value = self._render_param(path, info)
                    results[path] = value
        
        render_children(children)
        return results
    
    def render_all(self) -> Dict[str, Any]:
        """
        渲染所有配置节
        返回: 所有参数的新值字典
        """
        all_results = {}
        
        for section in PARAMETER_SCHEMAS.keys():
            results = self.render_section(section)
            all_results.update(results)
            st.markdown("---")
        
        return all_results
    
    def save_changes(self, changes: Dict[str, Any]) -> None:
        """
        保存参数变更
        changes: {path: value} 格式的字典
        """
        for path, value in changes.items():
            self.pm.set(path, value)
        self.pm.save()
    
    def create_form(self, sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        创建参数编辑表单
        sections: 要显示的配置节列表，None表示全部
        返回: 用户编辑后的参数字典
        """
        changes = {}
        section_list = sections or list(PARAMETER_SCHEMAS.keys())
        
        for section in section_list:
            if section in PARAMETER_SCHEMAS:
                section_changes = self.render_section(section)
                changes.update(section_changes)
        
        return changes


def render_param_editor(sections: Optional[List[str]] = None, 
                        key_prefix: str = "params") -> Dict[str, Any]:
    """
    便捷函数：渲染参数编辑器
    sections: 要显示的配置节，None表示全部
    返回: 参数变更字典
    """
    editor = ParameterEditor()
    
    # 创建form容器
    with st.form(key=f"{key_prefix}_form"):
        changes = editor.create_form(sections)
        
        submitted = st.form_submit_button("💾 保存参数", type="primary")
        
        if submitted:
            editor.save_changes(changes)
            st.success("✅ 参数已保存！")
    
    return changes


# 示例用法
if __name__ == "__main__":
    # 测试代码
    st.set_page_config(page_title="参数编辑器测试", layout="wide")
    
    st.title("🧪 参数编辑器测试")
    
    changes = render_param_editor(["qc", "normalization", "clustering"])
    
    st.divider()
    st.subheader("当前参数值")
    st.json(changes)