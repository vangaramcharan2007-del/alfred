import json
import os
import re
from pathlib import Path

class PreferenceStore:
    """
    Manages long-term capability memory and user preferences.
    """
    def __init__(self, filepath: str = "var/preferences.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"references": {}}
        return {"references": {}}

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def get_reference(self, key: str) -> str:
        """Resolves an abstract reference like 'my editor' to a concrete target."""
        refs = self.data.get("references", {})
        return refs.get(key, {}).get("target")

    def get_confidence(self, key: str) -> int:
        """Returns the confidence score for a reference."""
        refs = self.data.get("references", {})
        return refs.get(key, {}).get("confidence", 0)

    def set_reference(self, key: str, target: str, confidence: int = 1):
        """Sets or updates a reference."""
        if "references" not in self.data:
            self.data["references"] = {}
            
        self.data["references"][key] = {
            "target": target,
            "confidence": confidence
        }
        self._save()

    def increment_confidence(self, key: str):
        """Increments confidence for a successful memory recall."""
        refs = self.data.get("references", {})
        if key in refs:
            refs[key]["confidence"] += 1
            self._save()

    def resolve(self, text: str) -> tuple[str, bool]:
        """
        Attempts to replace known references in a string.
        Returns the resolved string and a boolean indicating if a low-confidence
        reference was used (which might require explicit confirmation).
        """
        resolved_text = text
        requires_confirmation = False
        
        refs = self.data.get("references", {})
        for key, info in refs.items():
            if key in text.lower():
                # Simple replacement for demo
                resolved_text = re.sub(rf"\b{key}\b", info["target"], resolved_text, flags=re.IGNORECASE)
                if info.get("confidence", 0) < 3:
                    requires_confirmation = True
                    
        return resolved_text, requires_confirmation
