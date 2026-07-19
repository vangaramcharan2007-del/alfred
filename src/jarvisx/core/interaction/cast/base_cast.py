from abc import ABC, abstractmethod

class BaseCastAdapter(ABC):
    """
    Abstract Base Class for TV Cast Engine Adapters.
    """
    
    @abstractmethod
    def discover_and_cast(self, media_path: str) -> bool:
        """
        Attempt to discover the TV and cast the media.
        Returns True if successful, False otherwise.
        """
        pass
