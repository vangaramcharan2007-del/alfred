import asyncio
import json
import unittest

from jarvisx.adapters.vision_interface import VisionManager, VisionProvider
from jarvisx.runtime import create_default_runtime


class VisionInterfaceTests(unittest.TestCase):
    def test_vision_extraction(self) -> None:
        provider = VisionProvider()
        # Test default fallback
        text1 = provider.extract_context(b"not json")
        self.assertEqual(text1, "Simulated visual context extracted from image.")
        
        # Test simulated JSON payload
        payload = json.dumps({"context": "A picture of a cat"}).encode("utf-8")
        text2 = provider.extract_context(payload)
        self.assertEqual(text2, "A picture of a cat")

    def test_vision_forces_tier_2(self) -> None:
        runtime = create_default_runtime()
        # Normally "open youtube" is tier_1_fast
        response = asyncio.run(runtime.alfred.process("open youtube", has_image=True))
        
        # Because has_image=True, it should be tier_2_reasoning
        self.assertEqual(response.model["tier"], "tier_2_reasoning")

    def test_vision_manager_integration(self) -> None:
        runtime = create_default_runtime()
        manager = VisionManager(runtime)
        
        payload = json.dumps({"context": "A complex image payload that requires thinking"}).encode("utf-8")
        raw_response = asyncio.run(manager.process_image_input(payload))
        
        response_data = json.loads(raw_response.decode("utf-8"))
        # Check that Alfred processed it and routed it via reasoning model
        self.assertEqual(response_data["model"]["tier"], "tier_2_reasoning")


if __name__ == "__main__":
    unittest.main()
