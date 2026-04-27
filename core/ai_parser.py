import json
import re
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AIParser:
    """AI需求解析器，将自然语言需求转换为分析流程参数"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化AI解析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.ai_config = config.get('ai_analysis', {}) if config else {}
        
    def parse_requirement(self, user_input: str, data_type: str = 'single_cell') -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        解析用户自然语言需求
        
        Args:
            user_input: 用户输入的自然语言需求
            data_type: 数据类型 ('single_cell' 或 'spatial')
            
        Returns:
            Tuple[分析参数字典, 图表选择字典]
        """
        logger.info(f"开始解析用户需求: {user_input}")
        
        # 初始化默认参数
        pipeline_config = self._get_default_pipeline_config(data_type)
        visualization_config = self._get_default_visualization_config(data_type)
        
        # 解析关键参数
        pipeline_config = self._extract_qc_parameters(user_input, pipeline_config)
        pipeline_config = self._extract_clustering_parameters(user_input, pipeline_config)
        pipeline_config = self._extract_dimension_reduction_parameters(user_input, pipeline_config)
        pipeline_config = self._extract_differential_expression_parameters(user_input, pipeline_config)
        
        # 解析富集分析需求
        enrichment_config = self._extract_enrichment_parameters(user_input)
        if enrichment_config:
            pipeline_config['enrichment'] = enrichment_config
        
        # 解析可视化需求
        visualization_config = self._extract_visualization_requirements(user_input, visualization_config)
        
        logger.info(f"解析完成，生成参数: {pipeline_config}")
        return pipeline_config, visualization_config
    
    def _get_default_pipeline_config(self, data_type: str) -> Dict[str, Any]:
        """获取默认的分析流程配置"""
        base_config = {
            'qc': {
                'filter_genes': True,
                'min_cells': 3,
                'min_genes': 200,
                'max_genes': 6000,
                'min_umi': 500,
                'max_umi': 20000,
                'filter_mito': True,
                'mito_prefix': 'MT-',
                'max_mito_ratio': 20,
                'filter_ribo': False,
                'ribo_prefix': 'RP[SL]',
                'max_ribo_ratio': 50
            },
            'normalization': {
                'method': 'scanpy',  # 与 config.yaml 保持一致（原为 'scanpy_standard'，已修正）
                'target_sum': 10000,
                'select_highly_variable': True,
                'highly_variable_method': 'seurat_v3',
                'highly_variable_genes': 2000,
                'scale_data': True,
                'max_value': 10
            },
            'dimension_reduction': {
                'n_pcs': 50,
                'use_highly_variable': True,
                'run_umap': True,
                'umap_n_neighbors': 15,
                'umap_min_dist': 0.5,
                'run_tsne': False,
                'tsne_perplexity': 30
            },
            'clustering': {
                'n_neighbors': 15,
                'n_pcs': 30,
                'algorithm': 'leiden',
                'resolution': 0.5
            },
            'differential': {  # 与 config.yaml 保持一致（原为 'differential_expression'，已修正）
                'apply': True,
                'method': 'wilcoxon',
                'p_adjust_cutoff': 0.05,
                'log2fc_cutoff': 0.25,
                'min_pct': 0.25
            }
        }
        
        if data_type == 'spatial':
            base_config['spatial'] = {
                'run_spatial_analysis': True,
                'find_spatial_variable_genes': True,
                'spatial_cluster': True
            }
        
        return base_config
    
    def _get_default_visualization_config(self, data_type: str) -> Dict[str, Any]:
        """获取默认的可视化配置"""
        viz_config = {
            'qc_viz': ['violin', 'scatter', 'histogram'],
            'dimred_viz': ['umap', 'cluster_bar'],
            'marker_viz': ['umap_gene', 'dotplot', 'violin', 'heatmap'],
            'de_viz': ['volcano', 'bar']
        }
        
        if data_type == 'spatial':
            viz_config['spatial_viz'] = ['spatial_gene', 'spatial_cluster', 'spatial_heatmap']
        
        return viz_config
    
    def _extract_qc_parameters(self, user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """提取质控参数"""
        user_input_lower = user_input.lower()
        
        # 提取线粒体比例
        mito_match = re.search(r'线粒体(?:比例)?超过?(\d+(?:\.\d+)?)%?', user_input)
        if mito_match:
            config['qc']['max_mito_ratio'] = float(mito_match.group(1))
            config['qc']['filter_mito'] = True
        
        # 提取最小基因数
        min_genes_match = re.search(r'最少?基因[数]?[为是]?(\d+)', user_input)
        if min_genes_match:
            config['qc']['min_genes'] = int(min_genes_match.group(1))
        
        # 提取最大基因数
        max_genes_match = re.search(r'最多?基因[数]?[为是]?(\d+)', user_input)
        if max_genes_match:
            config['qc']['max_genes'] = int(max_genes_match.group(1))
        
        return config
    
    def _extract_clustering_parameters(self, user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """提取聚类参数"""
        user_input_lower = user_input.lower()
        
        # 提取聚类分辨率
        resolution_match = re.search(r'分辨率[为是]?(\d+(?:\.\d+)?)', user_input)
        if resolution_match:
            config['clustering']['resolution'] = float(resolution_match.group(1))
        
        # 提取聚类算法
        if 'louvain' in user_input_lower:
            config['clustering']['algorithm'] = 'louvain'
        elif 'leiden' in user_input_lower:
            config['clustering']['algorithm'] = 'leiden'
        
        return config
    
    def _extract_dimension_reduction_parameters(self, user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """提取降维参数"""
        user_input_lower = user_input.lower()
        
        # tSNE
        if 'tsne' in user_input_lower or 't-sne' in user_input_lower:
            config['dimension_reduction']['run_tsne'] = True
        
        # PCA主成分数
        pca_match = re.search(r'pca[主成分]?[数]?[为是]?(\d+)', user_input, re.IGNORECASE)
        if pca_match:
            config['dimension_reduction']['n_pcs'] = int(pca_match.group(1))
            config['clustering']['n_pcs'] = int(pca_match.group(1))
        
        return config
    
    def _extract_differential_expression_parameters(self, user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """提取差异表达参数"""
        user_input_lower = user_input.lower()
        
        # 标记基因/差异基因
        if '标记基因' in user_input or '差异基因' in user_input:
            config['differential']['apply'] = True
        
        # p值阈值
        pvalue_match = re.search(r'p[-\s]?value[<≤]?(\d+(?:\.\d+)?)', user_input, re.IGNORECASE)
        if pvalue_match:
            config['differential']['p_adjust_cutoff'] = float(pvalue_match.group(1))
        
        # log2FC阈值
        fc_match = re.search(r'log2fc[≥>]?(\d+(?:\.\d+)?)', user_input, re.IGNORECASE)
        if fc_match:
            config['differential']['log2fc_cutoff'] = float(fc_match.group(1))
        
        return config
    
    def _extract_enrichment_parameters(self, user_input: str) -> Optional[Dict[str, Any]]:
        """提取富集分析参数"""
        user_input_lower = user_input.lower()
        
        enrichment_config = None
        
        # 检查是否需要富集分析
        if '富集分析' in user_input or 'go' in user_input_lower or 'kegg' in user_input_lower or 'reactome' in user_input_lower:
            enrichment_config = {
                'run_enrichment': True,
                'databases': [],
                'species': 'human',
                'p_adjust_cutoff': 0.05,
                'min_genes': 3
            }
            
            # 数据库选择
            if 'go' in user_input_lower or '基因本体' in user_input:
                enrichment_config['databases'].extend(['go_bp', 'go_cc', 'go_mf'])
            if 'kegg' in user_input_lower:
                enrichment_config['databases'].append('kegg')
            if 'reactome' in user_input_lower:
                enrichment_config['databases'].append('reactome')
            
            # 如果没有指定数据库，默认GO-BP和KEGG
            if not enrichment_config['databases']:
                enrichment_config['databases'] = ['go_bp', 'kegg']
            
            # 物种选择
            if '小鼠' in user_input or 'mouse' in user_input_lower:
                enrichment_config['species'] = 'mouse'
            elif '大鼠' in user_input or 'rat' in user_input_lower:
                enrichment_config['species'] = 'rat'
        
        return enrichment_config
    
    def _extract_visualization_requirements(self, user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """提取可视化需求"""
        user_input_lower = user_input.lower()
        
        # UMAP图
        if 'umap' in user_input_lower:
            if 'umap' not in config['dimred_viz']:
                config['dimred_viz'].append('umap')
        
        # tSNE图
        if 'tsne' in user_input_lower or 't-sne' in user_input_lower:
            if 'tsne' not in config['dimred_viz']:
                config['dimred_viz'].append('tsne')
        
        # 火山图
        if '火山图' in user_input or 'volcano' in user_input_lower:
            if 'volcano' not in config['de_viz']:
                config['de_viz'].append('volcano')
        
        # 气泡图（富集分析）
        if '气泡图' in user_input or 'bubble' in user_input_lower:
            config['enrichment_viz'] = ['bubble']
        
        # 空间可视化
        if '空间' in user_input and 'spatial_viz' in config:
            config['spatial_viz'] = ['spatial_gene', 'spatial_cluster']
        
        return config
    
    def validate_parameters(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证生成的参数是否合法
        
        Args:
            config: 生成的参数字典
            
        Returns:
            Tuple[是否合法, 错误信息]
        """
        try:
            # 验证质控参数
            qc = config.get('qc', {})
            if qc.get('min_genes', 0) > qc.get('max_genes', 100000):
                return False, "最小基因数不能大于最大基因数"
            
            if qc.get('min_umi', 0) > qc.get('max_umi', 1000000):
                return False, "最小UMI数不能大于最大UMI数"
            
            if qc.get('max_mito_ratio', 100) > 100:
                return False, "线粒体比例不能超过100%"
            
            # 验证聚类参数
            clustering = config.get('clustering', {})
            if clustering.get('resolution', 0.5) < 0.1 or clustering.get('resolution', 0.5) > 2.0:
                return False, "聚类分辨率应在0.1-2.0之间"
            
            # 验证差异表达参数
            de = config.get('differential', {})  # 与统一后的 key 保持一致
            if de.get('p_adjust_cutoff', 0.05) < 0.001 or de.get('p_adjust_cutoff', 0.05) > 0.1:
                return False, "p值阈值应在0.001-0.1之间"
            
            return True, "参数验证通过"
            
        except Exception as e:
            logger.error(f"参数验证失败: {e}")
            return False, f"参数验证异常: {str(e)}"
    
    def generate_prompt_template(self, data_type: str = 'single_cell') -> str:
        """
        生成提示词模板，用于指导大模型输出
        
        Args:
            data_type: 数据类型
            
        Returns:
            提示词模板字符串
        """
        template = f"""你是一个单细胞{'和空间转录组' if data_type == 'spatial' else ''}分析专家。请将用户的自然语言需求转换为JSON格式的分析参数。

请严格按照以下JSON格式输出，不要添加其他解释：

{{
  "qc": {{
    "filter_genes": true,
    "min_cells": 3,
    "min_genes": 200,
    "max_genes": 6000,
    "min_umi": 500,
    "max_umi": 20000,
    "filter_mito": true,
    "mito_prefix": "MT-",
    "max_mito_ratio": 20,
    "filter_ribo": false
  }},
  "normalization": {{
    "method": "scanpy_standard",
    "target_sum": 10000,
    "select_highly_variable": true,
    "highly_variable_genes": 2000,
    "scale_data": true
  }},
  "dimension_reduction": {{
    "n_pcs": 50,
    "run_umap": true,
    "umap_n_neighbors": 15,
    "umap_min_dist": 0.5,
    "run_tsne": false
  }},
  "clustering": {{
    "algorithm": "leiden",
    "resolution": 0.5
  }},
  "differential_expression": {{
    "run_de": true,
    "method": "wilcoxon",
    "p_adjust_cutoff": 0.05,
    "log2fc_cutoff": 0.25
  }},
  "enrichment": {{
    "run_enrichment": true,
    "databases": ["go_bp", "kegg"],
    "species": "human"
  }},
  "visualization": {{
    "qc": ["violin", "scatter"],
    "dimred": ["umap"],
    "marker": ["dotplot", "heatmap"],
    "de": ["volcano"],
    "enrichment": ["bubble"]
  }}
}}

用户需求："""
        return template
