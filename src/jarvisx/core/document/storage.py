import os
import shutil
import hashlib

class DocumentStorage:
    """Manages file storage, prevents duplicates, and provides temporary directories."""
    
    def __init__(self, base_dir: str = None):
        if not base_dir:
            self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_WhatsApp_Automation")
        else:
            self.base_dir = base_dir
            
        self.inbox_dir = os.path.join(self.base_dir, "Inbox")
        self.outbox_dir = os.path.join(self.base_dir, "Outbox")
        self.archive_dir = os.path.join(self.base_dir, "Archive")
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        for d in [self.base_dir, self.inbox_dir, self.outbox_dir, self.archive_dir]:
            os.makedirs(d, exist_ok=True)
            
    def _compute_hash(self, filepath: str) -> str:
        h = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def is_duplicate(self, filepath: str) -> bool:
        """Checks if the file has already been processed by comparing hashes in the Archive."""
        file_hash = self._compute_hash(filepath)
        if not file_hash:
            return False
            
        for root, _, files in os.walk(self.archive_dir):
            for file in files:
                archived_path = os.path.join(root, file)
                if self._compute_hash(archived_path) == file_hash:
                    return True
        return False
        
    def archive_source(self, filepath: str):
        """Moves the original file to the archive to prevent reprocessing."""
        filename = os.path.basename(filepath)
        dest = os.path.join(self.archive_dir, filename)
        
        # Handle filename collisions in archive
        counter = 1
        while os.path.exists(dest):
            name, ext = os.path.splitext(filename)
            dest = os.path.join(self.archive_dir, f"{name}_{counter}{ext}")
            counter += 1
            
        shutil.move(filepath, dest)
        return dest
