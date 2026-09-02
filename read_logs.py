import json
from pathlib import Path

transcript = Path(r'C:\Users\vanga\.gemini\antigravity\brain\5f3536a0-db67-45f8-b6ac-bcc96c90cbbf\.system_generated\logs\transcript_full.jsonl')
lines = transcript.read_text(encoding='utf-8').splitlines()

for line in lines:
    obj = json.loads(line)
    if obj.get('sender') in ['ba54adba-d2b9-4801-8666-69d144bd2c27', '6d4f42a6-d144-48e2-8118-3baae7468661', '298c0296-813c-46f2-867c-97b890f471dc', 'dc4e1e10-63bf-409e-8136-7c8dd6e7dacf', '5892fa33-bc40-497b-a3fb-987867340407']:
        print(f'\n--- From {obj.get("sender")} ---')
        print(obj.get('content', '')[:1000])
