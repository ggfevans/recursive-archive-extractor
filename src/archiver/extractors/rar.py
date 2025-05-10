import logging
import subprocess
from pathlib import Path
from typing import Optional
import shutil

from .base import BaseExtractor

logger = logging.getLogger(__name__)

class RarExtractor(BaseExtractor):
    """Extractor for RAR archives."""

    def __init__(self, base_dir: Path):
        """Initialize the RAR extractor.

        Args:
            base_dir: Base directory for extraction operations

        Raises:
            RuntimeError: If unrar command is not available
        """
        super().__init__(base_dir)
        if not shutil.which('unrar'):
            raise RuntimeError("unrar command not found. Please install unrar.")

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Return supported file extensions.

        Returns:
            Tuple containing .rar extension
        """
        return ('.rar',)

    def extract(self, archive_path: Path, target_dir: Optional[Path] = None) -> bool:
        """Extract a RAR archive using unrar command.

        Args:
            archive_path: Path to the RAR archive
            target_dir: Optional target directory. If None, extract to archive's directory

        Returns:
            True if extraction was successful
        """
        try:
            target_dir = target_dir or archive_path.parent
            logger.info(f"Extracting {archive_path} to {target_dir}")

            # Run unrar command
            result = subprocess.run(
                ['unrar', 'x', '-y', str(archive_path), str(target_dir)],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )

            if result.returncode == 0:
                self.stats.successful_extractions += 1
                return True
            else:
                logger.error(f"unrar failed with error: {result.stderr}")
                self.stats.failed_extractions += 1
                return False

        except Exception as e:
            logger.error(f"Error extracting RAR file {archive_path}: {str(e)}")
            self.stats.failed_extractions += 1
            return False
