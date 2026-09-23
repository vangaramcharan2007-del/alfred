"""
Jarvis X - Acoustic Soundpack Generator
Synthesizes crisp, studio-grade sci-fi audio cues using harmonic additive synthesis.
"""
import wave
import struct
import math
import os

SAMPLE_RATE = 44100
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "..", "var", "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)

def create_wav(filename, samples):
    filepath = os.path.join(SOUNDS_DIR, filename)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(2)      # Stereo
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        
        raw_data = bytearray()
        for left, right in samples:
            # Clamp to 16-bit signed int
            l_int = max(-32767, min(32767, int(left * 32767)))
            r_int = max(-32767, min(32767, int(right * 32767)))
            raw_data.extend(struct.pack("<hh", l_int, r_int))
        
        wav_file.writeframes(raw_data)
    print(f"[+] Generated: {filepath} ({len(samples)/SAMPLE_RATE:.2f}s)")
    return filepath

def synth_startup():
    # Jarvis holographic wake sound: Sub-bass swell + shimmering chord + crystal ping
    duration = 1.4
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    
    # Frequencies: F# Major 9th chord (F#2 = 92.5Hz, C#3 = 138.6Hz, F#3 = 185Hz, A#3 = 233.1Hz, C#4 = 277.2Hz, F4 = 349.2Hz, G#4 = 415.3Hz)
    chord = [92.5, 138.6, 185.0, 277.2, 415.3, 830.6]
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val_l = 0.0
        val_r = 0.0
        
        # Envelope: smooth exponential decay with quick 40ms attack
        attack = min(1.0, t / 0.05)
        decay = math.exp(-2.5 * t)
        env = attack * decay
        
        for idx, freq in enumerate(chord):
            # Frequency modulation for shimmer
            fm = math.sin(2 * math.pi * 3.5 * t) * 1.5
            phase = 2 * math.pi * (freq + fm) * t
            
            # Pan alternating frequencies left and right
            pan = 0.3 * ((-1) ** idx)
            sig = math.sin(phase) * (1.0 / (idx + 1.2))
            
            val_l += sig * (0.5 - pan)
            val_r += sig * (0.5 + pan)
        
        # Add high crystal ping at t=0.08
        if t > 0.08:
            ping_t = t - 0.08
            ping_env = math.exp(-12.0 * ping_t)
            ping = math.sin(2 * math.pi * 1760.0 * ping_t) * ping_env * 0.35
            val_l += ping * 0.4
            val_r += ping * 0.6
            
        samples.append((val_l * env * 0.7, val_r * env * 0.7))
    
    return create_wav("jarvis_startup.wav", samples)

def synth_success():
    # Upward energetic cyber-arpeggio (C5 -> E5 -> G5 -> C6)
    duration = 0.65
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    note_dur = 0.11
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val_l = 0.0
        val_r = 0.0
        
        for idx, freq in enumerate(notes):
            note_start = idx * note_dur
            if t >= note_start:
                dt = t - note_start
                env = math.exp(-8.0 * dt) * min(1.0, dt / 0.01)
                
                # Glass overtone
                sig1 = math.sin(2 * math.pi * freq * dt)
                sig2 = math.sin(2 * math.pi * freq * 2.0 * dt) * 0.25
                
                pan = -0.4 + (idx * 0.26)  # Sweep from left to right
                val_l += (sig1 + sig2) * env * (0.5 - pan * 0.5)
                val_r += (sig1 + sig2) * env * (0.5 + pan * 0.5)
                
        samples.append((val_l * 0.55, val_r * 0.55))
        
    return create_wav("jarvis_success.wav", samples)

def synth_notify():
    # Subtle, elegant luxury glass ping
    duration = 0.5
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    
    freq1 = 1200.0
    freq2 = 1800.0
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env1 = math.exp(-9.0 * t) * min(1.0, t / 0.005)
        env2 = math.exp(-14.0 * t) * min(1.0, t / 0.005)
        
        sig1 = math.sin(2 * math.pi * freq1 * t) * env1 * 0.5
        sig2 = math.sin(2 * math.pi * freq2 * t) * env2 * 0.3
        
        samples.append((sig1 + sig2 * 0.7, sig1 * 0.7 + sig2))
        
    return create_wav("jarvis_notify.wav", samples)

if __name__ == "__main__":
    print("Synthesizing Jarvis X Acoustic Soundpack...")
    s1 = synth_startup()
    s2 = synth_success()
    s3 = synth_notify()
    print("All soundpack assets generated in var/sounds/!")
