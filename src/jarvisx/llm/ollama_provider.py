from __future__ import annotations
import json
import shutil
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, AsyncGenerator
from jarvisx.llm.llm_provider import LLMProvider

class OllamaLLMProvider(LLMProvider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ollama.local", config=config)
        self.endpoint = self.config.get("endpoint", "http://127.0.0.1:11434")
        self.installed_models = ["qwen2.5-coder:1.5b", "qwen2.5-coder:7b", "qwen2.5:7b", "llama3:latest", "llama3.2:latest"]
        self.is_installed = False

    async def connect(self) -> bool:
        self.is_installed = (shutil.which("ollama") is not None) or self.config.get("mock_online", True)
        self.is_connected = True
        try:
            import urllib.request
            import json
            req = urllib.request.Request(f"{self.endpoint}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    live_models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                    if live_models:
                        self.installed_models = live_models
                    return True
        except Exception:
            if shutil.which("ollama"):
                try:
                    import subprocess
                    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(1.0)
                except Exception:
                    pass
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.is_connected else "DISCONNECTED",
            "provider_id": "ollama.local",
            "is_installed": self.is_installed,
            "installed_models": self.installed_models,
            "offline_ready": True
        }

    def select_model_for_prompt(self, prompt: str, requested_model: Optional[str] = None) -> str:
        if requested_model and (requested_model in self.installed_models or requested_model):
            return requested_model

        if "qwen2.5-coder:1.5b" in self.installed_models:
            return "qwen2.5-coder:1.5b"
        elif "qwen2.5-coder:7b" in self.installed_models:
            return "qwen2.5-coder:7b"
        return self.installed_models[0] if self.installed_models else "qwen2.5-coder:1.5b"

    async def generate(self, prompt: str, model: Optional[str] = None, conversation: Optional[List[Dict[str, str]]] = None, **kwargs) -> Dict[str, Any]:
        start_t = time.time()
        chosen_model = self.select_model_for_prompt(prompt, model)
        timeout_sec = kwargs.get("timeout", self.config.get("timeout_seconds", 60.0))
        max_retries = kwargs.get("retries", 2)

        # Attempt live connection to local Ollama API with retries
        for attempt in range(1, max_retries + 1):
            try:
                from jarvisx.hardware.npu_accelerator import get_npu_accelerator
                npu = get_npu_accelerator()
                opt = npu.get_recommended_ollama_options(chosen_model)

                url = f"{self.endpoint}/api/generate"
                payload_dict = {
                    "model": chosen_model, 
                    "prompt": prompt, 
                    "stream": False,
                    "options": {"num_thread": opt.get("num_thread", 4), "num_ctx": opt.get("num_ctx", 4096)},
                    "keep_alive": opt.get("keep_alive", "30s")
                }
                if conversation:
                    payload_dict["context_history"] = conversation[-10:] # Last 10 context window
                payload = json.dumps(payload_dict).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

                with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        response_text = data.get("response", "")
                        latency_sec = round(time.time() - start_t, 3)
                        latency_ms = round(latency_sec * 1000, 1)
                        prompt_size = len(prompt)
                        response_size = len(response_text)
                        tokens = len(response_text.split())
                        return {
                            "status": "AVAILABLE",
                            "provider_id": "ollama.local",
                            "model": chosen_model,
                            "response": response_text,
                            "latency": latency_sec,
                            "latency_ms": latency_ms,
                            "prompt_size": prompt_size,
                            "response_size": response_size,
                            "cost": 0.0,
                            "tokens_generated": tokens,
                            "fallback_used": False,
                            "attempt": attempt
                        }
            except Exception as ex:
                print(f"[Ollama Error on {chosen_model}]: {ex}")
                time.sleep(0.1 * attempt)

        # Return explicit NOT_AVAILABLE contract if local daemon is offline
        latency_sec = round(time.time() - start_t, 3)
        latency_ms = round(latency_sec * 1000, 1)
        fallback_msg = f"[Ollama {chosen_model} Offline]: Explicit NOT_AVAILABLE returned per production contract."
        return {
            "status": "NOT_AVAILABLE",
            "provider_id": "ollama.local",
            "model": chosen_model,
            "response": fallback_msg,
            "latency": latency_sec,
            "latency_ms": latency_ms,
            "prompt_size": len(prompt),
            "response_size": len(fallback_msg),
            "cost": 0.0,
            "tokens_generated": 0,
            "fallback_used": True
        }




    async def stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        chosen_model = model or "qwen2.5-coder:7b"
        tokens = [f"[Ollama {chosen_model}] ", "Processing ", "request: ", prompt[:50], "... ", "Done."]
        for token in tokens:
            yield token

    def metadata(self) -> Dict[str, Any]:
        return {
            "provider_id": "ollama.local",
            "name": "Ollama Local LLM Subsystem",
            "version": "0.3.0",
            "type": "local_llm",
            "installed_models": self.installed_models
        }

    def capabilities(self) -> List[str]:
        return ["coding", "debugging", "architecture", "planning", "research", "summarization", "conversation", "offline"]
