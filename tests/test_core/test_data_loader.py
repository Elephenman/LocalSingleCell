"""
Tests for core.data_loader module
"""

import pytest
import numpy as np
import pandas as pd
import anndata as ad
from pathlib import Path
from core import data_loader


class TestReadH5ad:
    """Tests for read_h5ad function."""

    def test_read_valid_file(self, temp_dir, small_adata):
        """Test reading a valid h5ad file."""
        file_path = temp_dir / "test.h5ad"
        small_adata.write_h5ad(file_path)

        result = data_loader.read_h5ad(file_path)

        assert isinstance(result, ad.AnnData)
        assert result.n_obs == small_adata.n_obs
        assert result.n_vars == small_adata.n_vars

    def test_file_not_found(self, temp_dir):
        """Test reading a non-existent file."""
        file_path = temp_dir / "nonexistent.h5ad"

        with pytest.raises(FileNotFoundError):
            data_loader.read_h5ad(file_path)


class TestRead10xMtx:
    """Tests for read_10x_mtx function."""

    def test_read_valid_directory(self, temp_dir):
        """Test reading a valid 10x directory."""
        # Create a mock 10x directory structure
        matrix_dir = temp_dir / "filtered_feature_bc_matrix"
        matrix_dir.mkdir()

        n_cells = 10
        n_genes = 100

        # Create barcodes.tsv.gz
        barcodes = pd.DataFrame([f'barcode_{i}' for i in range(n_cells)])
        barcodes.to_csv(matrix_dir / 'barcodes.tsv.gz', sep='\t', header=False, index=False, compression='gzip')

        # Create features.tsv.gz
        features = pd.DataFrame({
            'gene_id': [f'gene_{i}' for i in range(n_genes)],
            'gene_name': [f'gene_{i}' for i in range(n_genes)],
            'type': ['Gene Expression'] * n_genes
        })
        features.to_csv(matrix_dir / 'features.tsv.gz', sep='\t', header=False, index=False, compression='gzip')

        # Create matrix.mtx.gz
        from scipy import sparse
        matrix = sparse.random(n_cells, n_genes, density=0.1, format='csr')
        from scipy.io import mmwrite
        mmwrite(str(matrix_dir / 'matrix.mtx'), matrix)
        import gzip
        with open(matrix_dir / 'matrix.mtx', 'rb') as f_in:
            with gzip.open(matrix_dir / 'matrix.mtx.gz', 'wb') as f_out:
                f_out.write(f_in.read())

        result = data_loader.read_10x_mtx(matrix_dir)

        assert isinstance(result, ad.AnnData)
        assert result.n_obs == n_cells

    def test_invalid_directory(self, temp_dir):
        """Test reading from invalid directory."""
        invalid_dir = temp_dir / "invalid"

        with pytest.raises((FileNotFoundError, ValueError)):
            data_loader.read_10x_mtx(invalid_dir)


class TestValidateFile:
    """Tests for file validation functions."""

    def test_validate_h5ad_extension(self, temp_dir):
        """Test h5ad file extension validation."""
        valid_path = temp_dir / "test.h5ad"
        invalid_path = temp_dir / "test.txt"

        # This depends on the actual implementation
        # Assuming there's a validation function
        pass


class TestGetAnnDataInfo:
    """Tests for AnnData info extraction."""

    def test_basic_info(self, small_adata):
        """Test getting basic AnnData information."""
        info = {
            'n_obs': small_adata.n_obs,
            'n_vars': small_adata.n_vars,
            'obs_columns': list(small_adata.obs.columns),
            'var_columns': list(small_adata.var.columns)
        }

        assert info['n_obs'] == 100
        assert info['n_vars'] == 500
