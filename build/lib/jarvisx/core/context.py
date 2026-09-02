from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field


@dataclass
class DeviceContext:
    platform_name: str = field(default_factory=platform.system)
    
    @property
    def is_windows(self) -> bool:
        return self.platform_name.lower() == "windows"
        
    @property
    def is_linux(self) -> bool:
        return self.platform_name.lower() == "linux"
        
    @property
    def is_macos(self) -> bool:
        return self.platform_name.lower() == "darwin"
        
    @property
    def is_android(self) -> bool:
        # Termux sets PREFIX to /data/data/com.termux/files/usr
        # User might also set ANDROID_ROOT or similar.
        return "ANDROID_ROOT" in os.environ or "com.termux" in os.environ.get("PREFIX", "")

    @property
    def active_device(self) -> str:
        if self.is_android:
            return "mobile"
        return "desktop"

    @property
    def available_capabilities(self) -> list[str]:
        caps = ["memory", "planning", "research", "workflow", "browser"]
        if self.active_device == "desktop":
            caps.extend(["desktop_automation", "system_control", "coding"])
        if self.active_device == "mobile":
            caps.extend(["mobile_automation", "voice", "vision"])
        return caps
