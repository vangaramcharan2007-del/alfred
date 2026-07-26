import zmq
import json
import logging
from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)

class ZeroMQBus:
    """A lightweight asynchronous message bus using ZeroMQ for distributed worker nodes."""

    def __init__(self, bind_address: str = "tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.bind_address = bind_address
        self.socket = None
        
    def start_server(self):
        """Start the bus as a central broker or orchestrator."""
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.bind_address)
        logger.info(f"ZeroMQ Bus server started on {self.bind_address}")

    def start_client(self, connect_address: str = "tcp://127.0.0.1:5555"):
        """Connect as a worker node to the central bus."""
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(connect_address)
        logger.info(f"ZeroMQ Bus client connected to {connect_address}")

    def send_task(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a task to the bus and wait for the result."""
        if not self.socket:
            raise RuntimeError("Bus not started. Call start_client() first.")
            
        message = json.dumps({"type": task_type, "payload": payload})
        self.socket.send_string(message)
        
        reply = self.socket.recv_string()
        return json.loads(reply)

    def listen(self, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]):
        """Listen for incoming tasks (for the server or a worker)."""
        if not self.socket:
            raise RuntimeError("Bus not started. Call start_server() first.")
            
        logger.info("Listening for messages...")
        while True:
            try:
                message = self.socket.recv_string()
                data = json.loads(message)
                
                # Execute the handler
                result = handler(data.get("type", "unknown"), data.get("payload", {}))
                
                # Send back the result
                self.socket.send_string(json.dumps(result))
            except zmq.ZMQError as e:
                logger.error(f"ZeroMQ Error: {e}")
                break
            except Exception as e:
                logger.error(f"Handler error: {e}")
                self.socket.send_string(json.dumps({"error": str(e)}))

    def close(self):
        """Close the socket and context."""
        if self.socket:
            self.socket.close()
        self.context.term()
