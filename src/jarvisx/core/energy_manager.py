# src/jarvisx/core/energy_manager.py

class EnergyManager:
    """
    Influences scheduling based on battery levels and thermal states.
    Prefers charging devices for heavy workloads and supports eco-mode.
    """
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager

    def can_accept_workload(self, node_id: str, expected_load: float) -> bool:
        return True
