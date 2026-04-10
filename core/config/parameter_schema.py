# =============================================================================
# 参数定义 Schema - 从 config.yaml 自动提取的参数定义
# 用于UI组件自动生成和参数验证
# =============================================================================

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
import yaml
import os

# 参数Schema定义 - 基于config.yaml的参数结构
PARAMETER_SCHEMAS: Dict[str, Dict[str, Any]] = {
    # === 性能优化配置 ===
    "performance": {
        "display_name": "性能优化",
        "description": "性能相关参数配置",
        "children": {
            "auto_downsample": {
                "display_name": "自动降采样",
                "description": "数据量过大时自动降采样",
                "children": {
                    "enabled": {"type": "bool", "default": True, "display_name": "启用自动降采样"},
                    "max_cells": {"type": "int", "default": 10000, "display_name": "最大细胞数", "min": 1000, "max": 100000},
                    "max_genes": {"type": "int", "default": 20000, "display_name": "最大基因数", "min": 1000, "max": 50000},
                    "suggest_only": {"type": "bool", "default": False, "display_name": "仅提示不执行"},
                }
            },
            "memory": {
                "display_name": "内存优化",
                "description": "内存管理相关设置",
                "children": {
                    "gc_threshold_percent": {"type": "int", "default": 80, "display_name": "GC阈值(%)", "min": 50, "max": 95},
                    "enable_cache": {"type": "bool", "default": True, "display_name": "启用缓存"},
                    "cache_dir": {"type": "str", "default": "temp/cache", "display_name": "缓存目录"},
                }
            },
            "parallel": {
                "display_name": "并行处理",
                "description": "多核并行计算设置",
                "children": {
                    "enabled": {"type": "bool", "default": True, "display_name": "启用并行"},
                    "n_jobs": {"type": "int", "default": -1, "display_name": "CPU核心数", "min": -1, "max": 32},
                }
            },
            "monitoring": {
                "display_name": "性能监控",
                "description": "运行时性能监控",
                "children": {
                    "enabled": {"type": "bool", "default": True, "display_name": "启用监控"},
                    "log_memory": {"type": "bool", "default": True, "display_name": "记录内存"},
                    "log_timing": {"type": "bool", "default": True, "display_name": "记录耗时"},
                }
            },
        }
    },
    
    # === 质控过滤参数 ===
    "qc": {
        "display_name": "质控过滤",
        "description": "质量控制与过滤参数",
        "children": {
            "gene_filter": {
                "display_name": "基因过滤",
                "description": "基因过滤条件",
                "children": {
                    "min_cells": {"type": "int", "default": 3, "display_name": "最小细胞数", "min": 1, "max": 20},
                    "apply": {"type": "bool", "default": True, "display_name": "启用"},
                }
            },
            "cell_filter": {
                "display_name": "细胞过滤",
                "description": "细胞过滤条件",
                "children": {
                    "min_genes": {"type": "int", "default": 200, "display_name": "最小基因数", "min": 50, "max": 1000},
                    "max_genes": {"type": "int", "default": 6000, "display_name": "最大基因数", "min": 1000, "max": 20000},
                    "min_umi": {"type": "int", "default": 500, "display_name": "最小UMI数", "min": 100, "max": 5000},
                    "max_umi": {"type": "int", "default": 20000, "display_name": "最大UMI数", "min": 5000, "max": 100000},
                }
            },
            "mitochondrial": {
                "display_name": "线粒体过滤",
                "description": "线粒体基因过滤",
                "children": {
                    "prefix": {"type": "str", "default": "MT-", "display_name": "基因前缀"},
                    "max_percent": {"type": "float", "default": 20.0, "display_name": "最大占比(%)", "min": 0, "max": 100},
                    "apply": {"type": "bool", "default": True, "display_name": "启用"},
                }
            },
            "ribosomal": {
                "display_name": "核糖体过滤",
                "description": "核糖体基因过滤",
                "children": {
                    "prefix": {"type": "str", "default": "RP[SL]", "display_name": "基因前缀"},
                    "max_percent": {"type": "float", "default": 50.0, "display_name": "最大占比(%)", "min": 0, "max": 100},
                    "apply": {"type": "bool", "default": False, "display_name": "启用"},
                }
            },
        }
    },
    
    # === 归一化参数 ===
    "normalization": {
        "display_name": "归一化",
        "description": "数据归一化与高变基因筛选",
        "children": {
            "method": {"type": "select", "default": "scanpy", "display_name": "归一化方法", 
                      "options": ["scanpy", "log1p", "clr"]},
            "target_sum": {"type": "int", "default": 10000, "display_name": "目标UMI总和", "min": 1000, "max": 50000},
            "hvg": {
                "display_name": "高变基因",
                "description": "高变基因筛选",
                "children": {
                    "apply": {"type": "bool", "default": True, "display_name": "启用"},
                    "method": {"type": "select", "default": "seurat_v3", "display_name": "筛选方法",
                              "options": ["seurat_v3", "seurat", "cell_ranger", "mean_var"]},
                    "n_top_genes": {"type": "int", "default": 2000, "display_name": "高变基因数", "min": 500, "max": 5000},
                }
            },
            "scaling": {
                "display_name": "缩放",
                "description": "数据缩放",
                "children": {
                    "apply": {"type": "bool", "default": True, "display_name": "启用"},
                    "max_value": {"type": "float", "default": 10.0, "display_name": "最大值", "min": 5, "max": 50},
                }
            },
        }
    },
    
    # === 降维参数 ===
    "dimension_reduction": {
        "display_name": "降维",
        "description": "PCA/UMAP/t-SNE降维参数",
        "children": {
            "pca": {
                "display_name": "PCA",
                "description": "主成分分析",
                "children": {
                    "n_comps": {"type": "int", "default": 50, "display_name": "主成分数", "min": 10, "max": 100},
                    "use_hvg": {"type": "bool", "default": True, "display_name": "仅用高变基因"},
                }
            },
            "umap": {
                "display_name": "UMAP",
                "description": "UMAP降维",
                "children": {
                    "apply": {"type": "bool", "default": True, "display_name": "启用"},
                    "n_neighbors": {"type": "int", "default": 15, "display_name": "邻居数", "min": 5, "max": 100},
                    "min_dist": {"type": "float", "default": 0.5, "display_name": "最小距离", "min": 0.0, "max": 1.0},
                }
            },
            "tsne": {
                "display_name": "t-SNE",
                "description": "t-SNE降维",
                "children": {
                    "apply": {"type": "bool", "default": False, "display_name": "启用"},
                    "perplexity": {"type": "int", "default": 30, "display_name": "perplexity", "min": 5, "max": 100},
                }
            },
        }
    },
    
    # === 聚类参数 ===
    "clustering": {
        "display_name": "聚类",
        "description": "细胞聚类参数",
        "children": {
            "n_pcs": {"type": "int", "default": 30, "display_name": "使用主成分数", "min": 5, "max": 50},
            "n_neighbors": {"type": "int", "default": 15, "display_name": "邻居数", "min": 5, "max": 100},
            "method": {"type": "select", "default": "leiden", "display_name": "聚类方法",
                      "options": ["leiden", "louvain", "kmeans"]},
            "resolution": {"type": "float", "default": 0.5, "display_name": "聚类分辨率", "min": 0.1, "max": 2.0},
        }
    },
    
    # === 差异分析参数 ===
    "differential": {
        "display_name": "差异分析",
        "description": "差异基因分析参数",
        "children": {
            "apply": {"type": "bool", "default": True, "display_name": "启用"},
            "method": {"type": "select", "default": "wilcoxon", "display_name": "统计方法",
                      "options": ["wilcoxon", "t-test", "logreg"]},
            "p_adjust_cutoff": {"type": "float", "default": 0.05, "display_name": "p值阈值", "min": 0.001, "max": 0.1},
            "log2fc_min": {"type": "float", "default": 0.25, "display_name": "最小log2FC", "min": 0.1, "max": 1.0},
            "min_pct": {"type": "float", "default": 0.25, "display_name": "最小表达比例", "min": 0.1, "max": 0.5},
        }
    },
    
    # === 富集分析参数 ===
    "enrichment": {
        "display_name": "富集分析",
        "description": "功能富集分析参数",
        "children": {
            "databases": {"type": "multiselect", "default": ["GO_BP", "KEGG"], "display_name": "数据库",
                         "options": ["GO_BP", "GO_MF", "GO_CC", "KEGG", "REACTOME"]},
            "p_adjust_cutoff": {"type": "float", "default": 0.05, "display_name": "p值阈值", "min": 0.001, "max": 0.1},
            "min_gene_count": {"type": "int", "default": 3, "display_name": "最小基因数", "min": 1, "max": 10},
            "top_terms": {"type": "int", "default": 10, "display_name": "显示条目数", "min": 5, "max": 20},
        }
    },
    
    # === 可视化参数 ===
    "visualization": {
        "display_name": "可视化",
        "description": "图表可视化参数",
        "children": {
            "dpi": {"type": "int", "default": 300, "display_name": "DPI", "min": 72, "max": 600},
            "figsize": {"type": "float_list", "default": [10, 8], "display_name": "图形尺寸"},
            "color_palette": {"type": "select", "default": "viridis", "display_name": "配色方案",
                             "options": ["viridis", "plasma", "inferno", "magma", "Spectral", "RdBu"]},
            "font_size": {"type": "int", "default": 12, "display_name": "字体大小", "min": 8, "max": 24},
            "format": {"type": "select", "default": "png", "display_name": "输出格式",
                      "options": ["png", "pdf", "svg"]},
        }
    },
    
    # === 空间转录组参数 ===
    "spatial": {
        "display_name": "空间转录组",
        "description": "空间数据分析参数",
        "children": {
            "apply": {"type": "bool", "default": True, "display_name": "启用"},
            "coord_type": {"type": "select", "default": "grid", "display_name": "坐标类型",
                          "options": ["grid", "spatial", "generic"]},
            "n_rings": {"type": "int", "default": 1, "display_name": "环形数", "min": 1, "max": 5},
            "visualization": {
                "display_name": "可视化",
                "description": "空间可视化设置",
                "children": {
                    "spot_size": {"type": "float", "default": None, "display_name": "点大小", "min": 0.5, "max": 10},
                    "alpha": {"type": "float", "default": 1.0, "display_name": "透明度", "min": 0.1, "max": 1.0},
                    "img_alpha": {"type": "float", "default": 0.5, "display_name": "背景图透明度", "min": 0.0, "max": 1.0},
                }
            },
        }
    },
}


def get_all_params() -> Dict[str, Any]:
    """
    从config.yaml加载所有参数
    用于获取当前的参数默认值
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"警告: 无法加载config.yaml: {e}")
        return {}


def get_default_value(path: str) -> Any:
    """
    根据参数路径获取默认值
    path形如: "qc.cell_filter.min_genes"
    """
    config = get_all_params()
    keys = path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def get_schema(path: str) -> Optional[Dict[str, Any]]:
    """
    根据参数路径获取Schema定义
    path形如: "qc.cell_filter"
    """
    keys = path.split('.')
    schema = PARAMETER_SCHEMAS
    for key in keys:
        if isinstance(schema, dict) and key in schema:
            schema = schema[key]
        else:
            return None
    return schema if isinstance(schema, dict) else None