"""
Tests for core.qc_filter module
"""

import pytest
import numpy as np
import pandas as pd
import anndata as ad
from core import qc_filter


class TestCalculateQCMetrics:
    """Tests for calculate_qc_metrics function."""

    def test_basic_calculation(self, small_adata):
        """Test basic QC metrics calculation."""
        result = qc_filter.calculate_qc_metrics(small_adata)

        assert 'n_genes_by_counts' in result.obs.columns
        assert 'total_counts' in result.obs.columns

    def test_empty_data(self):
        """Test with empty AnnData."""
        adata = ad.AnnData(X=np.array([]).reshape(0, 0))
        result = qc_filter.calculate_qc_metrics(adata)
        assert result.n_obs == 0


class TestCalculateMitochondrialPercent:
    """Tests for mitochondrial percentage calculation."""

    def test_basic_calculation(self, small_adata):
        """Test mitochondrial percentage calculation."""
        # Add some MT- prefixed genes
        small_adata.var_names = [f'gene_{i}' if i < 495 else f'MT-{i-495}' for i in range(500)]

        result = qc_filter.calculate_mitochondrial_percent(small_adata, mitochondrial_prefix='MT-')

        assert 'pct_counts_mt' in result.obs.columns

    def test_no_mitochondrial_genes(self, small_adata):
        """Test when no mitochondrial genes are present."""
        result = qc_filter.calculate_mitochondrial_percent(small_adata, mitochondrial_prefix='MT-')

        assert 'pct_counts_mt' in result.obs.columns
        # Should be 0 or very low


class TestFilterCells:
    """Tests for filter_cells function."""

    def test_filter_by_genes(self, small_adata):
        """Test filtering cells by gene count."""
        original_n = small_adata.n_obs

        result = qc_filter.filter_cells(
            small_adata,
            min_genes=100,
            max_genes=10000
        )

        assert result.n_obs <= original_n

    def test_filter_by_umi(self, small_adata):
        """Test filtering cells by UMI count."""
        original_n = small_adata.n_obs

        result = qc_filter.filter_cells(
            small_adata,
            min_umi=100,
            max_umi=100000
        )

        assert result.n_obs <= original_n

    def test_no_filtering_needed(self, small_adata):
        """Test when no cells should be filtered."""
        result = qc_filter.filter_cells(
            small_adata,
            min_genes=0,
            max_genes=100000,
            min_umi=0,
            max_umi=1000000
        )

        assert result.n_obs == small_adata.n_obs


class TestFilterGenes:
    """Tests for filter_genes function."""

    def test_filter_by_cells(self, small_adata):
        """Test filtering genes by cell count."""
        original_n = small_adata.n_vars

        result = qc_filter.filter_genes(small_adata, min_cells=5)

        assert result.n_vars <= original_n

    def test_no_filtering_needed(self, small_adata):
        """Test when no genes should be filtered."""
        result = qc_filter.filter_genes(small_adata, min_cells=0)

        assert result.n_vars == small_adata.n_vars


class TestFilterMitochondrialCells:
    """Tests for filter_mitochondrial_cells function."""

    def test_basic_filter(self, small_adata):
        """Test mitochondrial cell filtering."""
        # Add mitochondrial percentage
        small_adata.obs['pct_counts_mt'] = np.random.uniform(0, 50, small_adata.n_obs)

        result = qc_filter.filter_mitochondrial_cells(small_adata, max_mt_percent=20)

        # Check that remaining cells have low MT percentage
        assert all(result.obs['pct_counts_mt'] <= 20)


class TestFilterRibosomalCells:
    """Tests for filter_ribosomal_cells function."""

    def test_basic_filter(self, small_adata):
        """Test ribosomal cell filtering."""
        # Add ribosomal percentage
        small_adata.obs['pct_counts_ribo'] = np.random.uniform(0, 80, small_adata.n_obs)

        result = qc_filter.filter_ribosomal_cells(small_adata, max_ribo_percent=50)

        assert all(result.obs['pct_counts_ribo'] <= 50)
