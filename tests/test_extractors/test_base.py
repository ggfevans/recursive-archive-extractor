import pytest
from pathlib import Path
from archiver.extractors.base import BaseExtractor, ExtractionStats

class TestExtractor(BaseExtractor):
    """Test implementation of BaseExtractor."""
    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return ('.test',)

    def extract(self, archive_path: Path, target_dir: Path | None = None) -> bool:
        return True

def test_base_extractor_initialization():
    """Test base extractor initialization."""
    base_dir = Path("/tmp")
    extractor = TestExtractor(base_dir)
    assert extractor.base_dir == base_dir
    assert isinstance(extractor.stats, ExtractionStats)

def test_extraction_stats_initialization():
    """Test extraction statistics initialization."""
    stats = ExtractionStats()
    assert stats.directories_processed == 0
    assert stats.compressed_files_found == 0
    assert stats.successful_extractions == 0
    assert stats.failed_extractions == 0

def test_can_handle_method():
    """Test file type detection."""
    extractor = TestExtractor(Path("/tmp"))
    
    # Should handle .test files
    assert extractor.can_handle(Path("file.test"))
    assert extractor.can_handle(Path("file.TEST"))  # Case insensitive
    
    # Should not handle other extensions
    assert not extractor.can_handle(Path("file.txt"))
    assert not extractor.can_handle(Path("file"))
    assert not extractor.can_handle(Path("file.test.txt"))

def test_get_stats():
    """Test statistics retrieval."""
    extractor = TestExtractor(Path("/tmp"))
    stats_dict = extractor.get_stats()
    
    assert isinstance(stats_dict, dict)
    assert "directories_processed" in stats_dict
    assert "compressed_files_found" in stats_dict
    assert "successful_extractions" in stats_dict
    assert "failed_extractions" in stats_dict

def test_stats_tracking():
    """Test statistics tracking during operations."""
    extractor = TestExtractor(Path("/tmp"))
    
    # Simulate some operations
    extractor.stats.directories_processed += 1
    extractor.stats.compressed_files_found += 2
    extractor.stats.successful_extractions += 1
    extractor.stats.failed_extractions += 1
    
    stats = extractor.get_stats()
    assert stats["directories_processed"] == 1
    assert stats["compressed_files_found"] == 2
    assert stats["successful_extractions"] == 1
    assert stats["failed_extractions"] == 1
