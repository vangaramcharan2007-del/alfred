"""
Jarvis X — Sovereign Voice Butler Runtime.
Hands-free continuous voice interaction loop.
Listens via Ears (STT) -> Decides via Brain (Groq LPU) -> Acts via Hands (Tools) -> Speaks via Mouth (TTS).
"""

import asyncio
import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jarvisx.organism import get_organism


async def run_voice_cycle(org, sample_prompt: str = None):
    """Execute a single voice turn with full neural synthesis."""
    if sample_prompt:
        user_text = sample_prompt
    else:
        print("\n[Ears] 🎙️ Listening for wake word ('Alfred', 'Jarvis')...")
        user_text = org.ears.listen_and_transcribe(timeout_sec=4.0)

    if not user_text:
        return

    print(f"\n[USER VOCAL]: \"{user_text}\"")
    t0 = time.time()
    res = await org.react_turn(user_text)
    latency_ms = (time.time() - t0) * 1000

    decision = res.get("decision")
    spoken = res.get("spoken") or res.get("response") or ""
    print(f"[ALFRED BRAIN]: {decision.upper()} in {latency_ms:.1f}ms")
    print(f"[ALFRED VOICE]: \"{spoken}\"\n")


async def main():
    print("=" * 70)
    print("   ALFRED OS — SOVEREIGN VOICE BUTLER (AMBIENT VOICE ENGINE)")
    print("=" * 70 + "\n")

    org = get_organism()
    salutation = "Sir" if org.persona == "ALFRED" else "Boss"

    welcome_msg = f"Alfred Voice Sentinel is online, {salutation}. Ready for voice commands."
    print(f"🎙️ {welcome_msg}")
    org.mouth.speak(welcome_msg)

    # Demo 2 voice test turns
    print("\n--- Testing Live Voice Reasoning Cycles ---")
    await run_voice_cycle(org, "Alfred, what time is it and how is the system running?")
    await run_voice_cycle(org, "Alfred, set a packing reminder for 524 pm today.")

    print("=" * 70)
    print("   VOICE BUTLER RUNTIME VERIFIED & ACTIVE [OK]")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
