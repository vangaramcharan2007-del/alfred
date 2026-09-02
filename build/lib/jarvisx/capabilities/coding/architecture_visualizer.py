from __future__ import annotations
import re
from typing import Dict, Any, List
from jarvisx.capabilities.coding.architecture_models import SystemArchitecture

class ArchitectureVisualizer:
    def _sanitize(self, text: str) -> str:
        # Keep alphanumeric and simple underscores for Mermaid node IDs
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        return cleaned if cleaned else "node"

    def generate_component_diagram(self, system_arch: SystemArchitecture) -> str:
        lines = ["```mermaid", "graph TD"]
        lines.append(f"    subgraph System [\"{system_arch.project_name} Architecture\"]")

        for comp in system_arch.components:
            comp_id = self._sanitize(comp.name)
            lines.append(f"        {comp_id}[\"{comp.name}<br/>({comp.responsibility})\"]")

        lines.append("    end")

        for comp in system_arch.components:
            comp_id = self._sanitize(comp.name)
            for dep in comp.dependencies:
                dep_id = self._sanitize(dep)
                lines.append(f"    {comp_id} --> {dep_id}")

        lines.append("```")
        return "\n".join(lines)

    def generate_data_flow_diagram(self, system_arch: SystemArchitecture) -> str:
        lines = ["```mermaid", "sequenceDiagram", f"    autonumber"]
        
        for step in system_arch.data_flow:
            if " -> " in step:
                parts = step.split(" -> ")
                if len(parts) >= 2:
                    src = self._sanitize(parts[0].strip())
                    target = self._sanitize(parts[1].strip())
                    label = " -> ".join(parts[2:]).strip() if len(parts) > 2 else "Data Payload"
                    lines.append(f"    {src}->>{target}: {label}")
            else:
                lines.append(f"    Note over System: {step}")

        lines.append("```")
        return "\n".join(lines)

    def generate_dependency_diagram(self, system_arch: SystemArchitecture) -> str:
        lines = ["```mermaid", "flowchart LR"]
        lines.append("    subgraph TechStack [\"Technology Stack Dependencies\"]")
        
        for layer, tech in system_arch.technology_stack.items():
            layer_id = self._sanitize(layer)
            tech_id = self._sanitize(tech)
            lines.append(f"        {layer_id}[\"{layer.upper()}\"] --> {tech_id}[\"{tech}\"]")

        lines.append("    end")
        lines.append("```")
        return "\n".join(lines)
