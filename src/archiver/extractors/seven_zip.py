import logging
import py7zr
import shutil
from pathlib import Path
from typing import Optional

from .base import BaseExtractor

logger = logging.getLogger(__name__)

class SevenZipExtractor(BaseExtractor):
    """Extractor for 7-Zip archives."""

    def __init__(self, base_dir: Path):
        """Initialize the 7-Zip extractor.

        Args:
            base_dir: Base directory for extraction operations

        Raises:
            RuntimeError: If py7zr is not available
        """
        super().__init__(base_dir)
        try:
            import py7zr
        except ImportError:
            raise RuntimeError("py7zr package not found. Please install py7zr for 7z support.")

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Return supported file extensions.

        Returns:
            Tuple containing supported extensions
        """
        return ('.7z',)

    def verify_integrity(self, archive_path: Path) -> bool:
        """Verify the integrity of a 7z archive.

        Args:
            archive_path: Path to the archive file

        Returns:
            True if archive is valid
        """
        try:
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                return archive.test()
        except Exception as e:
            logger.error(f"Failed to verify 7z archive {archive_path}: {e}")
            return False

    def extract(self, archive_path: Path, target_dir: Optional[Path] = None) -> bool:
        """Extract a 7z archive.

        Args:
            archive_path: Path to the archive file
            target_dir: Optional target directory. If None, extract to archive's directory

        Returns:
            True if extraction was successful
        """
        try:
            target_dir = target_dir or archive_path.parent
            logger.info(f"Extracting {archive_path} to {target_dir}")

            # Verify integrity first
            if not self.verify_integrity(archive_path):
                logger.error(f"Archive {archive_path} failed integrity check")
                self.stats.failed_extractions += 1
                return False

            # Extract the archive
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall(target_dir)
                self.stats.successful_extractions += 1
                return True

        except Exception as e:
            logger.error(f"Error extracting 7z file {archive_path}: {str(e)}")
            self.stats.failed_extractions += 1
            return False
