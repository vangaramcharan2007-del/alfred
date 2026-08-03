from __future__ import annotations
import heapq
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass(order=True)
class ScheduledTask:
    priority: int  # lower number = higher priority
    task_id: str = field(compare=False)
    action: str = field(compare=False)
    params: Dict[str, Any] = field(compare=False)
    timestamp: float = field(compare=False, default_factory=time.time)
    retries: int = field(compare=False, default=0)

class ProviderScheduler:
    def __init__(self, max_parallel: int = 4):
        self.max_parallel = max_parallel
        self.queue: List[ScheduledTask] = []
        self.active_reservations: Dict[str, str] = {}  # provider_id -> task_id

    def submit_task(
        self,
        task_id: str,
        priority: int,
        action: str,
        params: Dict[str, Any]
    ) -> ScheduledTask:
        task = ScheduledTask(priority=priority, task_id=task_id, action=action, params=params)
        heapq.heappush(self.queue, task)
        return task

    def pop_next_task(self) -> Optional[ScheduledTask]:
        if self.queue:
            return heapq.heappop(self.queue)
        return None

    def reserve_provider(self, provider_id: str, task_id: str) -> bool:
        if provider_id in self.active_reservations:
            return False
        self.active_reservations[provider_id] = task_id
        return True

    def release_provider(self, provider_id: str) -> None:
        if provider_id in self.active_reservations:
            del self.active_reservations[provider_id]

    def is_provider_available(self, provider_id: str) -> bool:
        return provider_id not in self.active_reservations
