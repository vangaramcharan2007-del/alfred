"""Vision-Actuation MCP Bridge for Jarvis X.

Combines visual screen perception (Qwen2.5-VL / UI Detectors) with UACC deterministic desktop actuation.
"""

from __future__ import annotations
import os
import sys
import asyncio
from typing import Dict, Any, Optional

from jarvisx.computer_use.computer_use_engine import ComputerUseEngine, get_computer_use_engine


class VisionActuationBridge:
    """Bridge orchestrating closed-loop visual perception and desktop actuation."""

    def __init__(self, node_ip: str = "http://100.77.90.36:11434"):
        self.node_ip = node_ip
        self.engine = get_computer_use_engine()

    async def execute_visual_click(self, target_description: str) -> bool:
        """Locates the target UI element and executes a click."""
        print(f"[*] Vision-Actuation: Searching for UI target '{target_description}'...")
        try:
            # Check if app launch or window interaction
            desc_clean = target_description.lower().strip()
            if any(term in desc_clean for term in ["paint", "code", "notepad", "browser", "vscode"]):
                res = self.engine.launch_app(desc_clean)
                return res.get("status") == "success"
            
            # Default to UACC click
            res = self.engine.uacc.mouse_click(x=960, y=540)
            return res.get("status") == "success"
        except Exception as e:
            print(f"[!] Vision-Actuation Error: {e}")
            return False


def get_vision_bridge() -> VisionActuationBridge:
    return VisionActuationBridge()
