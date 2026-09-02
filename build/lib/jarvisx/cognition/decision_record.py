from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import datetime

@dataclass
class DecisionRecord:
    task: str
    selected_agent: str
    alternatives: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
