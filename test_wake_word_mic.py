import time
from jarvisx.voice.ambient_dual_sentinel import launch_ambient_sentinel, AmbientDualSentinel

def test_mic():
    print("Testing Wake-Word Mic... Please say 'Alfred' or 'E-V'")
    sentinel = AmbientDualSentinel.get_instance()
    sentinel.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test stopped.")

if __name__ == "__main__":
    test_mic()
