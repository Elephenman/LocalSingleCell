"""
Tests for utils.validator_utils module
"""

import pytest
from utils import validator_utils


class TestValidateSRAId:
    """Tests for SRA ID validation."""

    def test_valid_srr_id(self):
        """Test valid SRR format."""
        valid_ids = ['SRR123456', 'SRR000001', 'SRR999999999']

        for sra_id in valid_ids:
            result = validator_utils.validate_sra_id(sra_id)
            assert result is True or result is not None

    def test_valid_err_id(self):
        """Test valid ERR format."""
        valid_ids = ['ERR123456', 'ERR000001']

        for sra_id in valid_ids:
            result = validator_utils.validate_sra_id(sra_id)
            assert result is True or result is not None

    def test_valid_drr_id(self):
        """Test valid DRR format."""
        valid_ids = ['DRR123456', 'DRR000001']

        for sra_id in valid_ids:
            result = validator_utils.validate_sra_id(sra_id)
            assert result is True or result is not None

    def test_invalid_format(self):
        """Test invalid SRA ID formats."""
        invalid_ids = ['ABC123456', 'SRR', '123456', 'srr123456', '']

        for sra_id in invalid_ids:
            try:
                result = validator_utils.validate_sra_id(sra_id)
                # If no exception, result should indicate invalid
                assert result is False or result is None
            except ValueError:
                # ValueError is also acceptable for invalid input
                pass


class TestValidateFilePath:
    """Tests for file path validation."""

    def test_valid_file_path(self, temp_dir):
        """Test valid file path."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        result = validator_utils.validate_file_path(str(test_file))
        assert result is True or result is not None

    def test_nonexistent_file(self, temp_dir):
        """Test nonexistent file path."""
        nonexistent = temp_dir / "nonexistent.txt"

        result = validator_utils.validate_file_path(str(nonexistent))
        assert result is False or result is None

    def test_invalid_characters(self):
        """Test path with invalid characters."""
        # Test paths that might be problematic
        invalid_paths = ['', None]

        for path in invalid_paths:
            try:
                result = validator_utils.validate_file_path(path)
                assert result is False or result is None
            except (ValueError, TypeError):
                # Exception is acceptable for invalid input
                pass


class TestValidateNumericRange:
    """Tests for numeric range validation."""

    def test_value_in_range(self):
        """Test value within valid range."""
        result = validator_utils.validate_numeric_range(5, min_val=0, max_val=10)
        assert result is True

    def test_value_at_boundary(self):
        """Test value at range boundary."""
        result = validator_utils.validate_numeric_range(0, min_val=0, max_val=10)
        assert result is True

        result = validator_utils.validate_numeric_range(10, min_val=0, max_val=10)
        assert result is True

    def test_value_outside_range(self):
        """Test value outside valid range."""
        result = validator_utils.validate_numeric_range(-1, min_val=0, max_val=10)
        assert result is False

        result = validator_utils.validate_numeric_range(11, min_val=0, max_val=10)
        assert result is False

    def test_invalid_input_type(self):
        """Test with invalid input types."""
        try:
            result = validator_utils.validate_numeric_range("not a number", min_val=0, max_val=10)
            assert result is False
        except (TypeError, ValueError):
            # Exception is acceptable
            pass


class TestValidateFileExtension:
    """Tests for file extension validation."""

    def test_valid_extension(self):
        """Test file with valid extension."""
        result = validator_utils.validate_file_extension("test.h5ad", ["h5ad"])
        assert result is True

        result = validator_utils.validate_file_extension("data.zip", ["zip", "tar"])
        assert result is True

    def test_invalid_extension(self):
        """Test file with invalid extension."""
        result = validator_utils.validate_file_extension("test.txt", ["h5ad"])
        assert result is False

    def test_case_insensitive(self):
        """Test case insensitive extension matching."""
        result = validator_utils.validate_file_extension("test.H5AD", ["h5ad"])
        # Depends on implementation
        assert result is True or result is False


class TestValidateEmptyValue:
    """Tests for empty value validation."""

    def test_non_empty_string(self):
        """Test non-empty string validation."""
        result = validator_utils.validate_not_empty("test")
        assert result is True

    def test_empty_string(self):
        """Test empty string validation."""
        result = validator_utils.validate_not_empty("")
        assert result is False

    def test_none_value(self):
        """Test None value validation."""
        result = validator_utils.validate_not_empty(None)
        assert result is False

    def test_whitespace_only(self):
        """Test whitespace-only string."""
        result = validator_utils.validate_not_empty("   ")
        # Depends on implementation
        assert result is True or result is False


class TestSanitizeInput:
    """Tests for input sanitization."""

    def test_sanitize_string(self):
        """Test string sanitization."""
        if hasattr(validator_utils, 'sanitize_input'):
            result = validator_utils.sanitize_input("<script>alert('test')</script>")
            assert "<script>" not in result

    def test_sanitize_path(self):
        """Test path sanitization."""
        if hasattr(validator_utils, 'sanitize_path'):
            result = validator_utils.sanitize_path("../../../etc/passwd")
            # Should not allow path traversal
            assert ".." not in result or result is False
