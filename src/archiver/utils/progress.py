from pathlib import Path
from typing import Iterator, List
from tqdm import tqdm
import os

class ProgressTracker:
    """Handles progress tracking for archive operations."""

    @staticmethod
    def count_directories(base_dir: Path) -> int:
        """Count total number of directories for progress tracking.

        Args:
            base_dir: Base directory to start counting from

        Returns:
            Total number of directories
        """
        return sum(1 for _ in base_dir.rglob("*") if _.is_dir())

    @staticmethod
    def walk_with_progress(
        base_dir: Path,
        desc: str = "Scanning directories"
    ) -> Iterator[tuple[str, List[str], List[str]]]:
        """Generator that yields os.walk results with a progress bar.

        Args:
            base_dir: Base directory to walk
            desc: Description for the progress bar

        Yields:
            Same as os.walk: (dirpath, dirnames, filenames)
        """
        total_dirs = ProgressTracker.count_directories(base_dir)
        
        with tqdm(total=total_dirs, desc=desc) as pbar:
            for root, dirs, files in os.walk(base_dir):
                pbar.update(1)
                yield root, dirs, files

    @staticmethod
    def process_archives_with_progress(
        archives: List[Path],
        desc: str = "Extracting archives"
    ) -> Iterator[Path]:
        """Process archives with a progress bar.

        Args:
            archives: List of archive paths to process
            desc: Description for the progress bar

        Yields:
            Each archive path in turn
        """
        with tqdm(archives, desc=desc) as pbar:
            for archive in pbar:
                pbar.set_postfix(file=archive.name)
                yield archive
