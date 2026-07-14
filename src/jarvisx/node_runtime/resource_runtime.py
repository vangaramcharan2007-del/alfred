import logging
try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger("ResourceRuntime")

class ResourceRuntime:
    def __init__(self):
        if not psutil:
            logger.warning("psutil not installed. Resource metrics will be mocked.")

    def get_telemetry(self) -> dict:
        if psutil:
            try:
                mem = psutil.virtual_memory()
                return {
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "memory_mb_used": mem.used / (1024 * 1024),
                    "memory_percent": mem.percent
                }
            except Exception as e:
                logger.error(f"Failed to fetch psutil metrics: {e}")
        
        return {
            "cpu_percent": 15.0,
            "memory_mb_used": 1024.5,
            "memory_percent": 30.0
        }
