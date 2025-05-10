import os
import zipfile
import subprocess
from pathlib import Path

class ArchiveProcessor:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.stats = {
            'directories_processed': 0,
            'compressed_files_found': 0,
            'successful_extractions': 0,
            'failed_extractions': 0
        }

    def extract_zip(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(path=os.path.dirname(zip_path))
            return True
        except Exception as e:
            print(f"Error extracting ZIP file {zip_path}: {str(e)}")
            return False

    def extract_rar(self, rar_path):
        try:
            result = subprocess.run(['unrar', 'x', '-y', rar_path, os.path.dirname(rar_path)],
                                capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error extracting RAR file {rar_path}: {str(e)}")
            return False

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
                
                if success:
                    self.stats['successful_extractions'] += 1
                    print(f"Successfully extracted: {archive}")
                else:
                    self.stats['failed_extractions'] += 1
                    print(f"Failed to extract: {archive}")

    def print_summary(self):
        print("\n=== Processing Summary ===")
        print(f"Directories processed: {self.stats['directories_processed']}")
        print(f"Compressed files found: {self.stats['compressed_files_found']}")
        print(f"Successful extractions: {self.stats['successful_extractions']}")
        print(f"Failed extractions: {self.stats['failed_extractions']}")

if __name__ == "__main__":
    processor = ArchiveProcessor("/mnt/user/data/torrents/download/readarr")
    processor.process_directory()
    processor.print_summary()
