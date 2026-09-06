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

    def _call_llm(self, full_prompt: str) -> str:
        """Call Groq first, then OpenRouter, then Gemini."""
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                resp = client.chat.completions.create(
                    model=os.getenv("CODER_MODEL", "openai/gpt-oss-120b"),
                    messages=[
                        {"role": "system", "content": "You are an autonomous senior developer. Write complete, functional code without omissions. Always specify target file using [FILE: filename.ext] before the code block."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_completion_tokens=4096,
                    temperature=0.2
                )
                text = resp.choices[0].message.content or ""
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"[{self.role}] Groq generation failed, attempting fallback: {e}")

        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            try:
                import httpx
                resp = httpx.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek/deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "You are an autonomous senior developer. Always specify target file using [FILE: filename.ext] before code blocks."},
                            {"role": "user", "content": full_prompt}
                        ],
                        "max_tokens": 4096
                    },
                    timeout=30.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"] or ""
                    if text.strip():
                        return text
            except Exception as e:
                logger.warning(f"[{self.role}] OpenRouter fallback failed: {e}")

        # Fallback to Gemini
        gemini = self._get_llm()
        if gemini:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            res = loop.run_until_complete(
                gemini.generate(prompt=full_prompt, model="gemini-1.5-flash")
            )
            return res.get("response", "")

        return ""

    def execute_task(self, task: str, workspace_dir: str = ".") -> Dict[str, Any]:
        """Runs the task through the LLM and writes real files to disk."""
        logger.info(f"[{self.role}] Executing task: {task}")
        self._push_to_ui("swarm_event", {"agent": self.role, "action": f"Analyzing task: {task}"})

        system_prompt = (
            f"{self.persona}\n"
            "You are an autonomous agent capable of writing files directly to disk.\n"
            "You MUST specify every file using this format:\n\n"
            "[FILE: filename.ext]\n"
            "```python\n"
            "# complete code here\n"
            "```\n\n"
            "Do not omit any code. Write production-ready code."
        )

        full_prompt = f"Role: {self.role}\n{system_prompt}\n\nTask: {task}"
        self._push_to_ui("swarm_event", {"agent": self.role, "action": "Writing code..."})

        try:
            llm_text = self._call_llm(full_prompt)
            if not llm_text:
                return {"status": "error", "error": "All LLM Providers failed to generate code."}

            written_files = self._parse_and_write_files(llm_text, workspace_dir, default_filename="generated_agent_solution.py")

            if written_files:
                return {"status": "success", "files": written_files, "raw": llm_text[:500]}
            else:
                return {"status": "success", "files": [], "raw": llm_text[:500], "note": "No code blocks found."}

        except Exception as e:
            logger.error(f"[{self.role}] Task execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_and_write_files(self, text: str, workspace_dir: str, default_filename: str = "solution.py") -> list:
        """Parses [FILE: path] and ```...``` blocks and writes them to disk."""
        written = []

        # 1. Regex to find [FILE: path] followed by ```language \n code ```
        pattern = r"\[FILE:\s*(.+?)\]\s*```[a-zA-Z0-9_-]*\n(.*?)```"
        matches = list(re.finditer(pattern, text, re.DOTALL))

        # 2. Fallback regex if LLM omitted [FILE: path] but wrote ```...```
        if not matches:
            fallback_pattern = r"```([a-zA-Z0-9_-]+)?\n(.*?)```"
            fb_matches = list(re.finditer(fallback_pattern, text, re.DOTALL))
            for i, match in enumerate(fb_matches):
                lang = (match.group(1) or "py").lower()
                ext = "py" if "py" in lang else ("html" if "html" in lang else ("js" if "js" in lang else "txt"))
                fname = f"generated_solution_{i+1}.{ext}" if len(fb_matches) > 1 else default_filename
                content = match.group(2)
                if self._write_single_file(workspace_dir, fname, content):
                    written.append(fname)
            return written

        for match in matches:
            filepath = match.group(1).strip()
            content = match.group(2)
            if self._write_single_file(workspace_dir, filepath, content):
                written.append(filepath)

        return written

    def _write_single_file(self, workspace_dir: str, filepath: str, content: str) -> bool:
        """Helper to safely write code to disk."""
        safe_path = os.path.normpath(filepath)
        if safe_path.startswith("..") or os.path.isabs(safe_path):
            safe_path = os.path.basename(safe_path)

        full_path = os.path.join(workspace_dir, safe_path)
        try:
            os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            lines_count = len(content.splitlines())
            logger.info(f"[{self.role}] ✅ Wrote {safe_path} ({lines_count} lines)")
            self._push_to_ui("swarm_event", {
                "agent": self.role,
                "action": f"Wrote {safe_path}",
                "lines": lines_count
            })
            return True
        except Exception as e:
            logger.error(f"[{self.role}] Failed to write {safe_path}: {e}")
            return False
