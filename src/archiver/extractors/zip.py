import logging
from pathlib import Path
from typing import Optional
import zipfile

from .base import BaseExtractor

logger = logging.getLogger(__name__)

class ZipExtractor(BaseExtractor):
    """Extractor for ZIP archives."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Return supported file extensions.

        Returns:
            Tuple containing .zip extension
        """
        return ('.zip',)

    def extract(self, archive_path: Path, target_dir: Optional[Path] = None) -> bool:
        """Extract a ZIP archive.

        Args:
            archive_path: Path to the ZIP archive
            target_dir: Optional target directory. If None, extract to archive's directory

        Returns:
            True if extraction was successful
        """
        try:
            target_dir = target_dir or archive_path.parent
            logger.info(f"Extracting {archive_path} to {target_dir}")

            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Verify archive integrity
                try:
                    zip_ref.testzip()
                except zipfile.BadZipFile as e:
                    logger.error(f"Archive {archive_path} is corrupted: {e}")
                    self.stats.failed_extractions += 1
                    return False

                # Extract the archive
                zip_ref.extractall(path=target_dir)
                self.stats.successful_extractions += 1
                return True

        except Exception as e:
            logger.error(f"Error extracting ZIP file {archive_path}: {str(e)}")
            self.stats.failed_extractions += 1
            return False
