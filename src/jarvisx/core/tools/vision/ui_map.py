from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UIBoundingBox:
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

@dataclass
class UIElement:
    id: str
    type: str  # e.g., 'button', 'text', 'icon', 'window'
    bbox: UIBoundingBox
    text: Optional[str] = None
    confidence: float = 1.0

@dataclass
class UIMap:
    elements: List[UIElement]
    timestamp: float
    screenshot_path: str
    
    def find_by_text(self, text: str) -> List[UIElement]:
        return [e for e in self.elements if e.text and text.lower() in e.text.lower()]
