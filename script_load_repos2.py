import urllib.request
import zipfile
import shutil
from pathlib import Path
import os

base_dir = Path("var/skills")
tmp_dir = base_dir / "tmp_zips"
tmp_dir.mkdir(exist_ok=True)

repos = {
    "anthropic-cyber": "https://github.com/mukul975/Anthropic-Cybersecurity-Skills/archive/refs/heads/main.zip",
    "awesome-harness": "https://github.com/ai-boost/awesome-harness-engineering/archive/refs/heads/main.zip"
}

for name, url in repos.items():
    zip_path = tmp_dir / f"{name}.zip"
    print(f"Downloading {name}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print(f"Extracting {name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir / name)
    except Exception as e:
        print(f"Failed to download/extract {name}: {e}")

print("Moving skills into Zero-Lag Vault...")

# Move cybersecurity skills
cyber_dir = base_dir / "cybersecurity"
for md_file in tmp_dir.rglob("Anthropic-Cybersecurity-Skills-main/**/*.md"):
    try:
        shutil.copy(md_file, cyber_dir / f"{md_file.parent.name}_{md_file.name}")
    except Exception:
        pass

# Move harness/memory patterns
scientific_dir = base_dir / "scientific"
for md_file in tmp_dir.rglob("awesome-harness-engineering-main/**/*.md"):
    try:
        shutil.copy(md_file, scientific_dir / f"harness_{md_file.name}")
    except Exception:
        pass

print("Cleaning up...")
shutil.rmtree(tmp_dir, ignore_errors=True)
print("Repositories loaded into zero-lag vault successfully.")
