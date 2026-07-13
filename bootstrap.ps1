Write-Host "Initializing Jarvis X Genesis (Windows)..."

Write-Host "Setting up virtual environment..."
python -m venv .venv
.venv\Scripts\Activate.ps1

Write-Host "Installing requirements..."
pip install -e .

Write-Host "Creating workspaces..."
New-Item -ItemType Directory -Force -Path "var" | Out-Null
New-Item -ItemType Directory -Force -Path "jarvis_workspace" | Out-Null
New-Item -ItemType Directory -Force -Path "cad_workspace" | Out-Null
New-Item -ItemType Directory -Force -Path "obsidian_vault" | Out-Null

Write-Host "Jarvis X setup complete."
Write-Host "Run '.venv\Scripts\Activate.ps1' then 'python src\jarvisx\cli.py' to start."
