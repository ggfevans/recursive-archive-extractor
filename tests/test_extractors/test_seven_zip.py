import pytest
from pathlib import Path
import py7zr
import shutil

from archiver.extractors.seven_zip import SevenZipExtractor

@pytest.fixture
def seven_zip_extractor(temp_dir):
    """Create a 7Z extractor instance."""
    return SevenZipExtractor(temp_dir)

@pytest.fixture
def test_7z(test_archives_dir):
    """Get path to test 7Z file."""
    return test_archives_dir / "7z" / "valid.7z"

def test_7z_extractor_initialization(seven_zip_extractor):
    """Test 7Z extractor initialization."""
    assert seven_zip_extractor.supported_extensions == ('.7z',)

def test_7z_can_handle(seven_zip_extractor):
    """Test 7Z file detection."""
    assert seven_zip_extractor.can_handle(Path("test.7z"))
    assert seven_zip_extractor.can_handle(Path("test.7Z"))
    assert not seven_zip_extractor.can_handle(Path("test.zip"))
    assert not seven_zip_extractor.can_handle(Path("test"))

def test_7z_extract_valid(seven_zip_extractor, test_7z, temp_dir):
    """Test extracting a valid 7Z file."""
    assert seven_zip_extractor.extract(test_7z, temp_dir)
    assert (temp_dir / "test1.txt").exists()
    assert (temp_dir / "test2.txt").exists()
    
    # Check content
    assert (temp_dir / "test1.txt").read_text() == "7z test content 1\n"
    assert (temp_dir / "test2.txt").read_text() == "7z test content 2\n"

def test_7z_extract_nonexistent(seven_zip_extractor, temp_dir):
    """Test extracting a nonexistent 7Z file."""
    assert not seven_zip_extractor.extract(temp_dir / "nonexistent.7z")
    assert seven_zip_extractor.stats.failed_extractions == 1

def test_7z_extract_corrupted(seven_zip_extractor, temp_dir):
    """Test extracting a corrupted 7Z file."""
    # Create a corrupted 7Z file
    corrupted_7z = temp_dir / "corrupted.7z"
    corrupted_7z.write_bytes(b"This is not a valid 7Z file")
    
    assert not seven_zip_extractor.extract(corrupted_7z)
    assert seven_zip_extractor.stats.failed_extractions == 1

def test_7z_verify_integrity(seven_zip_extractor, test_7z, temp_dir):
    """Test integrity verification of 7Z files."""
    # Valid file should pass verification
    assert seven_zip_extractor.verify_integrity(test_7z)
    
    # Corrupted file should fail verification
    corrupted_7z = temp_dir / "corrupted.7z"
    corrupted_7z.write_bytes(b"This is not a valid 7Z file")
    assert not seven_zip_extractor.verify_integrity(corrupted_7z)

def test_7z_statistics_tracking(seven_zip_extractor, test_7z, temp_dir):
    """Test statistics tracking during 7Z extraction."""
    # Extract valid file
    seven_zip_extractor.extract(test_7z, temp_dir)
    
    # Try to extract nonexistent file
    seven_zip_extractor.extract(temp_dir / "nonexistent.7z")
    
    stats = seven_zip_extractor.get_stats()
    assert stats["successful_extractions"] == 1
    assert stats["failed_extractions"] == 1
