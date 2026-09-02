"""
Terminal Sentinel — Auto-Debugger & Self-Healing Engine.
Watches terminal output or log files. If it detects a crash (Traceback),
it uses LLM to analyze the stack trace and propose/apply a fix.
"""
import os
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TerminalSentinel:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.active = True

    def analyze_crash(self, filepath: str, stack_trace: str) -> Dict[str, Any]:
        """Analyze a stack trace and generate a fixed version of the file."""
        import ollama
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            prompt = f"""Fix this code. It crashed with this error:
{stack_trace}

Source Code:
{source_code}

Output ONLY the fully fixed python code. No explanations. No markdown formatting."""

            res = ollama.chat(model="qwen2.5-coder:1.5b", messages=[{"role": "user", "content": prompt}])
            fixed_code = res["message"]["content"].strip()
            if "```python" in fixed_code:
                fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
                
            return {"status": "success", "fixed_code": fixed_code, "file": filepath}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def apply_fix(self, fix_data: Dict[str, Any]) -> bool:
        """Apply the fixed code back to the file."""
        try:
            with open(fix_data["file"], 'w', encoding='utf-8') as f:
                f.write(fix_data["fixed_code"])
            return True
        except Exception:
            return False
