import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel
from jarvisx.capabilities.coding.pipeline.code_executor import CodeExecutor, PermissionDeniedException

def test_code_executor_permissions():
    pm = PermissionManager()
    executor = CodeExecutor(permission_manager=pm)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Without WRITE permission, write should raise exception
        with pytest.raises(PermissionDeniedException):
            executor.write_file(tmpdir, "calculator.py", "x = 10", capability_name="coding_agent")

        # Grant WRITE permission
        pm.request_permission("coding_agent", PermissionLevel.WRITE)
        rec = executor.write_file(tmpdir, "calculator.py", "x = 10", capability_name="coding_agent")
        
        assert rec.action == "created"
        assert rec.file_path == "calculator.py"
        assert (Path(tmpdir) / "calculator.py").read_text() == "x = 10"

        # Modifying file
        rec_mod = executor.write_file(tmpdir, "calculator.py", "x = 20", capability_name="coding_agent")
        assert rec_mod.action == "modified"
        assert rec_mod.content_before == "x = 10"
        assert rec_mod.content_after == "x = 20"
