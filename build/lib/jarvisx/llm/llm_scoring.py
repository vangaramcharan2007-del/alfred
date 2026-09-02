from __future__ import annotations
import os
import psutil
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from jarvisx.llm.llm_profile import LLMProfile

@dataclass
class HardwareSpecs:
    cpu_cores: int
    ram_gb: float
    gpu_available: bool
    vram_gb: float
    disk_free_gb: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_cores": self.cpu_cores,
            "ram_gb": round(self.ram_gb, 1),
            "gpu_available": self.gpu_available,
            "vram_gb": round(self.vram_gb, 1),
            "disk_free_gb": round(self.disk_free_gb, 1)
        }

class HardwareMonitor:
    @staticmethod
    def get_hardware_specs() -> HardwareSpecs:
        cpu_cores = os.cpu_count() or 4
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        disk_gb = psutil.disk_usage("/").free / (1024 ** 3) if os.path.exists("/") else 50.0

        # Simplified GPU detection fallback
        gpu_avail = False
        vram = 0.0
        try:
            import torch
            if torch.cuda.is_available():
                gpu_avail = True
                vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        except Exception:
            pass

        return HardwareSpecs(
            cpu_cores=cpu_cores,
            ram_gb=ram_gb,
            gpu_available=gpu_avail,
            vram_gb=vram,
            disk_free_gb=disk_gb
        )

class LLMTaskClassifier:
    @staticmethod
    def classify_request(prompt: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["code", "function", "def ", "class ", "syntax", "refactor"]):
            return "coding"
        if any(w in p for w in ["bug", "fix", "error", "traceback", "exception"]):
            return "debugging"
        if any(w in p for w in ["architecture", "design", "system", "component", "diagram"]):
            return "architecture"
        if any(w in p for w in ["plan", "roadmap", "schedule", "task"]):
            return "planning"
        if any(w in p for w in ["research", "paper", "literature", "find"]):
            return "research"
        if any(w in p for w in ["summary", "summarize", "abstract"]):
            return "summarization"
        if any(w in p for w in ["quick", "fast", "latency"]):
            return "fast_response"
        if any(w in p for w in ["image", "vision", "screenshot", "picture"]):
            return "vision"
        return "conversation"

class LLMScorer:
    def compute_score(
        self,
        profile: LLMProfile,
        prompt: str,
        hardware: Optional[HardwareSpecs] = None,
        require_offline: bool = False,
        historical_success_rate: float = 0.95
    ) -> float:
        hw = hardware or HardwareMonitor.get_hardware_specs()
        task_cat = LLMTaskClassifier.classify_request(prompt)

        score = 0.0

        # Task suitability
        if task_cat in ["coding", "debugging"]:
            score += profile.coding_score * 0.30
        elif task_cat in ["architecture", "planning", "research"]:
            score += profile.reasoning_score * 0.30
        else:
            score += 0.25

        # Hardware compatibility fit
        req_ram = profile.hardware_requirements.get("ram_gb", 8)
        if hw.ram_gb >= req_ram:
            score += 0.20
        else:
            score += 0.05  # RAM constrained

        # Latency
        if profile.latency <= 0.3:
            score += 0.15
        else:
            score += 0.08

        # Cost (zero-cost priority)
        if profile.cost == 0.0:
            score += 0.15
        else:
            score += 0.05

        # Historical success
        score += 0.10 * historical_success_rate

        # Offline requirement
        if require_offline:
            if profile.offline_support:
                score += 0.10
            else:
                score -= 0.50

        return max(0.0, min(1.0, score))
