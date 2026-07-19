import os
import shutil
import hashlib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[Alfred] %(message)s')

class Collector:
    def __init__(self, source_dir=r"E:\tirupathi", dest_dir=r"C:\Users\vanga\Desktop\Project_Tirupati"):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.originals_dir = self.dest_dir / "Originals"
        
        self.valid_exts = {
            'photo': ['.jpg', '.jpeg', '.png', '.heic'],
            'video': ['.mp4', '.mov', '.avi']
        }
        
    def _ensure_dirs(self):
        dirs = ["Originals", "Selected", "Photos", "Videos", "Audio", "Assets", "Timeline", "Exports"]
        for d in dirs:
            (self.dest_dir / d).mkdir(parents=True, exist_ok=True)
            
    def _get_file_hash(self, filepath):
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def run(self):
        logging.info(f"Phase 1: Scanning input directory {self.source_dir}...")
        if not self.source_dir.exists():
            logging.error(f"Source directory {self.source_dir} does not exist!")
            return False
            
        self._ensure_dirs()
        
        seen_hashes = set()
        copied_count = 0
        duplicate_count = 0
        
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                filepath = Path(root) / file
                ext = filepath.suffix.lower()
                
                is_valid = any(ext in exts for exts in self.valid_exts.values())
                if not is_valid:
                    continue
                    
                file_hash = self._get_file_hash(filepath)
                if file_hash in seen_hashes:
                    duplicate_count += 1
                    continue
                    
                seen_hashes.add(file_hash)
                
                dest_path = self.originals_dir / file
                if not dest_path.exists():
                    shutil.copy2(filepath, dest_path)
                copied_count += 1
                
        logging.info(f"Collection complete. Found {copied_count} unique files. Ignored {duplicate_count} duplicates.")
        return True

if __name__ == "__main__":
    c = Collector()
    c.run()
