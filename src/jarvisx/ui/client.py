import socket

UDP_PORT = 8766

def set_overlay_color(agent_id: str):
    """
    Sends a UDP packet to the PyQt5 overlay to change the waveform color based on the agent.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(f"COLOR {agent_id}".encode("utf-8"), ("127.0.0.1", UDP_PORT))
    except Exception as e:
        pass # Ignore if overlay is not running
