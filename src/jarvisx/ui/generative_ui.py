"""
Generative Fluid UI — The "Her" Interface.
Dynamically generates custom HTML/JS/CSS widgets on the fly via LLM 
and streams them to the HUD based on user intent.
"""
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GenerativeUIEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def generate_ui(self, intent: str) -> Dict[str, Any]:
        """Hallucinates a custom UI component based on context."""
        logger.info(f"[GenerativeUI] Compiling dynamic fluid interface for: '{intent}'")
        
        try:
            import ollama
            prompt = f"Write a visually stunning, single-file HTML/CSS/JS widget (dark theme, neon accents) for this intent: {intent}. Return ONLY raw HTML."
            
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            html_payload = res["message"]["content"]
            if "```html" in html_payload:
                html_payload = html_payload.split("```html")[1].split("```")[0].strip()
                
            logger.info("[GenerativeUI] UI Component compiled. Pushing to HUD...")
            
            # Push to HUD via WebSocket
            try:
                from jarvisx.dashboard.hud_server import push_event_sync
                push_event_sync("fluid_ui_inject", {"html": html_payload})
            except Exception:
                pass
                
            return {
                "status": "success",
                "intent": intent,
                "ui_payload_size": len(html_payload)
            }
        except Exception as e:
            logger.error(f"[GenerativeUI] Fluid compilation failed: {e}")
            return {"status": "error", "error": str(e)}
