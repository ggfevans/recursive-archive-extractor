import pytest
import shutil
from pathlib import Path
import zipfile
import py7zr
import tarfile
from typing import Tuple

from archiver.extractors.nested import NestedArchiveHandler
from archiver.extractors.zip import ZipExtractor
from archiver.extractors.rar import RarExtractor
from archiver.extractors.seven_zip import SevenZipExtractor
from archiver.extractors.tar import TarExtractor

@pytest.fixture
def nested_handler(temp_dir):
    """Create a nested archive handler with all extractors."""
    extractors = [
        ZipExtractor(temp_dir),
        TarExtractor(temp_dir),
        SevenZipExtractor(temp_dir)
    ]
    try:
        extractors.append(RarExtractor(temp_dir))
    except RuntimeError:
        pass  # RAR support optional
    return NestedArchiveHandler(extractors, max_depth=3)

@pytest.fixture
def nested_test_files(temp_dir):
    """Create test files with nested archives."""
    # Create innermost files
    inner_dir = temp_dir / "inner"
    inner_dir.mkdir()
    (inner_dir / "inner1.txt").write_text("inner content 1")
    (inner_dir / "inner2.txt").write_text("inner content 2")

    # Create inner ZIP
    inner_zip = temp_dir / "inner.zip"
    with zipfile.ZipFile(inner_zip, 'w') as zf:
        zf.write(inner_dir / "inner1.txt", "inner1.txt")
        zf.write(inner_dir / "inner2.txt", "inner2.txt")

    # Create middle TAR containing the inner ZIP
    middle_tar = temp_dir / "middle.tar.gz"
    with tarfile.open(middle_tar, 'w:gz') as tf:
        tf.add(inner_zip, arcname="inner.zip")

    # Create outer 7Z containing the middle TAR
    outer_7z = temp_dir / "outer.7z"
    with py7zr.SevenZipFile(outer_7z, 'w') as archive:
        archive.write(middle_tar, "middle.tar.gz")

    return {
        'inner_zip': inner_zip,
        'middle_tar': middle_tar,
        'outer_7z': outer_7z,
    }

def print_directory_tree(path: Path, indent: str = ""):
    """Print a directory tree structure."""
    print(f"{indent}{path.name}/")
    try:
        for item in sorted(path.iterdir()):
            if item.is_dir():
                print_directory_tree(item, indent + "  ")
            else:
                print(f"{indent}  {item.name}")
    except Exception as e:
        print(f"{indent}  Error: {e}")

def create_nested_zip(base_path: Path, content: str, depth: int) -> Tuple[Path, Path]:
    """Create a series of nested ZIP files.

    Args:
        base_path: Base directory for creating files
        content: Content to put in the innermost file
        depth: Number of levels to create

    Returns:
        Tuple of (innermost file, outermost archive)
    """
    base_path.mkdir(exist_ok=True)
    
    # Create the content file
    content_file = base_path / "content.txt"
    content_file.write_text(content)
    
    # Create nested structure from innermost to outermost
    current_path = content_file
    
    # Create archives from deepest to outermost
    for i in range(depth - 1, -1, -1):
        archive_path = base_path / f"level_{i}.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.write(current_path, current_path.name)
        current_path = archive_path

    return content_file, current_path

def test_nested_handler_initialization(nested_handler):
    """Test nested handler initialization."""
    assert nested_handler.max_depth == 3
    assert nested_handler.verify_nested is True
    assert len(nested_handler.extractors) >= 3  # At least ZIP, TAR, and 7Z

def test_nested_handler_file_detection(nested_handler, nested_test_files):
    """Test archive file detection."""
    assert nested_handler._is_archive(nested_test_files['inner_zip'])
    assert nested_handler._is_archive(nested_test_files['middle_tar'])
    assert nested_handler._is_archive(nested_test_files['outer_7z'])
    assert not nested_handler._is_archive(Path("not_an_archive.txt"))

def test_nested_extraction_depth_limit(nested_handler, temp_dir):
    """Test maximum depth limit enforcement."""
    test_dir = temp_dir / "test_depth"
    content_file, archive = create_nested_zip(test_dir, "test content", nested_handler.max_depth)

    # Process the archives
    nested_handler.process_nested_archives(test_dir)

    # Print the directory structure for debugging
    print("\nActual directory structure:")
    print_directory_tree(test_dir)

    # Check first level extraction
    level_0_dir = test_dir / "level_0_extracted"
    assert level_0_dir.exists(), "First level not extracted"

    # Should contain the next archive and its extraction
    assert (level_0_dir / "level_1.zip").exists(), "Second level archive not found"
    level_1_dir = level_0_dir / "level_1_extracted"
    assert level_1_dir.exists(), "Second level not extracted"

    # Should contain the next archive and its extraction
    assert (level_1_dir / "level_2.zip").exists(), "Third level archive not found"
    level_2_dir = level_1_dir / "level_2_extracted"
    assert level_2_dir.exists(), "Third level not extracted"

    # Content should be at the deepest allowed level
    content_file = level_2_dir / "content.txt"
    assert content_file.exists(), "Content file not found"
    assert content_file.read_text() == "test content", "Content mismatch"

    # Verify no extraction beyond max depth
    final_level = level_2_dir.glob("*_extracted")
    assert not list(final_level), "Extraction exceeded maximum depth"

def test_nested_cycle_detection(nested_handler, temp_dir):
    """Test cycle detection in nested archives."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")

    archive1 = temp_dir / "archive1.zip"
    with zipfile.ZipFile(archive1, 'w') as zf:
        zf.write(test_file)

    archive2 = temp_dir / "archive2.zip"
    shutil.copy2(archive1, archive2)

    success, failed = nested_handler.process_nested_archives(temp_dir)
    assert success == 2  # Both archives should be processed once
    assert failed == 0

def test_multi_format_nested_extraction(nested_handler, nested_test_files, temp_dir):
    """Test extraction of nested archives in different formats."""
    extract_dir = temp_dir / "extract_test"
    extract_dir.mkdir()

    # Copy the outer archive to the extraction directory
    outer_archive = nested_test_files['outer_7z']
    target_archive = extract_dir / outer_archive.name
    shutil.copy2(outer_archive, target_archive)

    # Process the archive
    success, failed = nested_handler.process_nested_archives(extract_dir)
    assert success > 0
    assert failed == 0

    # Print the directory structure for debugging
    print("\nMulti-format directory structure:")
    print_directory_tree(extract_dir)

    # Verify inner files were extracted
    extracted_files = list(extract_dir.rglob("inner?.txt"))
    assert len(extracted_files) == 2
    
    content1 = next(f for f in extracted_files if f.name == "inner1.txt")
    content2 = next(f for f in extracted_files if f.name == "inner2.txt")
    
    assert content1.read_text() == "inner content 1"
    assert content2.read_text() == "inner content 2"
