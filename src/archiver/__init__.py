"""
recursive-archive-extractor: A tool for recursively extracting archives in directories
"""

from .core import ArchiveProcessor
from .extractors.base import BaseExtractor
from .extractors.zip import ZipExtractor
from .extractors.rar import RarExtractor

__version__ = "0.1.0"
__author__ = "ggfevans"
__author_email__ = "admin@local.host"

__all__ = [
    "ArchiveProcessor",
    "BaseExtractor",
    "ZipExtractor",
    "RarExtractor",
]
