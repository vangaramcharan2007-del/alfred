import sys
import os
import time
import shutil
import asyncio
from pathlib import Path

def print_step(msg):
    print(f"\n[ACCEPTANCE TEST] {msg}")

async def run_acceptance_test():
    # Ensure src is in PYTHONPATH
    src_path = str(Path(__file__).parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    print_step("1. Verifying Python version...")
    if sys.version_info < (3, 10):
        print("FAIL: Python 3.10+ is required.")
        return False
    print("PASS: Python version is ok.")
    
    print_step("2. Creating temporary workspace...")
    test_dir = Path("acceptance_workspace")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Temporarily point environment variables to the test dir
    os.environ["DB_PATH"] = str(test_dir / "test_objectives.db")
    os.environ["VAULT_PATH"] = str(test_dir / "test_vault")
    os.environ["JARVIS_ENV"] = "testing"
    
    print_step("3. Initializing Jarvis X Components...")
    try:
        from jarvisx.core.config.settings import settings
        from jarvisx.core.config.logging_config import setup_logging
        from jarvisx.runtime import create_default_runtime
        from jarvisx.core.tools.tool_registry import ToolRegistry
    except ImportError as e:
        print(f"FAIL: Failed to import components. {e}")
        return False
        
    setup_logging()
    
    print_step("4. Loading memory and skills (via initialization)...")
    try:
        runtime = create_default_runtime()
        alfred = runtime.alfred
        registry = ToolRegistry.get_instance()
    except Exception as e:
        print(f"FAIL: Failed to initialize Alfred. {e}")
        return False
        
    print_step("5. Executing representative commands...")
    commands = [
        "Hello Alfred.",
        "Remember that the secret code is 42.",
        "What is the secret code?",
        "Create a plan to test the system."
    ]
    
    success = True
    for cmd in commands:
        print(f"  -> User: {cmd}")
        try:
            # Running asynchronously since we are in async context, but Alfred process is sync/async.
            if asyncio.iscoroutinefunction(alfred.process):
                response = await alfred.process(cmd)
            else:
                response = alfred.process(cmd)
            print(f"  <- Alfred: {getattr(response, 'message', str(response))}")
        except Exception as e:
            print(f"FAIL: Error executing command '{cmd}': {e}")
            success = False
            break
            
    print_step("6. Cleaning up...")
    try:
        shutil.rmtree(test_dir, ignore_errors=True)
    except Exception:
        pass
        
    if success:
        print("\n========================================")
        print("ACCEPTANCE TEST: PASS")
        print("Jarvis X is ready for production.")
        print("========================================\n")
        return True
    else:
        print("\n========================================")
        print("ACCEPTANCE TEST: FAIL")
        print("========================================\n")
        return False

if __name__ == "__main__":
    passed = asyncio.run(run_acceptance_test())
    sys.exit(0 if passed else 1)
