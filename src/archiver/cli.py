import logging
from pathlib import Path
import sys
import click

from .core import ArchiveProcessor
from .utils.logging import setup_logging
from .utils.config import ArchiveConfig

@click.command()
@click.argument(
    'directory',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be done without actually extracting'
)
@click.option(
    '--log-file',
    type=click.Path(dir_okay=False, path_type=Path),
    help='Log file to write to'
)
@click.option(
    '--config',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to configuration file'
)
# Processing options
@click.option(
    '--parallel/--no-parallel',
    default=False,
    help='Enable parallel processing of archives'
)
@click.option(
    '--max-workers',
    type=int,
    default=4,
    help='Maximum number of parallel workers'
)
@click.option(
    '--delete-after/--no-delete-after',
    default=False,
    help='Delete archives after successful extraction'
)
@click.option(
    '--verify/--no-verify',
    default=True,
    help='Verify archive integrity before extraction'
)
# Nested archive options
@click.option(
    '--process-nested/--no-process-nested',
    default=False,
    help='Process archives found within extracted archives'
)
@click.option(
    '--max-depth',
    type=int,
    default=5,
    help='Maximum depth for nested archive processing'
)
# Format options
@click.option(
    '--enable-zip/--disable-zip',
    default=True,
    help='Enable/disable ZIP format support'
)
@click.option(
    '--enable-rar/--disable-rar',
    default=True,
    help='Enable/disable RAR format support'
)
@click.option(
    '--enable-7z/--disable-7z',
    default=True,
    help='Enable/disable 7Z format support'
)
@click.option(
    '--enable-tar/--disable-tar',
    default=True,
    help='Enable/disable TAR format support'
)
# Archive-specific options
@click.option(
    '--skip-existing/--no-skip-existing',
    default=True,
    help='Skip extraction if files already exist'
)
@click.option(
    '--password',
    help='Password for encrypted archives'
)
def main(
    directory: Path,
    verbose: bool,
    dry_run: bool,
    log_file: Path | None,
    config: Path | None,
    parallel: bool,
    max_workers: int,
    delete_after: bool,
    verify: bool,
    process_nested: bool,
    max_depth: int,
    enable_zip: bool,
    enable_rar: bool,
    enable_7z: bool,
    enable_tar: bool,
    skip_existing: bool,
    password: str | None,
) -> None:
    """
    Recursively extract archives in the specified directory.

    DIRECTORY: The target directory to process
    """
    try:
        # Initialize configuration
        if config:
            # Load from config file
            config_obj = ArchiveConfig.from_file(config)
            # Override with command line arguments
            config_obj.merge({
                'base_dir': directory,
                'verbose': verbose,
                'dry_run': dry_run,
                'log_file': log_file,
                'parallel_processing': parallel,
                'max_workers': max_workers,
                'delete_after_extract': delete_after,
                'verify_integrity': verify,
                'process_nested': process_nested,
                'max_depth': max_depth,
                'enable_zip': enable_zip,
                'enable_rar': enable_rar,
                'enable_7z': enable_7z,
                'enable_tar': enable_tar,
                'skip_existing': skip_existing,
                'password': password,
            })
        else:
            # Create config from command line arguments
            config_obj = ArchiveConfig(
                base_dir=directory,
                dry_run=dry_run,
                verbose=verbose,
                log_file=log_file,
                parallel_processing=parallel,
                max_workers=max_workers,
                delete_after_extract=delete_after,
                verify_integrity=verify,
                process_nested=process_nested,
                max_depth=max_depth,
                enable_zip=enable_zip,
                enable_rar=enable_rar,
                enable_7z=enable_7z,
                enable_tar=enable_tar,
                skip_existing=skip_existing,
                password=password,
            )

        # Validate configuration
        config_obj.validate()

        # Set up logging
        setup_logging(
            log_file=config_obj.log_file,
            verbose=config_obj.verbose
        )

        # Create and run processor
        processor = ArchiveProcessor(config=config_obj)
        stats = processor.process_directory()

        # Print summary
        click.echo("\n=== Processing Summary ===")
        click.echo(f"Directories processed: {stats['directories_processed']}")
        click.echo(f"Compressed files found: {stats['compressed_files_found']}")
        click.echo(f"Successful extractions: {stats['successful_extractions']}")
        click.echo(f"Failed extractions: {stats['failed_extractions']}")
        if 'nested_archives_processed' in stats:
            click.echo(f"Nested archives processed: {stats['nested_archives_processed']}")

        # Exit with error if any extractions failed
        if stats['failed_extractions'] > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
