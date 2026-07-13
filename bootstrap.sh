#!/bin/bash
set -e

echo "Initializing Jarvis X Genesis (Unix/Termux)..."

echo "Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing requirements..."
pip install -e .

echo "Creating workspaces..."
mkdir -p var
mkdir -p jarvis_workspace
mkdir -p cad_workspace
mkdir -p obsidian_vault

echo "Jarvis X setup complete."
echo "Run 'source .venv/bin/activate' then 'python src/jarvisx/cli.py' to start."
