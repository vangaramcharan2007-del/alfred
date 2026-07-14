import asyncio
import logging
from contextlib import asynccontextmanager
try:
    from fastapi import FastAPI
except ImportError:
    # Fallback mock for environments without fastapi
    class FastAPI:
        def __init__(self, *args, **kwargs): pass
        def get(self, *args, **kwargs): return lambda f: f

from .presence_runtime import PresenceRuntime
from .sync_runtime import SyncRuntime
from .session_runtime import SessionRuntime
from .resource_runtime import ResourceRuntime
from .recovery_runtime import RecoveryRuntime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NodeBootstrap")

class NodeRuntime:
    def __init__(self):
        self.presence = PresenceRuntime()
        self.sync = SyncRuntime()
        self.session = SessionRuntime()
        self.resource = ResourceRuntime()
        self.recovery = RecoveryRuntime()
        self.node_id = "node-001-primary"

    async def start(self):
        logger.info(f"Starting Node {self.node_id}...")
        self.sync.initialize_wal()
        await self.presence.start_heartbeat()
        self.recovery.start_watchdogs()
        self.session.restore_state()
        logger.info(f"Node {self.node_id} runtime initialized successfully.")

    async def stop(self):
        logger.info(f"Stopping Node {self.node_id}...")
        self.recovery.stop_watchdogs()
        await self.presence.stop_heartbeat()
        self.sync.flush_wal()
        logger.info(f"Node {self.node_id} shut down gracefully.")


node = NodeRuntime()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await node.start()
    yield
    await node.stop()

app = FastAPI(title="Antigravity Node 001", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "node_id": node.node_id,
        "resources": node.resource.get_telemetry()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("jarvisx.node_runtime.runtime_bootstrap:app", host="127.0.0.1", port=8000, reload=False)
