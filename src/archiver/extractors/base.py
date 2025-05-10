from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

@dataclass
class ExtractionStats:
    """Statistics for extraction operations."""
    directories_processed: int = 0
    compressed_files_found: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0

class BaseExtractor(ABC):
    """Base class for archive extractors."""

    def __init__(self, base_dir: Path):
        """Initialize the extractor.

        Args:
            base_dir: Base directory for extraction operations
        """
        self.base_dir = base_dir
        self.stats = ExtractionStats()

    @property
    @abstractmethod
    def supported_extensions(self) -> tuple[str, ...]:
        """Return tuple of supported file extensions.

        Returns:
            Tuple of supported extensions (e.g., ('.zip', '.rar'))
        """
        pass

    def can_handle(self, file_path: Path) -> bool:
        """Check if this extractor can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file can be handled by this extractor
        """
        return file_path.suffix.lower() in self.supported_extensions

    @abstractmethod
    def extract(self, archive_path: Path, target_dir: Optional[Path] = None) -> bool:
        """Extract the archive to the target directory.

        Args:
            archive_path: Path to the archive file
            target_dir: Optional target directory. If None, extract to archive's directory

        Returns:
            True if extraction was successful
        """
        pass

    def get_stats(self) -> Dict[str, int]:
        """Get current extraction statistics.

        Returns:
            Dictionary containing current statistics
        """
        return self.stats.__dict__
