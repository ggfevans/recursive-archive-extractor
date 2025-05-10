import logging
from pathlib import Path
import sys
import click

from .core import ArchiveProcessor
from .utils.logging import setup_logging

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
def main(
    directory: Path,
    verbose: bool,
    dry_run: bool,
    log_file: Path | None
) -> None:
    """
    Recursively extract archives in the specified directory.

    DIRECTORY: The target directory to process
    """
    try:
        # Set up logging
        setup_logging(
            log_file=log_file,
            verbose=verbose
        )

        # Create and run processor
        processor = ArchiveProcessor(
            base_dir=directory,
            dry_run=dry_run
        )

        # Process archives and get statistics
        stats = processor.process_directory()

        # Print summary
        click.echo("\n=== Processing Summary ===")
        click.echo(f"Directories processed: {stats['directories_processed']}")
        click.echo(f"Compressed files found: {stats['compressed_files_found']}")
        click.echo(f"Successful extractions: {stats['successful_extractions']}")
        click.echo(f"Failed extractions: {stats['failed_extractions']}")

        # Exit with error if any extractions failed
        if stats['failed_extractions'] > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
