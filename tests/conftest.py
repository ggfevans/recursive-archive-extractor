import os
import pytest
from pathlib import Path

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path

@pytest.fixture
def test_archives_dir():
    """Get the path to test archive files."""
    return Path(__file__).parent / 'data' / 'archives'

@pytest.fixture
def resource_path():
    """Get a function to load test resources."""
    def _get_resource_path(name: str) -> Path:
        return Path(__file__).parent / 'data' / name
    return _get_resource_path
