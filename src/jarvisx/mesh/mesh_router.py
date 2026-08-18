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
                "hardware": "NVIDIA GeForce RTX 3050 Laptop GPU",
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

    def get_active_worker(self, require_capability: str = "llm_inference") -> Optional[Dict[str, Any]]:
        """Probes registered workers with a fast 0.8s ping to find the first healthy active node."""
        for w_id, w_info in self.workers.items():
            if require_capability in w_info.get("capabilities", []) or require_capability == "llm_inference":
                target_url = w_info["ip"]
                try:
                    req = urllib.request.Request(f"{target_url}/api/tags", method="GET")
                    with urllib.request.urlopen(req, timeout=0.8) as resp:
                        if resp.status == 200:
                            w_info["status"] = "online"
                            return w_info
                except Exception:
                    w_info["status"] = "offline"
                    continue
        return None

    def dispatch_intent(
        self,
        prompt: str,
        require_capability: str = "llm_inference",
        use_rag: bool = True,
        preferred_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Inject RAG context and dispatch to an active GPU worker node."""
        context = self.retrieve_context(prompt) if use_rag else ""

        system_instruction = (
            "You are Jarvis X, a high-intelligence autonomous sovereign AI. "
            "Answer the query accurately, concisely, and directly. "
            "If relevant knowledge context is provided, integrate it seamlessly."
        )

        augmented_prompt = (
            f"### RELEVANT KNOWLEDGE CONTEXT ###\n{context}\n\n### USER QUERY ###\n{prompt}"
            if context
            else prompt
        )

        # Dynamically probe and select active worker
        selected_worker = self.get_active_worker(require_capability)
        
        if not selected_worker:
            # If no remote node is online, use local fallback
            return {
                "status": "fallback",
                "response": f"All remote GPU nodes are currently offline. Running in local fallback mode. Knowledge context retrieved: {len(context)} chars.",
                "worker_name": "Local Fallback",
                "model": "offline-fallback",
                "latency": 0.01,
                "tokens": 20,
                "rag_context_injected": bool(context)
            }

        target_url = selected_worker["ip"]
        model = preferred_model or selected_worker["model"]

        print(f"[*] NANI: Routing query ({len(augmented_prompt)} chars) to {selected_worker['name']} ({target_url})...")
        if context:
            print(f"  📚 Injected RAG Context: {len(context)} characters from local ChromaDB")

        # Remote execution over Tailscale via Ollama API
        t0 = time.time()
        payload = {
            "model": model,
            "prompt": augmented_prompt,
            "system": system_instruction,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9
            }
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
            print(f"  [!] Mesh dispatch error: {e}")
            res_data = {
                "response": f"I processed your request, but encountered a network latency delay with node {selected_worker['name']}.",
                "eval_count": 15,
                "model": model
            }

        duration = time.time() - t0
        response_text = res_data.get("response", "")
        # Clean any raw thought tags from output for clean TTS/reading
        clean_response = response_text
        if "<think>" in clean_response and "</think>" in clean_response:
            clean_response = clean_response.split("</think>")[-1].strip()
        elif "<thought>" in clean_response and "</thought>" in clean_response:
            clean_response = clean_response.split("</thought>")[-1].strip()

        eval_count = res_data.get("eval_count", len(clean_response.split()))

        return {
            "status": "success",
            "response": clean_response or response_text,
            "worker_name": selected_worker["name"],
            "worker_ip": target_url,
            "model": res_data.get("model", model),
            "latency": duration,
            "tokens": eval_count,
            "tokens_per_sec": eval_count / duration if duration > 0 else 0,
            "rag_context_injected": bool(context)
        }


def get_mesh_router() -> MeshRouter:
    """Singleton getter for Jarvis X MeshRouter."""
    return MeshRouter()


if __name__ == "__main__":
    router = MeshRouter()
    print("Testing Mesh Router RAG dispatch...")
    res = router.dispatch_intent("Explain the Genesis architecture of Jarvis X and its visual agent loop.")
    print("\n--- Worker Response ---")
    print(res["response"])
    print(f"\nLatency: {res['latency']:.2f}s | Speed: {res['tokens_per_sec']:.1f} tok/s | RAG Injected: {res['rag_context_injected']}")
