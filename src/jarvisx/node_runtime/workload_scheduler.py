import logging

logger = logging.getLogger("WorkloadScheduler")

class WorkloadScheduler:
    """
    Routes execution requests to the node with the highest available resources (CPU/RAM).
    """
    def __init__(self, local_node_id: str):
        self.local_node_id = local_node_id
        self.node_telemetry = {}

    def update_telemetry(self, node_id: str, telemetry: dict):
        self.node_telemetry[node_id] = telemetry

    def determine_best_node(self, task_requirements: dict) -> str:
        best_node = self.local_node_id
        highest_score = -1

        for node_id, metrics in self.node_telemetry.items():
            # A simplistic heuristic: lower cpu % and higher battery means better score
            cpu_avail = 100 - metrics.get("cpu_percent", 50)
            battery = metrics.get("battery_percent", 100)
            
            score = cpu_avail + (battery * 2)
            if score > highest_score:
                highest_score = score
                best_node = node_id

        logger.info(f"Scheduler selected {best_node} as optimal placement for workload.")
        return best_node
