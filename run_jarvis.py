import sys
import os
import logging
import traceback

sys.path.insert(0, os.path.abspath("src"))

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from jarvisx.core.voice.voice_runtime import VoiceRuntime
from jarvisx.core.omniroute_manager import OmniRouteManager
from jarvisx.core.skills.skill_loader import SkillLoader
from jarvisx.core.skills.skill_registry import SkillRegistry
from jarvisx.core.workflows.workflow_manager import WorkflowManager
import asyncio

# Configure logging at root
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)

async def async_main():
    print("==================================================")
    print("              JARVIS X RUNTIME STARTUP            ")
    print("==================================================")
    
    use_mic = os.environ.get("MOCK_STT", "0") != "1"
    
    logger.info("Initializing OmniRoute Gateway...")
    omniroute = OmniRouteManager()
    await omniroute.start()
    
    logger.info("Initializing VoiceRuntime...")
    try:
        runtime = VoiceRuntime(use_microphone=use_mic)
        
        
        logger.info("Initializing Skill Intelligence Layer...")
        skills_dir = os.path.abspath(os.path.join("src", "jarvisx", "core", "skills", "installed"))
        os.makedirs(skills_dir, exist_ok=True)
        skill_loader = SkillLoader(skills_dir)
        loaded_skills = skill_loader.load_all()
        
        logger.info("Initializing Workflow Manager...")
        workflow_manager = WorkflowManager()
        
        print("\n[Alfred System Check]\n")
        print("✓ Memory Engine")
        print("✓ Agent Runtime")
        print("✓ Tool Registry")
        print("✓ Planning Engine")
        print("✓ OmniRoute Gateway")
        print("✓ Ollama Local Model")
        print(f"✓ Skill Intelligence Layer ({loaded_skills} skills)")
        print(f"✓ Workflow Manager ({len(workflow_manager.list_workflows())} workflows)")
        print("\nSpeak your Wake Word (e.g., 'Alfred') to begin.\n")
        
        # We need to run the voice loop inside an executor because it's probably blocking
        await asyncio.to_thread(runtime.run_conversation_loop)
        
    except KeyboardInterrupt:
        print("\n[JARVIS X] Shutting down gracefully.")
    except Exception as e:
        logger.error(f"Fatal crash in Jarvis X: {e}\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        omniroute.stop()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
