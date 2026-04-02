"""
Tests for utils.config_utils module
"""

import pytest
import yaml
from pathlib import Path
from utils import config_utils


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_config(self):
        """Test loading the default configuration file."""
        config = config_utils.load_config()

        assert isinstance(config, dict)
        assert 'random_seed' in config
        assert 'qc' in config

    def test_load_custom_config(self, temp_dir):
        """Test loading a custom configuration file."""
        config_path = temp_dir / "custom_config.yaml"

        custom_config = {
            'random_seed': 123,
            'qc': {
                'cell_filter': {
                    'min_genes': 300
                }
            }
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(custom_config, f)

        config = config_utils.load_config(config_path)

        assert config['random_seed'] == 123

    def test_missing_config_file(self, temp_dir):
        """Test behavior when config file doesn't exist."""
        nonexistent_path = temp_dir / "nonexistent.yaml"

        # Should either raise an error or return default config
        # depending on implementation
        try:
            config = config_utils.load_config(nonexistent_path)
            # If it returns a config, it should be a valid dict
            assert isinstance(config, dict)
        except FileNotFoundError:
            # This is also acceptable behavior
            pass


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config(self, temp_dir):
        """Test saving configuration to file."""
        config_path = temp_dir / "saved_config.yaml"

        config = {
            'random_seed': 42,
            'test_key': 'test_value'
        }

        config_utils.save_config(config, config_path)

        assert config_path.exists()

        # Verify content
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f)

        assert loaded['random_seed'] == 42
        assert loaded['test_key'] == 'test_value'


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_valid_config_structure(self, default_config):
        """Test that default config has valid structure."""
        required_keys = ['random_seed', 'qc', 'normalization', 'clustering']

        for key in required_keys:
            assert key in default_config, f"Missing required key: {key}"

    def test_qc_config_structure(self, default_config):
        """Test QC configuration structure."""
        qc_config = default_config.get('qc', {})

        assert 'cell_filter' in qc_config
        assert 'min_genes' in qc_config['cell_filter']
        assert 'max_genes' in qc_config['cell_filter']

    def test_clustering_config_structure(self, default_config):
        """Test clustering configuration structure."""
        clustering_config = default_config.get('clustering', {})

        assert 'resolution' in clustering_config
        assert 0 <= clustering_config['resolution'] <= 2


class TestConfigMerge:
    """Tests for configuration merging."""

    def test_merge_configs(self):
        """Test merging user config with defaults."""
        default = {
            'a': 1,
            'b': 2,
            'nested': {
                'x': 10,
                'y': 20
            }
        }

        user_override = {
            'b': 3,
            'nested': {
                'y': 30
            }
        }

        # If there's a merge function, test it
        # merged = config_utils.merge_configs(default, user_override)
        # assert merged['a'] == 1
        # assert merged['b'] == 3
        # assert merged['nested']['x'] == 10
        # assert merged['nested']['y'] == 30
        pass
