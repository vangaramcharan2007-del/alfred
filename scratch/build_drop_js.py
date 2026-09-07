import json

with open("scratch/files_b64.json", encoding="utf-8") as f:
    files_data = json.load(f)

# Build a JS snippet that creates ALL 16 files and drops them at once!
files_js_array = []
for item in files_data:
    files_js_array.append(f'{{ name: "{item["name"]}", b64: "{item["b64"]}" }}')

all_files_js = ",\n".join(files_js_array)

js_code = f"""() => {{
    const filesData = [
{all_files_js}
    ];
    
    const dt = new DataTransfer();
    
    for (const item of filesData) {{
        const binary = atob(item.b64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {{
            bytes[i] = binary.charCodeAt(i);
        }}
        const blob = new Blob([bytes], {{ type: 'application/pdf' }});
        const file = new File([blob], item.name, {{ type: 'application/pdf' }});
        dt.items.add(file);
    }}
    
    const dropZone = document.querySelector('[role="main"]') || document.body;
    
    const enterEvt = new DragEvent('dragenter', {{ dataTransfer: dt, bubbles: true, cancelable: true }});
    const overEvt = new DragEvent('dragover', {{ dataTransfer: dt, bubbles: true, cancelable: true }});
    const dropEvt = new DragEvent('drop', {{ dataTransfer: dt, bubbles: true, cancelable: true }});
    
    dropZone.dispatchEvent(enterEvt);
    dropZone.dispatchEvent(overEvt);
    dropZone.dispatchEvent(dropEvt);
    
    return 'Dispatched drop event with ' + dt.files.length + ' files on ' + dropZone.tagName;
}}"""

with open("scratch/drop_all_files.js", "w", encoding="utf-8") as f:
    f.write(js_code)

print("Generated scratch/drop_all_files.js successfully.")
