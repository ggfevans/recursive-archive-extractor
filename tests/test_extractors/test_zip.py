import pytest
from pathlib import Path
import zipfile
import shutil

from archiver.extractors.zip import ZipExtractor

@pytest.fixture
def zip_extractor(temp_dir):
    """Create a ZIP extractor instance."""
    return ZipExtractor(temp_dir)

@pytest.fixture
def test_zip(test_archives_dir):
    """Get path to test ZIP file."""
    return test_archives_dir / "zip" / "valid.zip"

def test_zip_extractor_initialization(zip_extractor):
    """Test ZIP extractor initialization."""
    assert zip_extractor.supported_extensions == ('.zip',)

def test_zip_can_handle(zip_extractor):
    """Test ZIP file detection."""
    assert zip_extractor.can_handle(Path("test.zip"))
    assert zip_extractor.can_handle(Path("test.ZIP"))
    assert not zip_extractor.can_handle(Path("test.rar"))
    assert not zip_extractor.can_handle(Path("test"))

def test_zip_extract_valid(zip_extractor, test_zip, temp_dir):
    """Test extracting a valid ZIP file."""
    assert zip_extractor.extract(test_zip, temp_dir)
    assert (temp_dir / "test1.txt").exists()
    assert (temp_dir / "test2.txt").exists()
    
    # Check content
    assert (temp_dir / "test1.txt").read_text() == "test content 1\n"
    assert (temp_dir / "test2.txt").read_text() == "test content 2\n"

def test_zip_extract_nonexistent(zip_extractor, temp_dir):
    """Test extracting a nonexistent ZIP file."""
    assert not zip_extractor.extract(temp_dir / "nonexistent.zip")
    assert zip_extractor.stats.failed_extractions == 1

def test_zip_extract_corrupted(zip_extractor, temp_dir):
    """Test extracting a corrupted ZIP file."""
    # Create a corrupted ZIP file
    corrupted_zip = temp_dir / "corrupted.zip"
    corrupted_zip.write_bytes(b"This is not a valid ZIP file")
    
    assert not zip_extractor.extract(corrupted_zip)
    assert zip_extractor.stats.failed_extractions == 1

def test_zip_statistics_tracking(zip_extractor, test_zip, temp_dir):
    """Test statistics tracking during ZIP extraction."""
    # Extract valid file
    zip_extractor.extract(test_zip, temp_dir)
    
    # Try to extract nonexistent file
    zip_extractor.extract(temp_dir / "nonexistent.zip")
    
    stats = zip_extractor.get_stats()
    assert stats["successful_extractions"] == 1
    assert stats["failed_extractions"] == 1
