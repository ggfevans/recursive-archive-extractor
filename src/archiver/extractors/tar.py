import logging
import tarfile
from pathlib import Path
from typing import Optional

from .base import BaseExtractor

logger = logging.getLogger(__name__)

class TarExtractor(BaseExtractor):
    """Extractor for tar archives (including compressed variants)."""

    def __init__(self, base_dir: Path):
        """Initialize the tar extractor.

        Args:
            base_dir: Base directory for extraction operations
        """
        super().__init__(base_dir)

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Return supported file extensions.

        Returns:
            Tuple containing supported extensions
        """
        return (
            '.tar',
            '.tar.gz', '.tgz',
            '.tar.bz2', '.tbz2',
            '.tar.xz', '.txz'
        )

    def _is_safe_path(self, path: str, target_dir: Path) -> bool:
        """Check if the extraction path is safe (no path traversal).

        Args:
            path: Path to check
            target_dir: Target directory for extraction

        Returns:
            True if path is safe
        """
        try:
            extraction_path = (target_dir / path).resolve()
            common_prefix = Path(target_dir).resolve()
            return common_prefix in extraction_path.parents
        except Exception:
            return False

    def verify_integrity(self, archive_path: Path) -> bool:
        """Verify the integrity of a tar archive.

        Args:
            archive_path: Path to the archive file

        Returns:
            True if archive is valid
        """
        try:
            with tarfile.open(archive_path, 'r:*') as tar:
                # Try to read and verify the entire archive
                for member in tar:
                    if not member.name:
                        return False
                    if not self._is_safe_path(member.name, archive_path.parent):
                        logger.error(f"Unsafe path detected in archive: {member.name}")
                        return False
                return True
        except Exception as e:
            logger.error(f"Failed to verify tar archive {archive_path}: {e}")
            return False

    def extract(self, archive_path: Path, target_dir: Optional[Path] = None) -> bool:
        """Extract a tar archive.

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
            with tarfile.open(archive_path, 'r:*') as tar:
                # Filter out unsafe paths
                members = [m for m in tar if self._is_safe_path(m.name, target_dir)]
                tar.extractall(path=target_dir, members=members)
                
                self.stats.successful_extractions += 1
                return True

        except Exception as e:
            logger.error(f"Error extracting tar file {archive_path}: {str(e)}")
            self.stats.failed_extractions += 1
            return False

    def get_compression_type(self, archive_path: Path) -> str:
        """Determine the compression type of the tar archive.

        Args:
            archive_path: Path to the archive file

        Returns:
            String describing the compression type
        """
        suffix = archive_path.suffix.lower()
        if suffix in ('.gz', '.tgz'):
            return 'gzip'
        elif suffix in ('.bz2', '.tbz2'):
            return 'bzip2'
        elif suffix in ('.xz', '.txz'):
            return 'lzma'
        return 'none'
