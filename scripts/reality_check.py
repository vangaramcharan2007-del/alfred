#!/usr/bin/env python3
"""
Jarvis X Production Reality Check Script
"""
import os
import sys
from pathlib import Path

# Ensure src directory is on sys.path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from jarvisx.diagnostics.capability_checker import CapabilityChecker
from jarvisx.diagnostics.system_health_report import SystemHealthReporter

def main():
    print("\nRunning Jarvis X Production Reality Check...\n")
    checker = CapabilityChecker()
    caps = checker.get_system_capabilities()
    reporter = SystemHealthReporter(checker=checker)

    banner = reporter.generate_startup_banner()
    print(banner)

    print("Integrations Status:")
    for k, v in caps["integrations"].items():
        print(f"  - {k:<12}: {v}")

    print("\nDependency Check:")
    print("  Packages:")
    for k, v in caps["dependencies"]["packages"].items():
        print(f"    - {k:<12}: {'INSTALLED' if v else 'MISSING'}")
    print("  Binaries:")
    for k, v in caps["dependencies"]["binaries"].items():
        print(f"    - {k:<12}: {'ON PATH' if v else 'MISSING'}")

    print(f"\nOverall System Health: {caps['system_health']}")
    print(f"Online Subsystems: {caps['online_subsystems']} / {caps['total_subsystems']}\n")

if __name__ == "__main__":
    main()
