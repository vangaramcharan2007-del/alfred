from typing import Any
import pandas as pd
import re
import os
from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.core.health import HealthStatus

class DataProcessingTool(BaseTool):
    name = "data_processing"
    
    def parse_tabular_text_to_excel(self, text_data: str, output_dir: str = "scratch") -> ToolResult:
        """Parses raw text separated by 'File X:' into multiple Excel files."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            sections = text_data.split('\n\n')
            created_files = []
            
            for section in sections:
                lines = section.strip().split('\n')
                if len(lines) < 3: continue
                
                # Check if it looks like one of the files
                if not any(k in lines[0] for k in ["File", "Refined", "Data"]):
                    continue
                    
                title = lines[0].replace('File 1:', '').replace('File 2:', '').replace('File 3:', '').replace(':', '').replace('.pdf', '').strip()
                
                records = []
                for line in lines[2:]:
                    parts = re.split(r'\s{2,}|\t', line.strip())
                    if len(parts) >= 3:
                        records.append({
                            "Name": parts[0],
                            "Date of Birth": parts[1],
                            "Date of Joining": parts[2]
                        })
                
                if records:
                    df = pd.DataFrame(records)
                    clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    if not clean_title:
                        clean_title = f"dataset_{len(created_files)}"
                    filename = os.path.join(output_dir, f"{clean_title.replace(' ', '_')}.xlsx")
                    df.to_excel(filename, index=False)
                    created_files.append(os.path.abspath(filename))
                    
            if not created_files:
                return ToolResult(success=False, message="No tabular data recognized to parse.")
                
            return ToolResult(success=True, message=f"Generated {len(created_files)} files.", data={"files": created_files})
        except Exception as e:
            return ToolResult(success=False, message=f"Data processing failed: {str(e)}")
