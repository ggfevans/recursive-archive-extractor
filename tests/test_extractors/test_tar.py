import pytest
from pathlib import Path
import tarfile
import shutil

from archiver.extractors.tar import TarExtractor

@pytest.fixture
def tar_extractor(temp_dir):
    """Create a TAR extractor instance."""
    return TarExtractor(temp_dir)

@pytest.fixture
def test_tars(test_archives_dir):
    """Get paths to test TAR files."""
    tar_dir = test_archives_dir / "tar"
    return {
        'tar': tar_dir / "valid.tar",
        'gz': tar_dir / "valid.tar.gz",
        'bz2': tar_dir / "valid.tar.bz2"
    }

def test_tar_extractor_initialization(tar_extractor):
    """Test TAR extractor initialization."""
    assert '.tar' in tar_extractor.supported_extensions
    assert '.tar.gz' in tar_extractor.supported_extensions
    assert '.tar.bz2' in tar_extractor.supported_extensions

def test_tar_can_handle(tar_extractor):
    """Test TAR file detection."""
    assert tar_extractor.can_handle(Path("test.tar"))
    assert tar_extractor.can_handle(Path("test.tar.gz"))
    assert tar_extractor.can_handle(Path("test.tar.bz2"))
    assert tar_extractor.can_handle(Path("test.tgz"))
    assert tar_extractor.can_handle(Path("test.tbz2"))
    assert not tar_extractor.can_handle(Path("test.zip"))
    assert not tar_extractor.can_handle(Path("test"))

def test_tar_extract_valid(tar_extractor, test_tars, temp_dir):
    """Test extracting various TAR formats."""
    for format_name, tar_path in test_tars.items():
        extract_dir = temp_dir / format_name
        extract_dir.mkdir()
        
        assert tar_extractor.extract(tar_path, extract_dir)
        assert (extract_dir / "test1.txt").exists()
        assert (extract_dir / "test2.txt").exists()
        
        # Check content
        assert (extract_dir / "test1.txt").read_text() == "tar test content 1\n"
        assert (extract_dir / "test2.txt").read_text() == "tar test content 2\n"

def test_tar_extract_nonexistent(tar_extractor, temp_dir):
    """Test extracting a nonexistent TAR file."""
    assert not tar_extractor.extract(temp_dir / "nonexistent.tar")
    assert tar_extractor.stats.failed_extractions == 1

def test_tar_extract_corrupted(tar_extractor, temp_dir):
    """Test extracting a corrupted TAR file."""
    # Create a corrupted TAR file
    corrupted_tar = temp_dir / "corrupted.tar"
    corrupted_tar.write_bytes(b"This is not a valid TAR file")
    
    assert not tar_extractor.extract(corrupted_tar)
    assert tar_extractor.stats.failed_extractions == 1

def test_tar_safe_extraction(tar_extractor, temp_dir):
    """Test safe path extraction."""
    # Create a TAR file with a file that tries to write outside the target directory
    unsafe_tar = temp_dir / "unsafe.tar"
    with tarfile.open(unsafe_tar, 'w') as tar:
        tar.addfile(tarfile.TarInfo("../outside.txt"))
    
    assert not tar_extractor.extract(unsafe_tar, temp_dir)
    assert not (temp_dir.parent / "outside.txt").exists()

def test_tar_statistics_tracking(tar_extractor, test_tars, temp_dir):
    """Test statistics tracking during TAR extraction."""
    # Extract valid file
    tar_extractor.extract(test_tars['tar'], temp_dir)
    
    # Try to extract nonexistent file
    tar_extractor.extract(temp_dir / "nonexistent.tar")
    
    stats = tar_extractor.get_stats()
    assert stats["successful_extractions"] == 1
    assert stats["failed_extractions"] == 1
