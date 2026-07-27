import sys
import tempfile
import os

print("Starting F5-TTS generation...")

try:
    from f5_tts.api import F5TTS
    
    reference_audio = "assets/voices/friday_reference.wav"
    output_audio = "assets/voices/friday_generated.wav"
    text = "Hello, I am Friday. My neural pathways are fully integrated, and I am online."
    
    print("Loading model...")
    model = F5TTS()
    
    print("Running inference...")
    model.infer(
        ref_file=reference_audio,
        ref_text="",
        gen_text=text,
        file_wave=output_audio
    )
    
    print(f"Successfully generated {output_audio}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
