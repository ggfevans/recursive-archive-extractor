import json
import pytest
from pathlib import Path
from archiver.utils.config import ArchiveConfig

def test_config_basic_initialization():
    """Test basic configuration initialization."""
    config = ArchiveConfig(base_dir=Path("/tmp"))
    assert config.base_dir == Path("/tmp")
    assert config.dry_run is False
    assert config.verbose is False
    assert config.log_file is None

def test_config_validation_base_dir(temp_dir):
    """Test configuration validation for base directory."""
    # Valid directory should work
    config = ArchiveConfig(base_dir=temp_dir)
    config.validate()

    # Non-existent directory should fail in non-dry-run mode
    with pytest.raises(ValueError):
        config = ArchiveConfig(base_dir=Path("/nonexistent"))
        config.validate()

    # Non-existent directory should work in dry-run mode
    config = ArchiveConfig(base_dir=Path("/nonexistent"), dry_run=True)
    config.validate()

def test_config_validation_formats():
    """Test format validation."""
    # At least one format must be enabled
    with pytest.raises(ValueError):
        config = ArchiveConfig(
            base_dir=Path("/tmp"),
            enable_zip=False,
            enable_rar=False,
            enable_7z=False,
            enable_tar=False
        )
        config.validate()

def test_config_save_load(temp_dir):
    """Test saving and loading configuration."""
    config_file = temp_dir / "test_config.json"
    original_config = ArchiveConfig(
        base_dir=Path("/test"),
        verbose=True,
        max_workers=8,
        process_nested=True,
        max_depth=3
    )
    
    # Save configuration
    original_config.to_file(config_file)
    
    # Load configuration
    loaded_config = ArchiveConfig.from_file(config_file)
    
    # Check values match
    assert loaded_config.base_dir == Path("/test")
    assert loaded_config.verbose is True
    assert loaded_config.max_workers == 8
    assert loaded_config.process_nested is True
    assert loaded_config.max_depth == 3

def test_config_merge():
    """Test configuration merging."""
    config = ArchiveConfig(
        base_dir=Path("/test"),
        verbose=False,
        max_workers=4
    )
    
    # Merge new values
    config.merge({
        "verbose": True,
        "max_workers": 8,
        "nonexistent_option": "value"  # Should be ignored
    })
    
    assert config.verbose is True
    assert config.max_workers == 8
    assert not hasattr(config, "nonexistent_option")

def test_config_validation_max_workers():
    """Test validation of max_workers setting."""
    with pytest.raises(ValueError):
        config = ArchiveConfig(base_dir=Path("/tmp"), max_workers=0)
        config.validate()

    with pytest.raises(ValueError):
        config = ArchiveConfig(base_dir=Path("/tmp"), max_workers=-1)
        config.validate()

def test_config_validation_max_depth():
    """Test validation of max_depth setting."""
    with pytest.raises(ValueError):
        config = ArchiveConfig(base_dir=Path("/tmp"), max_depth=0)
        config.validate()

    with pytest.raises(ValueError):
        config = ArchiveConfig(base_dir=Path("/tmp"), max_depth=-1)
        config.validate()
