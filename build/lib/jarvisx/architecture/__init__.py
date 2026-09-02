"""Jarvis X Architectural Constitution and Governance.

Establishes structural boundaries, canonical layer mappings, dependency contracts,
and verification rules without moving physical folders or breaking imports.
"""

from jarvisx.architecture.contracts import AgentContract, ArchitectureContract
from jarvisx.architecture.dependency_rules import ArchitectureValidator, ValidationResult, Violation
from jarvisx.architecture.layers import LAYER_REGISTRY, get_layer_for_module

__all__ = [
    "LAYER_REGISTRY",
    "get_layer_for_module",
    "ArchitectureContract",
    "AgentContract",
    "ArchitectureValidator",
    "ValidationResult",
    "Violation",
]
