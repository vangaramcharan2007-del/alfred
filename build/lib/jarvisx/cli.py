"""
Jarvis X Command Line Interface (CLI).
Provides global commands to manage the OS daemon and interact headless.
"""
import sys
import argparse
import logging
from pathlib import Path

# Ensure imports work regardless of where CLI is called from
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format="%(message)s")

def boot_daemon():
    """Start the main jarvisd kernel."""
    try:
        from jarvisx.kernel.jarvisd import JarvisDaemon
        daemon = JarvisDaemon()
        daemon.boot()
    except Exception as e:
        print(f"FAILED TO BOOT JARVIS X: {e}")
        sys.exit(1)

def show_status():
    """Check if the daemon is running."""
    import psutil
    running = False
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            cmd = p.info.get('cmdline')
            if cmd and 'jarvisx.cli' in ' '.join(cmd) and 'boot' in ' '.join(cmd):
                running = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    if running:
        print("🟢 JARVIS X Kernel (jarvisd) is ONLINE and running in the background.")
        print("   HUD URL: http://localhost:8765")
    else:
        print("🔴 JARVIS X Kernel is OFFLINE.")
        print("   Run 'jarvis boot' to start.")

def headless_chat(prompt: str):
    """Direct chat via MultiModelRouter without voice."""
    print(f"Routing task: '{prompt}'...")
    from jarvisx.core.multi_model_router import MultiModelRouter
    router = MultiModelRouter.get_instance()
    res = router.route_and_call(prompt)
    
    print("\n" + "="*40)
    if res["status"] == "success":
        print(f"[{res['tier'].upper()} MODEL | {res['duration_sec']}s] ")
        print("-" * 40)
        print(res["response"])
    else:
        print(f"ERROR: {res.get('error')}")
    print("="*40 + "\n")

def open_hud():
    """Open the HUD in the default browser."""
    import webbrowser
    webbrowser.open("http://localhost:8765")
    print("Opening HUD in browser...")

def main():
    parser = argparse.ArgumentParser(description="JARVIS X Autonomous OS")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # boot
    subparsers.add_parser("boot", help="Start the Jarvis OS daemon")
    
    # status
    subparsers.add_parser("status", help="Check daemon status")
    
    # ui
    subparsers.add_parser("ui", help="Open the HUD dashboard")
    
    # chat
    chat_p = subparsers.add_parser("chat", help="Send a direct text command")
    chat_p.add_parser("prompt", help="The text prompt")
    chat_p.add_argument("prompt", nargs="+", help="The text command")
    
    args = parser.parse_args()
    
    if args.command == "boot":
        boot_daemon()
    elif args.command == "status":
        show_status()
    elif args.command == "ui":
        open_hud()
    elif args.command == "chat":
        headless_chat(" ".join(args.prompt))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
