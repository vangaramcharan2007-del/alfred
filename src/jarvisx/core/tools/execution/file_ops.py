import shutil
from pathlib import Path
import logging
from typing import List, Optional
from .permissions import PermissionManager, TrustLevel

logger = logging.getLogger(__name__)

class FileOps:
    @staticmethod
    def check_permissions():
        PermissionManager.check_permission(TrustLevel.LEVEL_1_FILES)

    @staticmethod
    def create_file(filepath: str, content: str = "") -> bool:
        FileOps.check_permissions()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        logger.info(f"Created file: {filepath}")
        return True

    @staticmethod
    def read_file(filepath: str) -> Optional[str]:
        FileOps.check_permissions()
        path = Path(filepath)
        if path.exists() and path.is_file():
            return path.read_text(encoding='utf-8')
        return None

    @staticmethod
    def write_file(filepath: str, content: str) -> bool:
        return FileOps.create_file(filepath, content)

    @staticmethod
    def move_file(src: str, dest: str) -> bool:
        FileOps.check_permissions()
        shutil.move(src, dest)
        logger.info(f"Moved {src} to {dest}")
        return True

    @staticmethod
    def copy_file(src: str, dest: str) -> bool:
        FileOps.check_permissions()
        shutil.copy2(src, dest)
        logger.info(f"Copied {src} to {dest}")
        return True

    @staticmethod
    def delete_file(filepath: str) -> bool:
        FileOps.check_permissions()
        path = Path(filepath)
        if path.exists():
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            logger.info(f"Deleted {filepath}")
            return True
        return False

    @staticmethod
    def search_files(directory: str, pattern: str) -> List[str]:
        FileOps.check_permissions()
        path = Path(directory)
        return [str(p) for p in path.rglob(pattern)]

    @staticmethod
    def create_directory(directory: str) -> bool:
        FileOps.check_permissions()
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
        return True
