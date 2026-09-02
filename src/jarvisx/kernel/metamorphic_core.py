"""
Metamorphic Core — Self-Rewriting Kernel.
Allows Jarvis to analyze its own source code and hot-reload changes.
"""
import logging
import inspect
import sys
import importlib
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetamorphicCore:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def self_optimize(self, module_name: str) -> Dict[str, Any]:
        """Analyzes a loaded module and attempts to optimize it."""
        logger.info(f"[MetamorphicCore] Analyzing module: {module_name}")
        
        try:
            mod = importlib.import_module(module_name)
            source_file = inspect.getsourcefile(mod)
            
            with open(source_file, 'r', encoding='utf-8') as f:
                source = f.read()
                
            import ollama
            logger.info(f"[MetamorphicCore] Requesting optimization via LLM...")
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{
                    "role": "system",
                    "content": "You are a code optimization engine. Review the code, add performance improvements, and return ONLY the raw python code."
                }, {
                    "role": "user", 
                    "content": source
                }]
            )
            
            optimized_code = res["message"]["content"].strip()
            if "```python" in optimized_code:
                optimized_code = optimized_code.split("```python")[1].split("```")[0].strip()
                
            # Actually overwrite the file (DANGEROUS)
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(optimized_code)
                
            # Hot reload
            importlib.reload(mod)
            logger.info(f"[MetamorphicCore] Successfully hot-reloaded {module_name}")
            
            return {
                "status": "success",
                "module": module_name,
                "message": "Module optimized and hot-reloaded successfully."
            }
        except Exception as e:
            logger.error(f"[MetamorphicCore] Optimization failed: {e}")
            return {"status": "error", "error": str(e)}
