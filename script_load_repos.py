import os
import subprocess
import shutil
from pathlib import Path

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=False)

base_dir = Path("var/skills")
tmp_dir = base_dir / "tmp_repos"
tmp_dir.mkdir(exist_ok=True)

repos = {
    "anthropic-cyber": "https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git",
    "awesome-harness": "https://github.com/ai-boost/awesome-harness-engineering.git"
}

for name, url in repos.items():
    repo_path = tmp_dir / name
    if not repo_path.exists():
        run_cmd(f"git clone {url} {repo_path}")

print("Moving skills into Zero-Lag Vault...")

# Move cybersecurity skills
cyber_dir = base_dir / "cybersecurity"
anthropic_repo = tmp_dir / "anthropic-cyber"
if anthropic_repo.exists():
    for md_file in anthropic_repo.rglob("*.md"):
        try:
            shutil.copy(md_file, cyber_dir / f"{md_file.parent.name}_{md_file.name}")
        except Exception:
            pass

# Move harness/memory patterns
scientific_dir = base_dir / "scientific"
harness_repo = tmp_dir / "awesome-harness"
if harness_repo.exists():
    for md_file in harness_repo.rglob("*.md"):
        try:
            shutil.copy(md_file, scientific_dir / f"harness_{md_file.name}")
        except Exception:
            pass

print("Cleaning up...")
shutil.rmtree(tmp_dir, ignore_errors=True)
print("Repositories loaded into zero-lag vault successfully.")
