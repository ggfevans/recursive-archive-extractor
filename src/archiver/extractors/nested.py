import logging
from pathlib import Path
from typing import List, Optional, Set, Type
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
        return bool(self._get_extractor_for_file(path))

    def process_nested_archives(
        self,
        directory: Path,
        current_depth: int = 0
    ) -> tuple[int, int]:
        """Recursively process nested archives in a directory.

        Args:
            directory: Directory to process
            current_depth: Current recursion depth

        Returns:
            Tuple of (successful_extractions, failed_extractions)
        """
        if current_depth >= self.max_depth:
            logger.warning(f"Maximum depth {self.max_depth} reached at {directory}")
            return 0, 0

        successful = 0
        failed = 0

        # Process all files in the directory
        for item in directory.iterdir():
            if item.is_file() and self._is_archive(item):
                # Skip if we've seen this archive before (cycle detection)
                if item.resolve() in self.processed_archives:
                    logger.warning(f"Skipping previously processed archive: {item}")
                    continue

                self.processed_archives.add(item.resolve())
                extractor = self._get_extractor_for_file(item)
                
                if extractor:
                    logger.info(f"Processing nested archive at depth {current_depth}: {item}")
                    if extractor.extract(item):
                        successful += 1
                        # Recursively process the extraction directory
                        sub_success, sub_failed = self.process_nested_archives(
                            item.parent,
                            current_depth + 1
                        )
                        successful += sub_success
                        failed += sub_failed
                    else:
                        failed += 1

        return successful, failed
