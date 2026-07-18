"""Capability Registry — manages metadata about available tools and their alternatives."""
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)

@dataclass
class Capability:
    name: str
    description: str
    requirements: List[str] = field(default_factory=list)
    supported_platforms: List[str] = field(default_factory=lambda: ["Windows", "Linux", "Darwin"])
    alternatives: List[str] = field(default_factory=list)
    verifier: Optional[str] = None
    retries: int = 3


class CapabilityRegistry:
    """Stores metadata about tools without eagerly probing the system."""
    
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Populate the registry with default tool capabilities."""
        # Browser capabilities
        self.register(Capability(
            name="chrome",
            description="Google Chrome web browser",
            alternatives=["edge", "firefox"]
        ))
        self.register(Capability(
            name="edge",
            description="Microsoft Edge web browser",
            alternatives=["chrome", "firefox"]
        ))
        self.register(Capability(
            name="firefox",
            description="Mozilla Firefox web browser",
            alternatives=["chrome", "edge"]
        ))
        # Abstract capability pointing to a concrete one
        self.register(Capability(
            name="browser",
            description="Default web browser",
            alternatives=["chrome", "edge", "firefox"]
        ))

        # Editor capabilities
        self.register(Capability(
            name="vscode",
            description="Visual Studio Code",
            alternatives=["notepad"]
        ))
        self.register(Capability(
            name="notepad",
            description="Windows Notepad",
            supported_platforms=["Windows"],
            alternatives=["vscode"]
        ))
        
        # Development tools
        self.register(Capability(
            name="git",
            description="Git version control system",
            alternatives=[]
        ))
        self.register(Capability(
            name="python",
            description="Python interpreter",
            alternatives=[]
        ))
        
        # OS tools
        self.register(Capability(
            name="explorer",
            description="Windows File Explorer",
            supported_platforms=["Windows"],
            alternatives=[]
        ))

    def register(self, capability: Capability) -> None:
        """Register a new capability."""
        self._capabilities[capability.name] = capability

    def get(self, name: str) -> Optional[Capability]:
        """Retrieve a capability by name."""
        return self._capabilities.get(name)

    def get_alternatives(self, name: str) -> List[str]:
        """Get list of alternative capability names."""
        cap = self.get(name)
        return cap.alternatives if cap else []
