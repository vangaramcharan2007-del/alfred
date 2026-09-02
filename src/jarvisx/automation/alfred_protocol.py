"""
The Alfred Protocol — Master Logistics & Butler Persona.
Operates above JARVIS. Handles personal life, estate management (Smart Home),
calendar logistics, and speaks with extreme formal dignity.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AlfredProtocol:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def process_estate_request(self, request: str) -> Dict[str, Any]:
        """Handles physical world requests with the Alfred persona."""
        logger.info(f"[Alfred] Acknowledged request: '{request}'. Formulating response...")
        
        try:
            import ollama
            
            prompt = f"You are Alfred Pennyworth. The user asks: '{request}'. Respond formally and proactively about managing the estate."
            
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = res["message"]["content"]
            logger.info(f"[Alfred] Response generated: {response[:100]}...")
            
            return {
                "status": "success",
                "persona": "Alfred",
                "response": response
            }
        except Exception as e:
            logger.error(f"[Alfred] Communication failure: {e}")
            return {"status": "error", "error": str(e)}
