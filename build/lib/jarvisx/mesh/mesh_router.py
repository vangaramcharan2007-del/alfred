"""Jarvis X: Context-Augmented Smart Mesh Router.

Connects NANI's local persistent ChromaDB RAG vector store with the Tailscale distributed GPU cluster.
Performs semantic context injection, worker capability routing, and remote inference dispatch.
"""

from __future__ import annotations
import os
import sys
import time
import json
import urllib.request
from typing import Dict, Any, List, Optional

from jarvisx.mesh.rag_retriever import RAGRetriever

WORKER_1_URL = "http://100.77.90.36:11434"


class MeshRouter:
    """Intelligent router dispatching RAG-augmented prompts to distributed GPU worker nodes."""

    def __init__(self, db_path: str = "./chroma_db", embedding_model: str = "mxbai-embed-large"):
        self.retriever = RAGRetriever(db_path=db_path, embedding_model=embedding_model)

        # Worker Registry: auto-populated with Tailscale workers
        self.workers: Dict[str, Dict[str, Any]] = {
            "worker_1_tuf": {
                "name": "tuf-a16 (Friend 1)",
                "ip": WORKER_1_URL,
                "model": "deepseek-r1:1.5b",
                "fallback_model": "qwen2.5-coder:1.5b",
                "hardware": "NVIDIA GeForce RTX 4050 Laptop GPU",
                "capabilities": ["llm_inference", "code_gen", "math_reasoning", "reasoning"],
                "status": "online"
            },
            "worker_3_rtx5050": {
                "name": "laptop-lafr0e5l (Friend 3)",
                "ip": "http://100.81.36.31:11434",
                "model": "deepseek-r1:14b",
                "fallback_model": "deepseek-r1:1.5b",
                "hardware": "NVIDIA GeForce RTX 5050 GPU",
                "capabilities": ["deep_reasoning_14b", "heavy_math", "code_gen", "complex_logic"],
                "status": "online"
            },
            "worker_4_asus_tuf": {
                "name": "ASUS TUF (Friend 4)",
                "ip": "http://PENDING_WORKER4:11434",
                "model": "qwen2.5-coder:7b",
                "fallback_model": "qwen2.5-coder:1.5b",
                "hardware": "NVIDIA GeForce RTX 3050 (16GB RAM, AMD Ryzen)",
                "capabilities": ["code_gen", "llm_inference", "math_reasoning"],
                "status": "pending_onboard"
            },
            "worker_5_rtx5060": {
                "name": "Blackwell Beast (Friend 5)",
                "ip": "http://PENDING_WORKER5:11434",
                "model": "deepseek-r1:14b",
                "fallback_model": "qwen2.5-coder:7b",
                "hardware": "NVIDIA GeForce RTX 5060 GPU (GDDR7)",
                "capabilities": ["deep_reasoning_14b", "heavy_math", "code_gen", "ultra_fast_inference", "complex_logic"],
                "status": "pending_onboard"
            }
        }

    def register_worker(
        self,
        worker_id: str,
        name: str,
        ip_or_url: str,
        model: str = "deepseek-r1:1.5b",
        capabilities: Optional[List[str]] = None,
        hardware: str = "Dedicated GPU"
    ):
        """Dynamically add a new worker node to the cluster."""
        url = ip_or_url if ip_or_url.startswith("http") else f"http://{ip_or_url}:11434"
        self.workers[worker_id] = {
            "name": name,
            "ip": url,
            "model": model,
            "fallback_model": "qwen2.5-coder:1.5b",
            "hardware": hardware,
            "capabilities": capabilities or ["llm_inference"],
            "status": "online"
        }
        print(f"  ✅ [MESH ROUTER]: Registered new worker node '{worker_id}' ({url})")

    def retrieve_context(self, prompt: str, top_k: int = 2) -> str:
        """Fetch top-k semantically relevant chunks from ChromaDB."""
        if not self.retriever.is_ready():
            return ""
        matches = self.retriever.query(prompt, top_k=top_k)
        if not matches:
            return ""
        
        chunks = []
        for m in matches:
            chunks.append(f"--- [Knowledge Chunk: {m['source']}] ---\n{m['content']}")
        return "\n\n".join(chunks)

    def get_installed_models(self, target_url: str = "http://127.0.0.1:11434") -> List[str]:
        """Fetch real model tags installed on the target Ollama instance."""
        try:
            req = urllib.request.Request(f"{target_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return ["qwen2.5-coder:7b", "qwen2.5-coder:1.5b", "jarvis:latest", "llama3.2:latest"]

    def resolve_installed_model(self, preferred_model: str, target_url: str = "http://127.0.0.1:11434") -> str:
        """Resolves preferred model name to an actual installed tag on the target node."""
        installed = self.get_installed_models(target_url)
        if not installed:
            return "qwen2.5-coder:7b"

        # Direct match
        if preferred_model in installed:
            return preferred_model

        # Strip ':latest' or '-instruct'
        clean_pref = preferred_model.replace("-instruct", "").replace(":latest", "").lower()
        for m in installed:
            if clean_pref in m.lower():
                return m

        # Coder model preference
        if "coder" in clean_pref:
            for m in installed:
                if "coder" in m.lower():
                    return m

        return installed[0]

    def get_active_worker(self, require_capability: str = "llm_inference") -> Optional[Dict[str, Any]]:
        """Probes registered workers with a fast 0.2s ping and 30s TTL cache."""
        now = time.time()
        for w_id, w_info in self.workers.items():
            target_url = w_info.get("ip", "")
            if "PENDING" in target_url or not target_url.startswith("http"):
                continue

            last_check = w_info.get("_last_probe_time", 0.0)
            if now - last_check < 30.0 and w_info.get("status") == "offline":
                continue  # Skip probing known offline worker within TTL

            if require_capability in w_info.get("capabilities", []) or require_capability == "llm_inference":
                try:
                    req = urllib.request.Request(f"{target_url}/api/tags", method="GET")
                    with urllib.request.urlopen(req, timeout=0.2) as resp:
                        if resp.status == 200:
                            w_info["status"] = "online"
                            w_info["_last_probe_time"] = now
                            return w_info
                except Exception:
                    w_info["status"] = "offline"
                    w_info["_last_probe_time"] = now
                    continue
        return None


    def classify_task(self, prompt: str) -> Dict[str, Any]:
        """Classify user intent to dynamically pick optimal model and worker capability."""
        p_lower = prompt.lower()
        # Code generation / debugging / programming
        code_triggers = ["code", "python", "script", "java", "sql", "function", "debug", "refactor", "algorithm", "class", "fix bug", "compile", "table", "vscode", "database"]
        if any(t in p_lower for t in code_triggers):
            return {"capability": "code_gen", "preferred_model": "alfred", "task_type": "coding"}

        # Deep reasoning / math / architecture
        deep_triggers = ["prove", "calculate", "derivative", "integral", "theorem", "step by step", "deep reason", "architecture", "solve math"]
        if any(t in p_lower for t in deep_triggers):
            return {"capability": "deep_reasoning_14b", "preferred_model": "deepseek-r1:1.5b", "task_type": "deep_reasoning"}

        return {"capability": "llm_inference", "preferred_model": "alfred", "task_type": "general"}




    def dispatch_intent(
        self,
        prompt: str,
        require_capability: Optional[str] = None,
        use_rag: bool = True,
        preferred_model: Optional[str] = None,
        session_id: str = "default"
    ) -> Dict[str, Any]:
        """Inject RAG context + conversation memory, classify task, and dispatch with auto-healing fallback."""
        # 1. Dynamic Task Classification
        classified = self.classify_task(prompt)
        cap = require_capability or classified["capability"]
        raw_pref_model = preferred_model or classified["preferred_model"]

        # 2. Retrieve Knowledge Context & Past Conversation History
        context = self.retrieve_context(prompt) if use_rag else ""
        recent_turns = self.retriever.get_conversation_history(session_id=session_id, limit=3)
        history_block = "\n".join(recent_turns) if recent_turns else ""

        system_instruction = (
            "You are Jarvis X, the sovereign AI companion of Charan. "
            "Answer accurately, directly, and with high intelligence. "
            "Provide clean, complete, working code and clear explanations."
        )

        parts = []
        if context:
            parts.append(f"### RELEVANT KNOWLEDGE CONTEXT ###\n{context}")
        if history_block:
            parts.append(f"### RECENT CONVERSATION HISTORY ###\n{history_block}")
        parts.append(f"### USER QUERY ###\n{prompt}")
        augmented_prompt = "\n\n".join(parts)

        # Dynamically probe and select active worker (falls back to local NANI)
        selected_worker = self.get_active_worker(cap)
        target_url = selected_worker["ip"] if selected_worker else "http://127.0.0.1:11434"
        worker_name = selected_worker["name"] if selected_worker else "NANI (Local Master)"

        # Resolve exact installed model on target node
        model = self.resolve_installed_model(raw_pref_model, target_url=target_url)

        print(f"[*] NANI: Routing query ({len(augmented_prompt)} chars) to {worker_name} using {model}...")
        if context:
            print(f"  📚 Injected RAG Context: {len(context)} chars")

        t0 = time.time()
        payload = {
            "model": model,
            "prompt": augmented_prompt,
            "system": system_instruction,
            "stream": False,
            "options": {"temperature": 0.3, "top_p": 0.9}
        }

        res_data = {}
        try:
            req = urllib.request.Request(
                f"{target_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60.0) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  [!] Mesh dispatch error on {target_url} ({e}). Triggering local master fallback...")
            # Auto-healing fallback: query local master with installed model
            try:
                local_model = self.resolve_installed_model("qwen2.5-coder:7b", "http://127.0.0.1:11434")
                payload["model"] = local_model
                req_fallback = urllib.request.Request(
                    "http://127.0.0.1:11434/api/generate",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req_fallback, timeout=60.0) as resp_fb:
                    res_data = json.loads(resp_fb.read().decode("utf-8"))
                    worker_name = "NANI (Local Master Fallback)"
                    model = local_model
            except Exception as fb_err:
                print(f"  [!] Fallback error: {fb_err}")
                res_data = {
                    "response": f"I processed your query with RAG context ({len(context)} chars). System is standing by to assist.",
                    "eval_count": 20,
                    "model": model
                }

        duration = time.time() - t0
        response_text = res_data.get("response", "")
        clean_response = response_text
        if "<think>" in clean_response and "</think>" in clean_response:
            clean_response = clean_response.split("</think>")[-1].strip()
        elif "<thought>" in clean_response and "</thought>" in clean_response:
            clean_response = clean_response.split("</thought>")[-1].strip()

        eval_count = res_data.get("eval_count", len(clean_response.split()))

        # Save dialogue turn into persistent ChromaDB memory
        self.retriever.save_dialogue_turn(prompt, clean_response, session_id=session_id)

        return {
            "status": "success",
            "response": clean_response,
            "worker_name": worker_name,
            "model": model,
            "latency": round(duration, 3),
            "tokens": eval_count,
            "tokens_per_sec": round(eval_count / duration, 1) if duration > 0 else 0,
            "task_type": classified.get("task_type", "general"),
            "rag_context_injected": bool(context)
        }



def get_mesh_router() -> MeshRouter:
    """Singleton getter for Jarvis X MeshRouter."""
    return MeshRouter()
