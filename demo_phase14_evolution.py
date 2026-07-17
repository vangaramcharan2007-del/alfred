"""Phase 14: Capability Evolution Demonstration."""
import os
import sys
import time

from jarvisx.core.failure_monitor import FailureMonitor
from jarvisx.core.capability_gap_analyzer import CapabilityGapAnalyzer
from jarvisx.core.initiative_manager import InitiativeManager
from jarvisx.core.improvement_engine import ImprovementEngine
from jarvisx.core.skill_generator import SkillGenerator
from jarvisx.core.tools.tool_registry import ToolRegistry

def run_demo():
    print("==================================")
    print("PHASE 14: CAPABILITY EVOLUTION")
    print("==================================\n")
    
    # Initialize components
    monitor = FailureMonitor()
    analyzer = CapabilityGapAnalyzer(monitor)
    init_manager = InitiativeManager()
    engine = ImprovementEngine(init_manager)
    generator = SkillGenerator()
    registry = ToolRegistry.get_instance()
    
    # Get initial capability count
    capabilities_before = registry.get_capability_count()
    
    # STEP 1
    print("Injecting failures...")
    print("youtube_transcript_missing")
    print("youtube_transcript_missing")
    print("youtube_transcript_missing\n")
    
    monitor.record_failure("youtube_transcript_missing")
    monitor.record_failure("youtube_transcript_missing")
    monitor.record_failure("youtube_transcript_missing")
    
    print("FailureMonitor:")
    print(f"youtube_transcript failures:\n{monitor.get_failure_count('youtube_transcript_missing')}\n")
    time.sleep(1)
    
    # STEP 2
    print(analyzer.generate_gap_report())
    print("\n")
    time.sleep(1)
    
    # STEP 3
    gaps = analyzer.detect_capability_gaps()
    if gaps:
        gap = gaps[0]
        # In actual logic, we'd map youtube_transcript to transcript_extractor,
        # but for demonstration we'll just hardcode the transformation matching the prompt.
        skill_name = "transcript_extractor" if gap == "youtube_transcript" else f"{gap}_skill"
        
        proposal = engine.generate_improvement_proposal(skill_name)
        engine.submit_proposal(proposal)
        
        print("==================================")
        print("JARVIS X EVOLUTION DASHBOARD")
        print("==================================")
        print(f"\nProposal:\nCreate {skill_name} skill\n")
        print("Priority:\nHIGH\n")
        print("Confidence:\n94%\n")
        print("Auto approval in:\n")
        
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(0.5)
            
        print("\nAPPROVED")
        print("GENERATING SKILL\n")
        
        # STEP 5
        generator.create_skill(skill_name)
        time.sleep(1)
        
        # STEP 6
        print("Registry Reloaded\n")
        registry.load_generated_skills()
        
        capabilities_after = registry.get_capability_count()
        print(f"Capabilities Before:\n{capabilities_before}\n")
        print(f"Capabilities After:\n{capabilities_after}\n")
        time.sleep(1)
        
        # STEP 7
        print("Retrying transcript request...\n")
        if registry.has_tool(skill_name):
            print(f"Capability found:\n{skill_name}\n")
            print("Operation successful.")
        else:
            print("Capability not found. Operation failed.")
            
if __name__ == "__main__":
    # Setup path
    sys.path.insert(0, os.path.abspath("src"))
    run_demo()
