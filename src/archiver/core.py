import logging
from pathlib import Path
from typing import List, Optional, Type

from .extractors.base import BaseExtractor
from .extractors.zip import ZipExtractor
from .extractors.rar import RarExtractor
from .utils.progress import ProgressTracker

logger = logging.getLogger(__name__)

class ArchiveProcessor:
    """Main class for processing archives in directories."""

    def __init__(
        self,
        base_dir: Path,
        extractors: Optional[List[Type[BaseExtractor]]] = None,
        dry_run: bool = False
    ):
        """Initialize the archive processor.

        Args:
            base_dir: Base directory to process
            extractors: Optional list of extractor classes to use
            dry_run: If True, don't actually extract archives
        """
        self.base_dir = Path(base_dir)
        self.dry_run = dry_run
        
        # Initialize extractors
        self.extractors = []
        extractor_classes = extractors or [ZipExtractor, RarExtractor]
        
        for extractor_class in extractor_classes:
            try:
                self.extractors.append(extractor_class(self.base_dir))
            except Exception as e:
                logger.warning(
                    f"Failed to initialize {extractor_class.__name__}: {e}"
                )

    def _get_extractor_for_file(self, file_path: Path) -> Optional[BaseExtractor]:
        """Get appropriate extractor for the given file.

        Args:
            file_path: Path to the file

        Returns:
            Matching extractor instance or None if no matching extractor
        """
        for extractor in self.extractors:
            if extractor.can_handle(file_path):
                return extractor
        return None

    def process_directory(self) -> dict:
        """Process all archives in the base directory recursively.

        Returns:
            Dictionary containing combined statistics from all extractors
        """
        logger.info(f"Starting archive processing in {self.base_dir}")
        
        # Track overall statistics
        total_stats = {
            "directories_processed": 0,
            "compressed_files_found": 0,
            "successful_extractions": 0,
            "failed_extractions": 0
        }

        # Walk through directories with progress bar
        for root, _, files in ProgressTracker.walk_with_progress(self.base_dir):
            current_dir = Path(root)
            archive_paths = []

            # Find archives in current directory
            for file in files:
                file_path = current_dir / file
                if self._get_extractor_for_file(file_path):
                    archive_paths.append(file_path)

            # Process found archives
            if archive_paths:
                logger.info(f"Found {len(archive_paths)} archives in {current_dir}")
                
                for archive_path in ProgressTracker.process_archives_with_progress(
                    archive_paths
                ):
                    extractor = self._get_extractor_for_file(archive_path)
                    if extractor:
                        if self.dry_run:
                            logger.info(f"[DRY RUN] Would extract: {archive_path}")
                        else:
                            extractor.extract(archive_path)

        # Combine statistics from all extractors
        for extractor in self.extractors:
            stats = extractor.get_stats()
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

        return total_stats
