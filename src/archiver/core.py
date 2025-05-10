import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Type

from .extractors.base import BaseExtractor
from .extractors.zip import ZipExtractor
from .extractors.rar import RarExtractor
from .utils.progress import ProgressTracker
from .utils.config import ArchiveConfig

logger = logging.getLogger(__name__)

class ArchiveProcessor:
    """Main class for processing archives in directories."""

    def __init__(
        self,
        config: ArchiveConfig,
        extractors: Optional[List[Type[BaseExtractor]]] = None
    ):
        """Initialize the archive processor.

        Args:
            config: Configuration settings
            extractors: Optional list of extractor classes to use
        """
        self.config = config
        self.config.validate()
        
        # Initialize extractors
        self.extractors = []
        extractor_classes = extractors or [ZipExtractor, RarExtractor]
        
        for extractor_class in extractor_classes:
            try:
                self.extractors.append(extractor_class(self.config.base_dir))
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

    def _process_single_archive(self, archive_path: Path) -> bool:
        """Process a single archive file.

        Args:
            archive_path: Path to the archive file

        Returns:
            True if extraction was successful
        """
        extractor = self._get_extractor_for_file(archive_path)
        if not extractor:
            logger.warning(f"No suitable extractor found for {archive_path}")
            return False

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would extract: {archive_path}")
            return True

        success = extractor.extract(archive_path)
        
        if success and self.config.delete_after_extract:
            try:
                archive_path.unlink()
                logger.info(f"Deleted archive after extraction: {archive_path}")
            except Exception as e:
                logger.error(f"Failed to delete archive {archive_path}: {e}")

        return success

    def process_directory(self) -> dict:
        """Process all archives in the base directory recursively.

        Returns:
            Dictionary containing combined statistics from all extractors
        """
        logger.info(f"Starting archive processing in {self.config.base_dir}")
        
        # Track overall statistics
        total_stats = {
            "directories_processed": 0,
            "compressed_files_found": 0,
            "successful_extractions": 0,
            "failed_extractions": 0
        }

        # Walk through directories with progress bar
        for root, _, files in ProgressTracker.walk_with_progress(self.config.base_dir):
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
                
                if self.config.parallel_processing and len(archive_paths) > 1:
                    # Process archives in parallel
                    with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                        future_to_archive = {
                            executor.submit(self._process_single_archive, archive): archive
                            for archive in archive_paths
                        }
                        
                        for future in ProgressTracker.process_archives_with_progress(
                            as_completed(future_to_archive)
                        ):
                            archive = future_to_archive[future]
                            try:
                                success = future.result()
                                if success:
                                    logger.debug(f"Successfully processed {archive}")
                                else:
                                    logger.error(f"Failed to process {archive}")
                            except Exception as e:
                                logger.error(f"Error processing {archive}: {e}")
                else:
                    # Process archives sequentially
                    for archive_path in ProgressTracker.process_archives_with_progress(
                        archive_paths
                    ):
                        self._process_single_archive(archive_path)

        # Combine statistics from all extractors
        for extractor in self.extractors:
            stats = extractor.get_stats()
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)

        return total_stats
