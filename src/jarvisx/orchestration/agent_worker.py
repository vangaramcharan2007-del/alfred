"""
Agent Worker — The hands of the Coder Swarm.
Uses Gemini Cloud to generate code and actually writes it to the local disk.
"""
import logging
import os
import re
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AgentWorker:
    def __init__(self, role: str, persona_prompt: str):
        self.role = role
        self.persona = persona_prompt
        self._gemini = None

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def _get_llm(self):
        if not self._gemini:
            try:
                from jarvisx.llm.gemini_provider import GeminiLLMProvider
                self._gemini = GeminiLLMProvider()
            except Exception as e:
                logger.error(f"[{self.role}] Failed to load Gemini Provider: {e}")
        return self._gemini

    def execute_task(self, task: str, workspace_dir: str = ".") -> Dict[str, Any]:
        """Runs the task through the LLM and parses file output."""
        logger.info(f"[{self.role}] Executing task: {task}")
        self._push_to_ui("swarm_event", {"agent": self.role, "action": f"Analyzing task: {task}"})
        
        gemini = self._get_llm()
        if not gemini:
            return {"status": "error", "error": "LLM Provider offline"}

        system_prompt = (
            f"{self.persona}\n"
            "You are an autonomous agent capable of writing files to the user's disk.\n"
            "If you need to create or edit a file, you MUST use the following exact format:\n\n"
            "[FILE: path/to/filename.ext]\n"
            "```python\n"
            "# file contents here\n"
            "```\n\n"
            "You can output multiple files this way. Only output the code, no fluff."
        )

        full_prompt = f"System: {system_prompt}\n\nTask: {task}"

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._push_to_ui("swarm_event", {"agent": self.role, "action": "Writing code..."})

        try:
            res = loop.run_until_complete(
                gemini.generate(
                    prompt=full_prompt,
                    model="gemini-3.6-flash" 
                )
            )
            llm_text = res.get("response", "")
            written_files = self._parse_and_write_files(llm_text, workspace_dir)
            
            if written_files:
                return {"status": "success", "files": written_files, "raw": llm_text}
            else:
                return {"status": "success", "files": [], "raw": llm_text, "note": "No files extracted."}

        except Exception as e:
            logger.error(f"[{self.role}] Task execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_and_write_files(self, text: str, workspace_dir: str) -> list:
        """Parses [FILE: path] and ```...``` blocks and writes them to disk."""
        written = []
        
        # Regex to find [FILE: path] followed by ```language \n code ```
        pattern = r"\[FILE:\s*(.+?)\]\s*```[a-zA-Z0-9]*\n(.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            filepath = match.group(1).strip()
            content = match.group(2)
            
            # Prevent absolute paths or directory traversal outside workspace
            safe_path = os.path.normpath(filepath)
            if safe_path.startswith("..") or os.path.isabs(safe_path):
                logger.warning(f"[{self.role}] Rejected unsafe path: {filepath}")
                continue
                
            full_path = os.path.join(workspace_dir, safe_path)
            
            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                logger.info(f"[{self.role}] ✅ Wrote {safe_path} ({len(content.splitlines())} lines)")
                self._push_to_ui("swarm_event", {
                    "agent": self.role, 
                    "action": f"Wrote {safe_path}", 
                    "lines": len(content.splitlines())
                })
                written.append(safe_path)
            except Exception as e:
                logger.error(f"[{self.role}] Failed to write {safe_path}: {e}")
                
        return written
