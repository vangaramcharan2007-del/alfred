import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryAnalyzer

def test_repository_analyzer_fastapi():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_py = tmp_path / "main.py"
        main_py.write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
        
        test_py = tmp_path / "test_main.py"
        test_py.write_text("def test_dummy(): assert True\n", encoding="utf-8")

        analyzer = RepositoryAnalyzer()
        ctx = analyzer.analyze(tmpdir)

        assert ctx.primary_language == "python"
        assert ctx.framework == "FastAPI"
        assert ctx.files_count == 2
        assert ctx.has_tests is True
        assert "main.py" in ctx.key_files

def test_repository_analyzer_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = RepositoryAnalyzer()
        ctx = analyzer.analyze(tmpdir)
        assert ctx.files_count == 0
        assert ctx.framework in ["none", "unknown"]
