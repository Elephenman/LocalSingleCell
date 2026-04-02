import matplotlib.pyplot as plt
import seaborn as sns
import plotly.io as pio
import plotly.graph_objects as go
import os
import platform


def setup_chinese_font():
    """
    配置中文字体
    """
    # 获取系统类型
    system = platform.system()
    
    # 根据系统选择字体
    if system == 'Windows':
        font_family = 'SimHei'  # 微软雅黑
    elif system == 'Darwin':
        font_family = 'PingFang SC'  # 苹方
    elif system == 'Linux':
        font_family = 'WenQuanYi Micro Hei'  # 文泉驿微米黑
    else:
        font_family = 'SimHei'
    
    # 配置matplotlib
    plt.rcParams['font.sans-serif'] = [font_family]
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    # 配置seaborn
    sns.set(font=font_family)
    
    # 配置plotly
    pio.templates.default = 'plotly_white'
    
    print(f"已配置中文字体: {font_family}")


def get_color_palette(n_colors, palette='viridis'):
    """
    获取颜色 palette
    
    Args:
        n_colors: 颜色数量
        palette: 调色板名称
    
    Returns:
        list: 颜色列表
    """
    return sns.color_palette(palette, n_colors).as_hex()


def create_heatmap(data, xlabels, ylabels, title=''):
    """
    创建热图
    
    Args:
        data: 数据矩阵
        xlabels: x轴标签
        ylabels: y轴标签
        title: 标题
    
    Returns:
        plotly Figure对象
    """
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=xlabels,
        y=ylabels,
        colorscale='Viridis',
        colorbar=dict(title='表达量')
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='基因',
        yaxis_title='聚类',
        xaxis_tickangle=-45
    )
    
    return fig