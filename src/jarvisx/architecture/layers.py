"""Canonical Layer Registry for Jarvis X.

Maps existing physical directories and modules in src/jarvisx to their canonical
architectural layer without requiring disruptive folder relocations.
"""

from typing import Optional

# Canonical mapping of layers to their corresponding top-level modules and packages
LAYER_REGISTRY = {
    "human": [
        "config",
    ],
    "alfred": [
        "main.py",
        "core",
        "kernel",
        "runtime",
        "decision",
        "evolution",
        "architecture",
    ],
    "agents": [
        "agents",
        "brain",
        "cognition",
        "memory",
        "missions",
        "engineering",
        "llm",
        "learning",
        "automation",
        "skills",
        "verification",
    ],
    "capabilities": [
        "capabilities",
        "tools",
        "benchmark",
    ],
    "infrastructure": [
        "adapters",
        "deployment",
        "observability",
        "models",
    ],
    "interface": [
        "interface",
        "ui",
    ],
}

# Hierarchical dependency ordering (from top to bottom)
LAYER_ORDER = [
    "human",
    "alfred",
    "agents",
    "capabilities",
    "infrastructure",
    "interface",
]


def get_layer_for_module(module_name: str) -> Optional[str]:
    """Returns the architectural layer name for a given top-level jarvisx package or file."""
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[0] == "jarvisx":
        top_mod = parts[1]
    elif len(parts) == 1 and not parts[0].endswith(".py"):
        top_mod = parts[0]
    else:
        top_mod = module_name

    if top_mod == "main":
        top_mod = "main.py"

    for layer, modules in LAYER_REGISTRY.items():
        if top_mod in modules or f"{top_mod}.py" in modules:
            return layer
    return None
