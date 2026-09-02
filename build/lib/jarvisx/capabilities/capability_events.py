from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CapabilityEvent:
    capability_name: str

@dataclass
class CapabilityLoaded(CapabilityEvent):
    version: str

@dataclass
class CapabilityFailed(CapabilityEvent):
    error: str

@dataclass
class CapabilityUpdated(CapabilityEvent):
    new_version: str

@dataclass
class CapabilityDisabled(CapabilityEvent):
    reason: str
