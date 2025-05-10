# LLM Instructions for Improving the Recursive Archive Extractor

## Repository Overview
This repository contains a Python tool designed to recursively traverse directories, find compressed files (ZIP, RAR), and automatically extract them. The primary use case is handling media downloads that contain compressed files, particularly for applications like Readarr that cannot natively extract these archives.

## Current Implementation
The current implementation includes:
- A Python script (`process_archives.py`) with an `ArchiveProcessor` class
- Support for ZIP and RAR archives
- Basic statistics tracking (directories processed, files found, extraction successes/failures)
- Simple command-line execution with a hardcoded directory path

## Improvement Tasks

### 1. Project Structure and Organization
- [ ] Create a proper Python package structure
- [ ] Implement a modular design with separate files for different functionalities
- [ ] Add appropriate `__init__.py` files
- [ ] Create a setup.py file for pip installation
- [ ] Organize code according to separation of concerns

### 2. Command-Line Interface
- [ ] Implement a robust CLI using argparse or click
- [ ] Add command-line options for:
  - [ ] Target directory
  - [ ] Include/exclude patterns
  - [ ] Verbosity level
  - [ ] Dry-run mode
  - [ ] Post-extraction options (delete archives, move archives, etc.)
  - [ ] Handling conflicts (skip, overwrite, rename)

### 3. Functionality Enhancements
- [ ] Support additional archive formats (7z, tar, tar.gz, tar.bz2, etc.)
- [ ] Add parallel processing for improved performance
- [ ] Implement progress tracking (especially for large directory structures)
- [ ] Add support for password-protected archives
- [ ] Handle nested archives (archives within archives)
- [ ] Add file integrity verification
- [ ] Implement retry logic for failed extractions

### 4. Error Handling and Logging
- [ ] Replace print statements with proper logging
- [ ] Add configurable log levels
- [ ] Implement comprehensive error handling
- [ ] Add detailed error messages and suggestions
- [ ] Create crash reports or logs for troubleshooting

### 5. Testing
- [ ] Develop unit tests for core functionality
- [ ] Create integration tests for end-to-end workflows
- [ ] Implement test fixtures with sample archives
- [ ] Add CI/CD configuration (.github/workflows)
- [ ] Ensure test coverage across different platforms (Windows, Linux, macOS)

### 6. Documentation
- [ ] Create a comprehensive README.md
- [ ] Write installation instructions
- [ ] Provide usage examples
- [ ] Document all command-line options
- [ ] Add docstrings for all functions and classes
- [ ] Create CONTRIBUTING.md guidelines
- [ ] Add a LICENSE file (suggest MIT or GPL)

### 7. Configuration
- [ ] Implement configuration file support
- [ ] Allow for directory-specific settings
- [ ] Support environment variables
- [ ] Create sensible defaults
- [ ] Allow for user profiles or presets

### 8. Performance Optimization
- [ ] Optimize directory traversal
- [ ] Add memory usage constraints
- [ ] Implement batch processing for large directories
- [ ] Add benchmarking capabilities
- [ ] Optimize for various system configurations

### 9. User Experience
- [ ] Add colorized output
- [ ] Implement progress bars (using tqdm or similar)
- [ ] Create summary reports
- [ ] Add interactive mode for handling edge cases
- [ ] Provide helpful warnings and suggestions

### 10. Integration
- [ ] Add hooks for integration with media managers (Readarr, Sonarr, etc.)
- [ ] Create plugins system for extensibility
- [ ] Support notifications (email, webhooks, etc.)
- [ ] Add scheduler functionality
- [ ] Provide an API for programmatic use

## Code Quality Guidelines
- Follow PEP 8 style guidelines
- Use type hints for better code understanding
- Write clear, concise docstrings
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names
- Apply SOLID principles where appropriate
- Minimize dependencies while maximizing functionality

## Example Improvements

### Current Code (excerpt):
```python
def process_directory(self):
    for root, dirs, files in os.walk(self.base_dir):
        self.stats['directories_processed'] += 1
        print(f"\nProcessing directory: {root}")
        
        archives = [f for f in files if f.lower().endswith(('.zip', '.rar'))]
        self.stats['compressed_files_found'] += len(archives)
        
        for archive in archives:
            full_path = os.path.join(root, archive)
            print(f"Processing archive: {archive}")
            
            success = False
            if archive.lower().endswith('.zip'):
                success = self.extract_zip(full_path)
            elif archive.lower().endswith('.rar'):
                success = self.extract_rar(full_path)
```

### Improved Version (example):
```python
def process_directory(self) -> None:
    """
    Recursively process directories and extract archives.
    Shows progress with tqdm and uses logging instead of print statements.
    """
    self.logger.info(f"Starting processing in {self.base_dir}")
    
    # Get total directory count for progress bar
    dir_count = sum(1 for _ in os.walk(self.base_dir))
    
    for root, dirs, files in tqdm(os.walk(self.base_dir), total=dir_count, desc="Processing directories"):
        self.stats['directories_processed'] += 1
        self.logger.debug(f"Processing directory: {root}")
        
        # Filter by configured patterns
        archives = self._find_archives_in_directory(files)
        self.stats['compressed_files_found'] += len(archives)
        
        if not archives:
            continue
            
        # Use thread pool for parallel extraction
        if self.use_parallel and len(archives) > 1:
            self._extract_archives_parallel(root, archives)
        else:
            self._extract_archives_sequential(root, archives)
```

## Priorities
1. Create a user-friendly CLI
2. Implement proper error handling and logging
3. Add support for more archive formats
4. Develop comprehensive tests
5. Write quality documentation

Approach these improvements incrementally, testing each change thoroughly before moving to the next.
