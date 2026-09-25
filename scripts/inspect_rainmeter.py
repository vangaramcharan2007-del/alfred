import os
import pathlib

ini_path = pathlib.Path(r"C:\Users\vanga\AppData\Roaming\Rainmeter\Rainmeter.ini")
if ini_path.exists():
    with open(ini_path, "r", encoding="utf-16le", errors="ignore") as f:
        content = f.read()
    
    sections = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            sections.append(line)
        elif line.startswith("Active="):
            sections.append(f"  {line}")
    print("\n".join(sections))
else:
    print("Rainmeter.ini not found")
