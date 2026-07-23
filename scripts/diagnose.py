import os
import sys
import shutil
import importlib.util
from pathlib import Path

def print_result(name, status, msg=""):
    color = "\033[92m" if status == "PASS" else "\033[93m" if status == "WARNING" else "\033[91m"
    reset = "\033[0m"
    # Basic ANSI colors for terminal
    print(f"{name.ljust(30)} [{color}{status}{reset}] {msg}")

def check_import(module_name):
    return importlib.util.find_spec(module_name) is not None

def main():
    print("========================================")
    print("      JARVIS X - SELF DIAGNOSTICS      ")
    print("========================================\n")

    overall_health = True

    # 1. Python Version
    if sys.version_info >= (3, 10):
        print_result("Python Version", "PASS", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        print_result("Python Version", "FAIL", "Requires 3.10+")
        overall_health = False

    # 2. Workspace Folders
    folders = ["workspace", "logs", "missions", "workflows", "databases", "memory", "configs"]
    missing = [f for f in folders if not Path(f).exists()]
    if missing:
        print_result("Workspace Folders", "WARNING", f"Missing: {', '.join(missing)}")
    else:
        print_result("Workspace Folders", "PASS", "All essential folders exist.")

    # 3. Environment Variables
    if Path(".env").exists():
        content = Path(".env").read_text()
        if "OPENAI_API_KEY=" in content or "ANTHROPIC_API_KEY=" in content:
            print_result("Environment Variables", "PASS", ".env file found.")
        else:
            print_result("Environment Variables", "WARNING", ".env exists but may lack API keys.")
    else:
        print_result("Environment Variables", "WARNING", "Missing .env file.")

    # 4. Ollama
    if shutil.which("ollama"):
        print_result("Ollama Engine", "PASS", "Installed and accessible in PATH.")
    else:
        print_result("Ollama Engine", "WARNING", "Not installed. Offline routing disabled.")

    # 5. OmniRoute (LiteLLM)
    if check_import("litellm"):
        print_result("OmniRoute (LiteLLM)", "PASS", "Installed.")
    else:
        print_result("OmniRoute (LiteLLM)", "FAIL", "Missing litellm package. Run bootstrap.py.")
        overall_health = False

    # 6. Playwright
    if check_import("playwright"):
        print_result("Playwright (Browser)", "PASS", "Installed.")
    else:
        print_result("Playwright (Browser)", "WARNING", "Missing playwright package. Web actions disabled.")

    # 7. PyAudio / Microphone
    if check_import("pyaudio"):
        print_result("PyAudio (Microphone)", "PASS", "Installed.")
    else:
        print_result("PyAudio (Microphone)", "WARNING", "Missing pyaudio. Voice listening disabled.")

    # 8. SQLite / DB drivers
    if check_import("sqlite3"):
        print_result("SQLite Database", "PASS", "Built-in sqlite3 available.")
    else:
        print_result("SQLite Database", "FAIL", "sqlite3 not found.")
        overall_health = False

    print("\n========================================")
    if overall_health:
        print("SYSTEM STATUS: \033[92mHEALTHY\033[0m")
    else:
        print("SYSTEM STATUS: \033[91mCRITICAL FAILURES DETECTED\033[0m")
        print("Please run 'python scripts/bootstrap.py' to resolve issues.")
    print("========================================\n")

if __name__ == "__main__":
    main()
