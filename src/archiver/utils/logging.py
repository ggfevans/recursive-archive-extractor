import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_file: Optional[Path] = None,
    log_level: int = logging.INFO,
    verbose: bool = False
) -> None:
    """Set up logging configuration.

    Args:
        log_file: Optional path to log file
        log_level: Logging level for file output
        verbose: If True, set console output to DEBUG level

    This configures both file and console logging with different formats
    and levels. Console logging is more concise, while file logging includes
    more details for debugging.
    """
    # Create logger
    logger = logging.getLogger("archiver")
    logger.setLevel(logging.DEBUG if verbose else log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else log_level)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False
