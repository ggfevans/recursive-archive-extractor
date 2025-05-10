# Archive Processor

A Python script that recursively processes and extracts ZIP and RAR archives in a specified directory. The script provides detailed statistics about the processing operation and handles errors gracefully.

## Features

- Recursive directory traversal
- Supports both ZIP and RAR archives
- In-place extraction
- Detailed statistics tracking:
  - Directories processed
  - Compressed files found
  - Successful extractions
  - Failed extractions
- Error handling and logging
- Progress feedback during processing

## Requirements

- Python 3.x
- `unrar` command-line tool for RAR archive extraction

## Usage

```bash
python3 process_archives.py
```

By default, the script processes archives in the specified base directory. You can modify the base directory in the script.

## Example Output

```
Processing directory: /path/to/directory
Processing archive: example.zip
Successfully extracted: example.zip

=== Processing Summary ===
Directories processed: 10
Compressed files found: 5
Successful extractions: 5
Failed extractions: 0
```
