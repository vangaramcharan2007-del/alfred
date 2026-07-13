from __future__ import annotations

import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.tesseract_client import TesseractClient


class TesseractProvider(BaseProvider):
    def __init__(self):
        self.client = TesseractClient()
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("VISION", "Tesseract", 10, True)
        
    async def check_health(self) -> bool:
        from jarvisx.clients.tesseract_client import HAVE_TESSERACT
        return HAVE_TESSERACT
        
    async def benchmark(self) -> float:
        from jarvisx.clients.tesseract_client import HAVE_TESSERACT
        return 100.0 if HAVE_TESSERACT else float('inf')


class FutureOCRProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("VISION", "Future OCR", 20, False)
        
    async def check_health(self) -> bool:
        return False
        
    async def benchmark(self) -> float:
        return float('inf')
