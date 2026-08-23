"""
Semantic UI Element Finder for Windows Desktop Applications.
Adapted from windows_use patterns to locate clickable and editable elements by text and role.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jarvisx.computer_use.windows_ui import UIElement, WindowsUIAutomationInspector


class SemanticElementFinder:
    """Finds interactive desktop UI elements by text, accessibility name, or role."""

    def __init__(self, inspector: Optional[WindowsUIAutomationInspector] = None):
        self.inspector = inspector or WindowsUIAutomationInspector()

    def find_elements_in_window(self, window_title_query: str) -> List[UIElement]:
        """Inspects and returns all interactive elements in the target window."""
        ps_script = f"""
        Add-Type -AssemblyName UIAutomationClient
        Add-Type -AssemblyName UIAutomationTypes
        
        $p = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{window_title_query}*' }} | Select-Object -First 1
        if (-not $p) {{ return "[]" }}
        
        $root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
        if (-not $root) {{ return "[]" }}
        
        $condition = [System.Windows.Automation.Condition]::TrueCondition
        $elements = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
        
        $res = @()
        foreach ($el in $elements) {{
            try {{
                $name = $el.Current.Name
                $ctrl = $el.Current.ControlType.ProgrammaticName.Replace("ControlType.", "")
                $rect = $el.Current.BoundingRectangle
                if ($name -and $rect.Width -gt 5 -and $rect.Height -gt 5) {{
                    $res += @{{
                        name = $name
                        control_type = $ctrl
                        is_enabled = $el.Current.IsEnabled
                        left = [int]$rect.Left
                        top = [int]$rect.Top
                        width = [int]$rect.Width
                        height = [int]$rect.Height
                    }}
                }}
            }} catch {{}}
        }}
        $res | ConvertTo-Json -Compress
        """

        try:
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=5.0)
            if proc.returncode == 0 and proc.stdout.strip():
                raw = json.loads(proc.stdout.strip())
                if isinstance(raw, dict):
                    raw = [raw]
                return [
                    UIElement(
                        name=item.get("name", "Unknown"),
                        control_type=item.get("control_type", "Custom"),
                        rect={
                            "left": item.get("left", 0),
                            "top": item.get("top", 0),
                            "right": item.get("left", 0) + item.get("width", 0),
                            "bottom": item.get("top", 0) + item.get("height", 0),
                            "width": item.get("width", 0),
                            "height": item.get("height", 0),
                        },
                        is_enabled=item.get("is_enabled", True),
                        window_title=window_title_query,
                    )
                    for item in raw
                ]
        except Exception:
            pass

        return []

    def locate_target_element(self, window_title: str, text_query: str) -> Optional[UIElement]:
        """Finds the most specific element matching the text query in the window."""
        elements = self.find_elements_in_window(window_title)
        query_lower = text_query.lower().strip()

        # 1. Exact match
        for el in elements:
            if el.name.lower() == query_lower:
                return el

        # 2. Substring match
        for el in elements:
            if query_lower in el.name.lower():
                return el

        return None
