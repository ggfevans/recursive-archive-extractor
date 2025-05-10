from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ArchiveConfig:
    """Configuration for archive processing."""
    # General settings
    base_dir: Path
    dry_run: bool = False
    verbose: bool = False
    log_file: Optional[Path] = None
    
    # Processing settings
    parallel_processing: bool = False
    max_workers: int = 4
    delete_after_extract: bool = False
    verify_integrity: bool = True
    
    # Nested archive settings
    process_nested: bool = False
    max_depth: int = 5
    verify_nested: bool = True
    
    # Archive-specific settings
    password: Optional[str] = None
    skip_existing: bool = True
    overwrite: bool = False
    
    # Format settings
    enable_zip: bool = True
    enable_rar: bool = True
    enable_7z: bool = True
    enable_tar: bool = True
    enable_tar_gz: bool = True
    enable_tar_bz2: bool = True
    enable_tar_xz: bool = True
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'ArchiveConfig':
        """Create configuration from a JSON file.

        Args:
            config_file: Path to JSON configuration file

        Returns:
            ArchiveConfig instance

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Convert path strings to Path objects
            if 'base_dir' in config_data:
                config_data['base_dir'] = Path(config_data['base_dir'])
            if 'log_file' in config_data and config_data['log_file']:
                config_data['log_file'] = Path(config_data['log_file'])
            
            return cls(**config_data)
        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise ValueError(f"Invalid configuration file: {e}")

    def to_file(self, config_file: Path) -> None:
        """Save configuration to a JSON file.

        Args:
            config_file: Path to save configuration to
        """
        config_data = {
            k: str(v) if isinstance(v, Path) else v
            for k, v in self.__dict__.items()
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(self.base_dir, Path):
            raise ValueError("base_dir must be a Path object")
        
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        
        if self.max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        
        if self.log_file and not isinstance(self.log_file, Path):
            raise ValueError("log_file must be a Path object")
        
        # Validate base_dir exists if not in dry run mode
        if not self.dry_run and not self.base_dir.exists():
            raise ValueError(f"base_dir does not exist: {self.base_dir}")
        
        # Ensure at least one format is enabled
        if not any([
            self.enable_zip,
            self.enable_rar,
            self.enable_7z,
            self.enable_tar,
            self.enable_tar_gz,
            self.enable_tar_bz2,
            self.enable_tar_xz
        ]):
            raise ValueError("At least one archive format must be enabled")

    def merge(self, other: Dict[str, Any]) -> None:
        """Merge additional configuration settings.

        Args:
            other: Dictionary of configuration values to merge
        """
        for key, value in other.items():
            if hasattr(self, key):
                setattr(self, key, value)
