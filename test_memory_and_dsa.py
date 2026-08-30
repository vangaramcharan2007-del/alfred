"""
Test live memory, DSA code generation, and multi-turn conversational context.
"""
import asyncio
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvisx.organism import get_organism

async def main():
    org = get_organism()
    
    print("=" * 60)
    print("TEST 1: DSA Code Generation")
    print("=" * 60)
    res1 = await org.react_turn("could u type a code for linked list")
    print("Response:", res1.get("response")[:300] + "...")
    print("Spoken:", res1.get("spoken")[:100])
    print()

    print("=" * 60)
    print("TEST 2: Follow-up Multi-Turn Context")
    print("=" * 60)
    res2 = await org.react_turn("explain how insertion works in that code you just showed")
    print("Response:", res2.get("response")[:300] + "...")
    print()

    print("=" * 60)
    print("TEST 3: Memory Recall & Second Brain")
    print("=" * 60)
    res3 = await org.react_turn("what were we doing in our last activity on jarvis")
    print("Response:", res3.get("response")[:300] + "...")
    print()

if __name__ == "__main__":
    asyncio.run(main())
