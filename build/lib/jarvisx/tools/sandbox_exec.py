import subprocess
import tempfile
import os

class RuntimeSandbox:
    def __init__(self, timeout_seconds: int = 5):
        self.timeout_seconds = timeout_seconds

    def execute_code(self, python_code: str) -> dict:
        temp_fd, temp_path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(python_code)
                
            env = os.environ.copy()
            
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env=env
            )
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "exit_code": -1,
                "output": e.stdout.decode('utf-8') if e.stdout else "",
                "error": f"Execution timed out after {self.timeout_seconds} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "output": "",
                "error": str(e)
            }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
