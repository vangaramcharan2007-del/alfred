import base64
import json
from pathlib import Path

pdf_dir = Path("outputs/srm_unit1_fixed/pdfs")
files_data = []

for pdf_file in sorted(pdf_dir.glob("*.pdf")):
    b64 = base64.b64encode(pdf_file.read_bytes()).decode("utf-8")
    files_data.append({
        "name": pdf_file.name,
        "b64": b64
    })

print(f"Encoded {len(files_data)} files into base64.")

# Save as json
with open("scratch/files_b64.json", "w", encoding="utf-8") as f:
    json.dump(files_data, f)

print("Saved scratch/files_b64.json")
