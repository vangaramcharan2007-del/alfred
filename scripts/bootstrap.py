import os
import sys
import subprocess
import shutil
import venv
from pathlib import Path

def print_step(msg):
    print(f"\n[Jarvis X Bootstrap] {msg}")

def check_command(cmd_name):
    return shutil.which(cmd_name) is not None

def run_command(cmd, cwd=None):
    try:
        subprocess.check_call(cmd, cwd=cwd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print_step("Starting Jarvis X Bootstrap...")

    # 1. Check Python Version
    print_step("Checking Python version...")
    if sys.version_info < (3, 10):
        print("FAIL: Python 3.10+ is required.")
        sys.exit(1)
    print("✓ Python version is acceptable.")

    # 2. Check Git
    print_step("Checking Git...")
    if not check_command("git"):
        print("FAIL: Git is not installed or not in PATH.")
        sys.exit(1)
    print("✓ Git is installed.")

    # 3. Check Ollama
    print_step("Checking Ollama (Local LLM Engine)...")
    if not check_command("ollama"):
        print("WARNING: Ollama is not installed. OmniRoute offline capabilities will not function.")
        print("         Please install Ollama from https://ollama.com/")
    else:
        print("✓ Ollama is installed.")
        print("  NOTE: Please ensure you have pulled necessary models manually (e.g., 'ollama pull llama3.2')")

    # 5. Virtual Environment
    print_step("Setting up Virtual Environment (.venv)...")
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        venv.create(venv_dir, with_pip=True)
        print("✓ Created virtual environment.")
    else:
        print("✓ Virtual environment already exists.")

    # Determine pip path
    if os.name == 'nt':
        pip_exe = str(venv_dir / "Scripts" / "pip.exe")
        python_exe = str(venv_dir / "Scripts" / "python.exe")
    else:
        pip_exe = str(venv_dir / "bin" / "pip")
        python_exe = str(venv_dir / "bin" / "python")

    # 6. Install Dependencies
    print_step("Installing dependencies...")
    if Path("requirements.txt").exists():
        if run_command(f"{pip_exe} install -r requirements.txt"):
            print("✓ Requirements installed.")
        else:
            print("FAIL: Failed to install requirements.")
            sys.exit(1)
    else:
        print("WARNING: requirements.txt not found. Skipping dependency installation.")

    # 7. Install Playwright drivers
    print_step("Installing Playwright browser drivers...")
    if run_command(f"{python_exe} -m playwright install"):
        print("✓ Playwright drivers installed.")
    else:
        print("WARNING: Failed to install playwright drivers. Web automation may not work.")

    # 8. Setup Workspace Folders
    print_step("Creating workspace directories...")
    folders = ["workspace", "logs", "missions", "workflows", "databases", "memory", "vault", "configs", "assets"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"  ✓ {folder}/")

    # 9. .env Setup
    print_step("Setting up environment variables...")
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✓ Copied .env.example to .env. Please update it with your keys.")
        else:
            Path(".env").touch()
            print("✓ Created empty .env file. Please populate it.")
    else:
        print("✓ .env file already exists.")

    print_step("System Ready! You can now start Jarvis X.")
    print("\nNext step: Run 'python jarvis.py'\n")

if __name__ == "__main__":
    main()
