import sys
import time
import subprocess
from pathlib import Path

def run_checks():
    print("[Jarvis] Running bootstrap checks...")
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10+ required.")
        sys.exit(1)
    
    # Check if virtual env is active
    if "VIRTUAL_ENV" not in os.environ and not sys.prefix.endswith('.venv'):
        print("WARNING: Virtual environment not detected. Running without it.")

    # Call diagnostics silently
    try:
        res = subprocess.run([sys.executable, "scripts/diagnose.py"], capture_output=True, text=True)
        if "CRITICAL FAILURES DETECTED" in res.stdout:
            print("ERROR: Diagnostics failed. Please run 'python scripts/diagnose.py' for details.")
            sys.exit(1)
    except Exception as e:
        print(f"Diagnostics error: {e}")

if __name__ == "__main__":
    import os
    run_checks()
    
    try:
        from jarvisx.core.config.settings import settings
        from jarvisx.core.config.logging_config import setup_logging
        from jarvisx.runtime import create_default_runtime
    except ImportError as e:
        print(f"ERROR: Initialization failed: {e}")
        print("Did you run 'python scripts/bootstrap.py'?")
        sys.exit(1)

    # Initialize components
    loggers = setup_logging()
    logger = loggers["runtime"]
    logger.info("Jarvis X starting up...")
    
    # Create required DBs/folders lazily
    settings.DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    settings.VAULT_PATH.mkdir(exist_ok=True, parents=True)
    
    print("\n" + "="*50)
    print("                JARVIS X                  ")
    print("="*50)
    print(f" Environment : {settings.ENV}")
    print(f" Mode        : {'Offline' if settings.IS_OFFLINE else 'Online'}")
    print("="*50 + "\n")
    
    try:
        runtime = create_default_runtime()
        alfred = runtime.alfred
        print("Jarvis X is ready. Type 'exit' to quit.\n")
        
        while True:
            cmd = input("Jarvis> ")
            if cmd.strip().lower() in ["exit", "quit"]:
                break
            
            # Simple fallback response if command is passed
            if cmd.strip():
                try:
                    response = alfred.process(cmd)
                    print(f"Alfred: {response}")
                except Exception as ex:
                    print(f"ERROR: {ex}")
                    logger.error(f"Execution failed: {ex}", exc_info=True)
                    
    except KeyboardInterrupt:
        print("\nShutting down Jarvis X...")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        logger.critical("Fatal error", exc_info=True)
    finally:
        logger.info("Jarvis X shutdown.")
        print("Goodbye.")
