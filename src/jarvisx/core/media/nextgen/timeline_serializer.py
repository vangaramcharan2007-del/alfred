import json
import dataclasses
from typing import Any
from .timeline import Timeline

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

class TimelineSerializer:
    @staticmethod
    def to_json(timeline: Timeline, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(timeline, f, cls=EnhancedJSONEncoder, indent=4)
            
    @staticmethod
    def to_dict(timeline: Timeline) -> dict:
        return dataclasses.asdict(timeline)
