import os
from abc import ABC, abstractmethod
from typing import Dict, Any

class DocumentConverterBase(ABC):
    """Base class for all document converters in Jarvis X."""

    @abstractmethod
    def convert(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """
        Converts the source document to the destination format.
        
        Args:
            source_path: Path to the input file.
            destination_path: Path to save the output file.
            
        Returns:
            Dictionary containing metrics and metadata about the conversion.
        """
        pass

    @abstractmethod
    def validate(self, destination_path: str) -> bool:
        """
        Validates the output document (e.g. checks for corruption, correct sheet counts, etc.).
        """
        pass
