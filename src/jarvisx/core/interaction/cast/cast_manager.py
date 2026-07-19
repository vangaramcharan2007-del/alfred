from .cast_dlna import DLNACastAdapter
import logging

class CastManager:
    """
    Manages casting media to TVs.
    """
    def __init__(self, backend="dlna"):
        if backend == "dlna":
            self.adapter = DLNACastAdapter()
        else:
            logging.warning(f"Unknown cast backend: {backend}. TV casting disabled.")
            self.adapter = None
            
    def cast(self, media_path: str):
        if not self.adapter:
            return False
            
        try:
            return self.adapter.discover_and_cast(media_path)
        except Exception as e:
            logging.error(f"Cast subsystem encountered an error: {e}. Gracefully continuing locally.")
            return False
