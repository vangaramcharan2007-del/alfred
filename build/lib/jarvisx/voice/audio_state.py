"""Global Audio State for Full-Duplex Interruption."""

IS_SPEAKING = False
INTERRUPT_REQUESTED = False

def stop_all_audio():
    global INTERRUPT_REQUESTED
    INTERRUPT_REQUESTED = True
