import pytest
import shutil
import subprocess
from pathlib import Path

def test_real_git_binary_and_local_repo(tmp_path):
    git_path = shutil.which("git")
    assert git_path is not None

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    (tmp_path / "test.txt").write_text("hello git", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
    res = subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=t@test.com", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True, text=True, check=True)
    assert res.returncode == 0
