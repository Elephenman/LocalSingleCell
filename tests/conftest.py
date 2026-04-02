"""
Pytest Configuration and Fixtures

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import anndata as ad


# ============================================================
# Configuration
# ============================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# ============================================================
# Directory Fixtures
# ============================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    dir_path = tempfile.mkdtemp()
    yield Path(dir_path)
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def fixtures_dir():
    """Return the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


# ============================================================
# AnnData Fixtures
# ============================================================

@pytest.fixture
def small_adata():
    """
    Create a small AnnData object for quick testing.

    Returns:
        AnnData: Object with 100 cells and 500 genes
    """
    np.random.seed(42)
    n_cells = 100
    n_genes = 500

    # Generate random count data
    X = np.random.negative_binomial(5, 0.3, size=(n_cells, n_genes))

    # Create observation metadata
    obs = pd.DataFrame({
        'n_genes': np.random.randint(200, 3000, n_cells),
        'n_counts': np.random.randint(1000, 20000, n_cells),
        'pct_mito': np.random.uniform(0, 20, n_cells)
    }, index=[f'cell_{i}' for i in range(n_cells)])

    # Create variable metadata
    var = pd.DataFrame({
        'gene_name': [f'gene_{i}' for i in range(n_genes)]
    }, index=[f'gene_{i}' for i in range(n_genes)])

    # Create AnnData object
    adata = ad.AnnData(
        X=X.astype(np.float32),
        obs=obs,
        var=var
    )

    return adata


@pytest.fixture
def adata_with_clusters(small_adata):
    """
    Create an AnnData object with clustering results.

    Returns:
        AnnData: Object with Leiden clustering results
    """
    adata = small_adata.copy()

    # Add PCA results
    adata.obsm['X_pca'] = np.random.randn(adata.n_obs, 50)

    # Add UMAP results
    adata.obsm['X_umap'] = np.random.randn(adata.n_obs, 2)

    # Add cluster assignments
    adata.obs['leiden'] = pd.Categorical(
        [f'{i % 5}' for i in range(adata.n_obs)]
    )

    return adata


@pytest.fixture
def large_adata():
    """
    Create a larger AnnData object for performance testing.

    Returns:
        AnnData: Object with 1000 cells and 2000 genes
    """
    np.random.seed(42)
    n_cells = 1000
    n_genes = 2000

    X = np.random.negative_binomial(5, 0.3, size=(n_cells, n_genes))

    obs = pd.DataFrame({
        'n_genes': np.random.randint(200, 6000, n_cells),
        'n_counts': np.random.randint(500, 50000, n_cells),
    }, index=[f'cell_{i}' for i in range(n_cells)])

    var = pd.DataFrame(index=[f'gene_{i}' for i in range(n_genes)])

    adata = ad.AnnData(X=X.astype(np.float32), obs=obs, var=var)

    return adata


# ============================================================
# Configuration Fixtures
# ============================================================

@pytest.fixture
def default_config():
    """
    Return a default configuration dictionary.

    Returns:
        dict: Default analysis configuration
    """
    return {
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


@pytest.fixture
def spatial_config(default_config):
    """
    Return a spatial analysis configuration.

    Returns:
        dict: Configuration with spatial settings
    """
    config = default_config.copy()
    config['spatial'] = {
        'apply': True,
        'coord_type': 'grid',
        'n_rings': 1,
        'delaunay': False,
        'spatial_variable_genes': {
            'apply': True,
            'mode': 'moran'
        },
        'colocalization': {
            'apply': False,
            'n_splits': 1
        },
        'ligand_receptor': {
            'apply': False
        }
    }
    return config


# ============================================================
# File Fixtures
# ============================================================

@pytest.fixture
def temp_h5ad_file(temp_dir, small_adata):
    """
    Create a temporary h5ad file for testing.

    Returns:
        Path: Path to the temporary h5ad file
    """
    file_path = temp_dir / "test_data.h5ad"
    small_adata.write_h5ad(file_path)
    return file_path


@pytest.fixture
def invalid_file(temp_dir):
    """
    Create an invalid file for error testing.

    Returns:
        Path: Path to an invalid file
    """
    file_path = temp_dir / "invalid.h5ad"
    with open(file_path, 'w') as f:
        f.write("This is not a valid h5ad file")
    return file_path
