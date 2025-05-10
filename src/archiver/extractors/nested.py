import logging
import shutil
from pathlib import Path
from typing import List, Set, Tuple, Optional, Type, Dict

from .base import BaseExtractor

logger = logging.getLogger(__name__)

class NestedArchiveHandler:
    """Handler for processing nested archives."""

    def __init__(
        self,
        extractors: List[BaseExtractor],
        max_depth: int = 5,
        verify_nested: bool = True
    ):
        """Initialize nested archive handler.

        Args:
            extractors: List of available extractors
            max_depth: Maximum recursion depth for nested archives
            verify_nested: Whether to verify nested archives
        """
        self.extractors = extractors
        self.max_depth = max_depth
        self.verify_nested = verify_nested
        self.processed_archives: Set[Path] = set()
        self.success_within_depth = 0
        self.total_failed = 0

    def _get_extractor_for_file(self, file_path: Path) -> Optional[BaseExtractor]:
        """Get appropriate extractor for the given file.

        Args:
            file_path: Path to check

        Returns:
            Matching extractor or None
        """
        for extractor in self.extractors:
            if extractor.can_handle(file_path):
                return extractor
        return None

    def _is_archive(self, path: Path) -> bool:
        """Check if a path is an archive file.

        Args:
            path: Path to check

        Returns:
            True if path is an archive file
        """
        try:
            return bool(self._get_extractor_for_file(path))
        except Exception:
            return False

    def _reset_stats(self):
        """Reset extraction statistics."""
        self.success_within_depth = 0
        self.total_failed = 0
        self.processed_archives.clear()

    def process_nested_archives(
        self,
        directory: Path,
        current_depth: int = 0,
        reset_stats: bool = True
    ) -> Tuple[int, int]:
        """Recursively process nested archives in a directory.

        Args:
            directory: Directory to process
            current_depth: Current recursion depth
            reset_stats: Whether to reset statistics before processing

        Returns:
            Tuple of (successful_extractions, failed_extractions)
        """
        if reset_stats:
            self._reset_stats()

        try:
            directory = Path(directory)
            if not directory.exists():
                logger.error(f"Directory does not exist: {directory}")
                return self.success_within_depth, self.total_failed

            if current_depth >= self.max_depth:
                logger.warning(f"Maximum depth {self.max_depth} reached at {directory}")
                return self.success_within_depth, self.total_failed

            # Process all files in directory (non-recursively)
            for item in directory.iterdir():
                if not item.is_file():
                    continue

                if not self._is_archive(item):
                    continue

                # Skip if we've seen this archive before (cycle detection)
                resolved_path = item.resolve()
                if resolved_path in self.processed_archives:
                    logger.warning(f"Skipping previously processed archive: {item}")
                    continue

                self.processed_archives.add(resolved_path)
                extractor = self._get_extractor_for_file(item)

                if extractor:
                    extract_dir = item.parent / f"{item.stem}_extracted"
                    extract_dir.mkdir(exist_ok=True)
                    logger.info(f"Processing archive at depth {current_depth}: {item}")

                    if extractor.extract(item, extract_dir):
                        self.success_within_depth += 1
                        if current_depth < self.max_depth - 1:
                            # Recursively process the extraction directory
                            self.process_nested_archives(
                                extract_dir,
                                current_depth + 1,
                                reset_stats=False
                            )
                    else:
                        self.total_failed += 1

            # Process subdirectories at current level
            for subdir in directory.iterdir():
                if subdir.is_dir() and not subdir.name.endswith('_extracted'):
                    self.process_nested_archives(
                        subdir,
                        current_depth,
                        reset_stats=False
                    )

        except Exception as e:
            logger.error(f"Error processing directory {directory}: {e}")
            self.total_failed += 1

        return self.success_within_depth, self.total_failed
