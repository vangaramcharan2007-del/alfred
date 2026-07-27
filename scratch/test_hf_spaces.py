import os
from gradio_client import Client, handle_file
import httpx

# Patch httpx timeout globally
original_init = httpx.Client.__init__
def new_init(self, *args, **kwargs):
    kwargs['timeout'] = httpx.Timeout(300.0)
    original_init(self, *args, **kwargs)
httpx.Client.__init__ = new_init

spaces = [
    "mrfakename/E2-F5-TTS",
    "cocktailpeanut/E2-F5-TTS",
    "raajmaurya/SWivid-F5-TTS",
    "LeonEr/SWivid-F5-TTS",
    "SWivid/F5-TTS"
]

ref_audio = "assets/voices/friday_reference.wav"
text = "Hello, I am Friday. My neural pathways are fully integrated, and I am online."

success = False
for space in spaces:
    print(f"Trying space: {space}")
    try:
        client = Client(space)
        result = client.predict(
            ref_audio=handle_file(ref_audio),
            ref_text="",
            gen_text=text,
            remove_silence=False,
            api_name="/predict"
        )
        print(f"SUCCESS with {space}! Output saved to: {result}")
        success = True
        break
    except Exception as e:
        print(f"FAILED {space}: {e}")

if not success:
    print("ALL SPACES FAILED.")
