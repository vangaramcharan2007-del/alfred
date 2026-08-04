import pytest
from jarvisx.capabilities.core.capability_discovery import CapabilityDiscoverySystem

def test_capability_selection():
    discovery = CapabilityDiscoverySystem()
    
    # Test PDF query capability selection
    match_pdf = discovery.discover_best_capability("Read PDF document and extract table data")
    assert match_pdf.capability_id in ("tool.ocr_vision", "tool.file_system")
    
    # Test Python execution query capability selection
    match_py = discovery.discover_best_capability("Execute python script and run pytest")
    assert match_py.capability_id == "tool.python_executor"
    
    # Test Academic capability selection
    match_acad = discovery.discover_best_capability("Prepare Operating Systems revision plan for 10 CGPA")
    assert match_acad.capability_id == "tool.academic_engine"
