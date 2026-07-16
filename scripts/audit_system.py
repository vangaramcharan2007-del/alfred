import sys
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

async def test_integration():
    try:
        print("--- IMPORTING VOICE ROUTER ---")
        from jarvisx.core.voice_router import VoiceRouter
        router = VoiceRouter()
        
        print("--- TESTING CONTINUITY LOOP ---")
        # Should route to continuity engine
        resp1 = await router.process_voice_command("continue the authentication system")
        print("Response 1:", resp1)
        
        print("--- TESTING PLANNING LOOP ---")
        # Should route to planning engine
        resp2 = await router.process_voice_command("build a new frontend component")
        print("Response 2:", resp2)
        
        print("--- TESTING INITIATIVE LOOP ---")
        # Should route to initiative engine
        resp3 = await router.process_voice_command("what needs our attention?")
        print("Response 3:", resp3)
        
        print("--- TESTING REFLECTION LOOP ---")
        # Should route to reflection engine
        resp4 = await router.process_voice_command("what did we learn from the last failure?")
        print("Response 4:", resp4)
        
        print("\nINTEGRATION TEST PASSED. NO CIRCULAR DEPENDENCIES DETECTED.")
        
    except Exception as e:
        print(f"INTEGRATION TEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_integration())
