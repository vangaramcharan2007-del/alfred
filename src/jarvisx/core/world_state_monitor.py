# src/jarvisx/core/world_state_monitor.py

import os
import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class WorldEvent:
    event_type: str
    severity: str
    source: str
    metadata: Dict[str, Any]

class BaseSensor:
    def __init__(self, name: str):
        self.name = name

    async def poll(self) -> Optional[WorldEvent]:
        raise NotImplementedError

class FilesystemSensor(BaseSensor):
    def __init__(self, watch_dir: str, threshold: int = 500):
        super().__init__("filesystem_sensor")
        self.watch_dir = watch_dir
        self.threshold = threshold

    async def poll(self) -> Optional[WorldEvent]:
        if not os.path.exists(self.watch_dir):
            return None
        
        file_count = 0
        for entry in os.scandir(self.watch_dir):
            if entry.is_file():
                file_count += 1
                
        if file_count >= self.threshold:
            return WorldEvent(
                event_type="DOWNLOADS_CLUTTER",
                severity="MEDIUM",
                source=self.name,
                metadata={
                    "file_count": file_count,
                    "path": self.watch_dir
                }
            )
        return None

class TaskFailureSensor(BaseSensor):
    def __init__(self):
        super().__init__("task_sensor")
        self.simulated_failures = {}

    def inject_failure(self, task_name: str, failures: int):
        self.simulated_failures[task_name] = failures

    async def poll(self) -> Optional[WorldEvent]:
        # Detect if any simulated task has repeatedly failed
        for task_name, failures in list(self.simulated_failures.items()):
            if failures >= 3:
                # Clear after detecting so we don't infinitely trigger
                del self.simulated_failures[task_name]
                return WorldEvent(
                    event_type="TASK_FAILURE",
                    severity="HIGH",
                    source=self.name,
                    metadata={
                        "task_name": task_name,
                        "failures": failures
                    }
                )
        return None

class ResourceSensor(BaseSensor):
    def __init__(self):
        super().__init__("resource_sensor")
        self.simulated_disk_usage = 50

    def set_disk_usage(self, usage: int):
        self.simulated_disk_usage = usage

    async def poll(self) -> Optional[WorldEvent]:
        if self.simulated_disk_usage > 90:
            usage = self.simulated_disk_usage
            self.simulated_disk_usage = 50  # Reset after trigger
            return WorldEvent(
                event_type="DISK_PRESSURE",
                severity="CRITICAL",
                source=self.name,
                metadata={
                    "disk_usage": usage
                }
            )
        return None

class WorldStateMonitor:
    def __init__(self, initiative_manager):
        self.sensors: List[BaseSensor] = []
        self.initiative_manager = initiative_manager
        self.running = False

    def add_sensor(self, sensor: BaseSensor):
        self.sensors.append(sensor)

    async def run(self):
        self.running = True
        while self.running:
            for sensor in self.sensors:
                event = await sensor.poll()
                if event:
                    self.initiative_manager.handle_world_event(event)
            await asyncio.sleep(1.0)
            
    def stop(self):
        self.running = False
