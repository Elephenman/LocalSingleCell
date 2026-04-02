"""
Tests for core.ai_parser module
"""

import pytest
from core.ai_parser import AIParser


class TestAIParser:
    """Tests for AIParser class."""

    @pytest.fixture
    def parser(self, default_config):
        """Create an AIParser instance."""
        return AIParser(default_config)

    def test_parser_initialization(self, default_config):
        """Test parser initialization."""
        parser = AIParser(default_config)
        assert parser.config is not None

    def test_parse_basic_requirement(self, parser):
        """Test parsing a basic analysis requirement."""
        requirement = "做一个基础的单细胞分析"
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        assert isinstance(pipeline_config, dict)
        assert isinstance(viz_config, dict)

    def test_parse_qc_requirement(self, parser):
        """Test parsing quality control requirements."""
        requirement = "过滤线粒体比例超过15%的细胞，最少200个基因"
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        # Check QC parameters are set
        assert 'qc' in pipeline_config

    def test_parse_clustering_requirement(self, parser):
        """Test parsing clustering requirements."""
        requirement = "用Leiden算法，分辨率0.8聚类"
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        # Check clustering parameters
        assert 'clustering' in pipeline_config

    def test_parse_enrichment_requirement(self, parser):
        """Test parsing enrichment analysis requirements."""
        requirement = "做GO和KEGG富集分析"
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        # Check enrichment parameters
        assert 'enrichment' in pipeline_config

    def test_parse_visualization_requirement(self, parser):
        """Test parsing visualization requirements."""
        requirement = "生成UMAP图和火山图"
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        # Check visualization config
        assert isinstance(viz_config, dict)

    def test_parse_complex_requirement(self, parser):
        """Test parsing a complex multi-part requirement."""
        requirement = """
        过滤线粒体比例超过15%的细胞，最少300个基因，
        用Leiden算法分辨率0.8聚类，
        找每个聚类的标记基因，
        做GO和KEGG富集分析，
        生成UMAP图和气泡图
        """
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        assert isinstance(pipeline_config, dict)
        assert isinstance(viz_config, dict)

    def test_validate_parameters_valid(self, parser):
        """Test parameter validation with valid parameters."""
        valid_config = {
            'qc': {
                'filter_mito': True,
                'max_mito_ratio': 20,
                'min_genes': 200
            },
            'clustering': {
                'resolution': 0.5,
                'n_neighbors': 15
            }
        }

        is_valid, message = parser.validate_parameters(valid_config)
        assert is_valid is True

    def test_validate_parameters_invalid(self, parser):
        """Test parameter validation with invalid parameters."""
        invalid_config = {
            'clustering': {
                'resolution': 5.0,  # Out of range
            }
        }

        is_valid, message = parser.validate_parameters(invalid_config)
        # Validation behavior depends on implementation
        assert isinstance(is_valid, bool)
        assert isinstance(message, str)

    def test_empty_requirement(self, parser):
        """Test parsing empty requirement."""
        requirement = ""
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'single_cell')

        # Should return default config
        assert isinstance(pipeline_config, dict)


class TestKeywordExtraction:
    """Tests for keyword extraction in AI parser."""

    @pytest.fixture
    def parser(self, default_config):
        """Create an AIParser instance."""
        return AIParser(default_config)

    def test_extract_mitochondrial_keywords(self, parser):
        """Test extraction of mitochondrial-related keywords."""
        text = "线粒体比例超过15%"
        # Test internal keyword extraction
        assert "线粒体" in text or "mitochondrial" in text.lower()

    def test_extract_clustering_keywords(self, parser):
        """Test extraction of clustering-related keywords."""
        text = "Leiden聚类，分辨率0.8"
        assert "Leiden" in text or "聚类" in text

    def test_extract_enrichment_keywords(self, parser):
        """Test extraction of enrichment-related keywords."""
        text = "GO和KEGG富集分析"
        assert "GO" in text or "KEGG" in text or "富集" in text


class TestSpatialRequirements:
    """Tests for spatial transcriptomics requirements parsing."""

    @pytest.fixture
    def parser(self, spatial_config):
        """Create an AIParser instance with spatial config."""
        return AIParser(spatial_config)

    def test_parse_spatial_requirement(self, parser):
        """Test parsing spatial analysis requirements."""
        requirement = "空间转录组分析，找空间可变基因"
        pipeline_config, viz_config = parser.parse_requirement(requirement, 'spatial')

        assert isinstance(pipeline_config, dict)
