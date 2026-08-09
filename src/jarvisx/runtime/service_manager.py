"""Windows Service & Startup Automation Manager for Phase 104.5."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict


class WindowsServiceManager:
    """Generates startup registration scripts for Windows Task Scheduler and startup folder."""

    def __init__(self, scripts_dir: str = "var/scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

    def generate_startup_artifacts(self) -> Dict[str, Any]:
        """Generate Windows batch and PowerShell background service launcher scripts."""
        python_exe = sys.executable
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        main_py = root_dir / "src" / "jarvisx" / "main.py"

        bat_file = self.scripts_dir / "jarvis_startup.bat"
        bat_content = f"""@echo off
title Jarvis X Background Daemon
cd /d "{root_dir}"
"{python_exe}" -m jarvisx daemon start --background
"""
        bat_file.write_text(bat_content, encoding="utf-8")

        ps1_file = self.scripts_dir / "jarvis_startup.ps1"
        ps1_content = f"""# Jarvis X Background Startup Script
$RootDir = "{root_dir}"
Set-Location -Path $RootDir
Start-Process -FilePath "{python_exe}" -ArgumentList "-m jarvisx daemon start" -WindowStyle Hidden
"""
        ps1_file.write_text(ps1_content, encoding="utf-8")

        task_xml_file = self.scripts_dir / "jarvis_task_scheduler.xml"
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Jarvis X Sovereign Background Daemon</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>-m jarvisx daemon start</Arguments>
      <WorkingDirectory>{root_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
        task_xml_file.write_text(task_xml, encoding="utf-8")

        return {
            "status": "SUCCESS",
            "bat_script": str(bat_file),
            "ps1_script": str(ps1_file),
            "task_scheduler_xml": str(task_xml_file),
            "instructions": (
                f"1. To run on boot, copy '{bat_file.name}' to 'shell:startup'.\n"
                f"2. Or import '{task_xml_file.name}' into Windows Task Scheduler (taskschd.msc)."
            ),
        }
