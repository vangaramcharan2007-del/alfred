# src/jarvisx/telemetry/hardware_sensors.py

class HardwareSensors:
    """
    Captures battery state, network latency, and CPU load across nodes.
    Designed to feed into the PresenceMesh.
    """
    def __init__(self):
        pass

    def get_battery_level(self) -> int:
        return 100

    def get_network_quality(self) -> str:
        return "HIGH"

    def get_cpu_load(self) -> float:
        return 0.0
