import sys
import asyncio
import json
from jarvisx.mcp.mcp_client import MCPClient
from jarvisx.computer_use.art_synthesizer import ArtSynthesizer

async def main():
    print("=========================================================================")
    print("     JARVIS X: UACC MCP REAL PROTOCOL VERIFICATION")
    print("=========================================================================")
    client = MCPClient(server_id="uacc_server", command=[sys.executable, "-m", "jarvisx.mcp.uacc_server"])
    conn = await client.connect(timeout_sec=4.0)
    print("  1. MCP Handshake & Protocol Negotiation :", "[CONNECTED]" if conn else "[FAILED]")
    
    tools = await client.list_tools()
    print(f"  2. MCP Tools Discovered ({len(tools)})          : {[t.name for t in tools]}")
    
    screen_res = await client.call_tool("uacc_inspect_screen", {})
    screen_text = screen_res.get("content", [{}])[0].get("text", "{}")
    screen_data = json.loads(screen_text)
    print(f"  3. Screen Inspection via MCP            : {screen_data.get('width')}x{screen_data.get('height')} | Window: '{screen_data.get('active_window')}'")
    
    strokes_zoro = ArtSynthesizer.generate_zoro_strokes(960, 540)
    strokes_iron = ArtSynthesizer.generate_ironman_strokes(960, 540)
    print(f"  4. Parametric Zoro Strokes Synthesized  : {len(strokes_zoro)} vector strokes")
    print(f"  5. Parametric Iron Man Strokes          : {len(strokes_iron)} vector strokes")
    
    await client.disconnect()
    print("  6. UACC MCP Server Teardown             : [CLEAN SHUTDOWN]")
    print("=========================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
