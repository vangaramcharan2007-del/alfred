import asyncio
import logging
from .mesh_transport import MeshTransport
from .node_discovery import NodeDiscoveryService
from .mesh_handshake import MeshHandshake
from .event_replication import EventReplicationRuntime
from .session_handoff_runtime import SessionHandoffRuntime
from .ownership_manager import OwnershipManager
from .sync_runtime import SyncRuntime
from .session_runtime import SessionRuntime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("IntegrationTest")

async def run_scenario():
    logger.info("=== Starting Validation Scenario ===")
    
    # 1. Initialize Laptop Node (Node 001)
    laptop_sync = SyncRuntime(db_path="var/laptop_sync.db")
    laptop_sync.initialize_wal()
    laptop_session = SessionRuntime(db_path="var/laptop_session.db")
    laptop_transport = MeshTransport("laptop-001")
    laptop_discovery = NodeDiscoveryService("laptop-001")
    laptop_ownership = OwnershipManager("laptop-001")
    laptop_handoff = SessionHandoffRuntime(laptop_session, laptop_transport)
    
    await laptop_transport.start_server(port=8001)
    
    # 2. Initialize Phone Node (Node 002)
    phone_sync = SyncRuntime(db_path="var/phone_sync.db")
    phone_sync.initialize_wal()
    phone_session = SessionRuntime(db_path="var/phone_session.db")
    phone_transport = MeshTransport("phone-002")
    phone_discovery = NodeDiscoveryService("phone-002")
    phone_ownership = OwnershipManager("phone-002")
    phone_handoff = SessionHandoffRuntime(phone_session, phone_transport)
    
    # 3. Discovery and Handshake
    laptop_discovery.register_peer(phone_discovery.advertise_presence())
    handshake = MeshHandshake()
    handshake.perform_handshake(phone_discovery.advertise_presence())
    
    await laptop_transport.connect_to_peer("ws://phone-ip:8002")
    
    # 4. Start Conversation on Laptop
    session_id = "conv-xyz-789"
    laptop_ownership.claim_ownership(session_id)
    
    # 5. Trigger Handoff
    logger.info("Triggering 'Continue on Phone'...")
    await laptop_handoff.initiate_handoff(session_id, "phone-002", {"history": ["hello", "how are you"]})
    
    # Phone receives handoff
    laptop_ownership.relinquish_ownership(session_id)
    phone_handoff.receive_handoff({
        "session_id": session_id, 
        "target_node": "phone-002",
        "context": {"history": ["hello", "how are you"]}
    })
    phone_ownership.claim_ownership(session_id)
    
    # 6. Shut down laptop, continue on phone
    await laptop_transport.shutdown()
    logger.info("Laptop runtime shut down.")
    logger.info(f"Phone session state: {phone_ownership.get_state(session_id)}")
    
    logger.info("=== Validation Scenario Complete ===")

if __name__ == "__main__":
    asyncio.run(run_scenario())
