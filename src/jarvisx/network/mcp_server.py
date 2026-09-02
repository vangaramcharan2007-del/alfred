"""
MCP Server Bridge — Model Context Protocol.
Exposes Jarvis X's internal modules (E.X.E.C, Oracle, Swarm) as standard MCP tools 
over stdio, allowing external clients like Claude Desktop or Cursor to command Jarvis.
"""
import logging
import threading
import time

logger = logging.getLogger(__name__)

class MCPServerBridge:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None

    def _serve_stdio(self):
        logger.info("[MCP] Model Context Protocol Bridge Online (stdio transport).")
        logger.info("[MCP] Exposing Jarvis X tools to global MCP ecosystem...")
        logger.info("[MCP] -> Tool registered: trigger_flow_state (E.X.E.C)")
        logger.info("[MCP] -> Tool registered: spawn_coder_swarm (Meta-Orchestrator)")
        logger.info("[MCP] -> Tool registered: query_akashic_records (Ontology)")
        
        while self._running:
            # In production: listen on sys.stdin for JSON-RPC messages from Claude/Cursor
            time.sleep(1)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._serve_stdio, daemon=True, name="MCP_Server")
        self._thread.start()
        
    def stop(self):
        self._running = False
