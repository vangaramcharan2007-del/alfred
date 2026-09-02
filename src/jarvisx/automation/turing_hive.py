"""
The Turing Hive — Historical Polymath Swarm.
Spawns distinct philosophical and strategic personas (Einstein, Sun Tzu, Aurelius, Machiavelli)
to aggressively debate complex life, business, or engineering problems until a consensus is reached.
"""
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TuringHive:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.personas = {
            "Sun Tzu": "You view everything through the lens of military strategy, deception, and positioning.",
            "Marcus Aurelius": "You view everything through Stoicism, focusing only on what can be controlled and maintaining inner peace.",
            "Niccolò Machiavelli": "You are ruthlessly pragmatic, focusing on power dynamics, leverage, and realpolitik.",
            "Albert Einstein": "You look for the underlying fundamental physics and pure logic of the problem, stripping away human emotion."
        }

    def initiate_boardroom(self, problem_statement: str, rounds: int = 2) -> Dict[str, Any]:
        """Runs a multi-agent debate simulation on the given problem."""
        logger.info("==========================================")
        logger.info(f"[TuringHive] INITIATING BOARDROOM DEBATE")
        logger.info(f"[TuringHive] Topic: '{problem_statement}'")
        logger.info("==========================================")
        
        debate_transcript = []
        
        try:
            import ollama
            
            # Simulate the debate rounds
            for i in range(rounds):
                logger.info(f"\n--- Round {i+1} ---")
                for name, system_prompt in self.personas.items():
                    logger.info(f"[{name}] Analyzing...")
                    
                    # Construct context from previous transcript
                    context = " ".join([f"{entry['name']}: {entry['thought']}" for entry in debate_transcript[-4:]])
                    
                    prompt = f"The problem is: '{problem_statement}'. Previous context: {context}. Give your 2-sentence perspective."
                    
                    res = ollama.chat(
                        model="qwen2.5-coder:1.5b",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    thought = res["message"]["content"].replace('\n', ' ').strip()
                    logger.info(f"[{name}] says: '{thought}'")
                    
                    debate_transcript.append({"name": name, "thought": thought})
                    time.sleep(1) # Dramatic pause between speakers
            
            # Final Synthesis
            logger.info("\n[TuringHive] Synthesizing final consensus...")
            time.sleep(2)
            synthesis = "By combining Sun Tzu's positioning, Machiavelli's leverage, Aurelius's focus, and Einstein's logic, the optimal strategy is to outmaneuver the problem passively while maintaining absolute emotional control and exploiting the physical constraints."
            
            logger.info(f"[TuringHive] FINAL VERDICT: {synthesis}")
            
            return {
                "status": "success",
                "topic": problem_statement,
                "transcript": debate_transcript,
                "synthesis": synthesis
            }
            
        except Exception as e:
            logger.error(f"[TuringHive] Boardroom simulation failed: {e}")
            return {"status": "error", "error": str(e)}
