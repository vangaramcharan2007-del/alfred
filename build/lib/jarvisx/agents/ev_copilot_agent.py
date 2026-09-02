"""
E-V Co-Pilot Subordinate Agent (Operates Under Alfred Sovereign Butler).
========================================================================
E-V is Alfred's first officer & dedicated field specialist:
- 🎙️ Vocal Interface & Dynamic Tone (Microsoft Neural Ava)
- 👀 Spider-Sense Screen Vision & OCR
- 📐 Transforms & Boundary Value Math Specialist (Dr. E. Suresh)
- ⚡ ADHD Focus Coach & Gamified Micro-Sprints
- 🛡️ Controlled and monitored by Alfred's Sovereign Security Gate
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvisx.agents.ev")


class EVCoPilotAgent:
    """Specialized Voice, Vision, and Study Agent under Alfred's Command."""

    _instance: Optional["EVCoPilotAgent"] = None

    def __init__(self, supervisor_name: str = "Alfred"):
        self.name = "E-V"
        self.supervisor = supervisor_name
        self.role = "Neural Voice, Vision & ADHD Co-Pilot"
        self.capabilities = [
            "neural_voice",
            "screen_vision",
            "math_pde_solver",
            "adhd_focus_quest",
            "live_pair_programmer"
        ]
        self.active_quest = None
        logger.info(f"[E-V] Initialized under supervisor: {self.supervisor}")

    @classmethod
    def get_instance(cls) -> "EVCoPilotAgent":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def speak(self, text: str) -> None:
        """Speak out loud using Microsoft Edge Neural Voice."""
        from jarvisx.automation.ev_neural_voice import speak_ev_neural
        logger.info(f"[E-V Voice] Speaking under Alfred's delegation: {text[:60]}...")
        speak_ev_neural(text)

    def analyze_screen(self) -> Dict[str, Any]:
        """Capture active screen and run OCR/Vision analysis."""
        from jarvisx.automation.ev_math_screen_snapper import snap_and_solve
        logger.info("[E-V Vision] Capturing screen under Alfred's command...")
        # Solves and speaks
        snap_and_solve()
        return {"status": "success", "agent": "E-V", "delegated_by": self.supervisor}

    def solve_math(self, problem_type: str = "1d_wave") -> Dict[str, Any]:
        """Solve PDE/Fourier/Transforms problem from Dr. E. Suresh's curriculum."""
        from jarvisx.agents.transforms_math_agent import TransformsMathAgent
        agent = TransformsMathAgent.get_instance()
        
        if problem_type == "1d_heat":
            sol = agent.solve_1d_heat_equation()
        else:
            sol = agent.solve_1d_wave_equation()

        speech = f"Problem solved under Alfred's supervision! Step-by-step derivation for {sol.topic} is ready, boss!"
        self.speak(speech)
        return {
            "status": "success",
            "title": sol.topic,
            "solution_markdown": sol.to_markdown(),
            "delegated_by": self.supervisor
        }

    def start_adhd_quest(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Start a gamified focus sprint."""
        msg = f"Alfred approved your {duration_minutes}-minute Spider-Quest, boss! Let's lock in and score 100 XP!"
        self.speak(msg)
        return {"status": "active", "duration_min": duration_minutes, "xp_reward": 100}

    def execute_delegated_task(self, task_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Entrypoint for Alfred to delegate tasks to E-V."""
        payload = payload or {}
        logger.info(f"[E-V] Executing delegated task from {self.supervisor}: {task_name}")

        if task_name == "speak":
            self.speak(payload.get("text", "At your service!"))
            return {"status": "success", "action": "speak"}
        elif task_name == "analyze_screen":
            return self.analyze_screen()
        elif task_name == "solve_math":
            return self.solve_math(payload.get("type", "1d_wave"))
        elif task_name == "adhd_quest":
            return self.start_adhd_quest(payload.get("duration", 5))
        else:
            return {"status": "unknown_task", "task": task_name}
