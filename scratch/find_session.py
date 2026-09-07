import os
import glob
import re

leveldb_dir = r"C:\Users\vanga\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Local Storage\leveldb"
files = glob.glob(os.path.join(leveldb_dir, "*.ldb")) + glob.glob(os.path.join(leveldb_dir, "*.log"))

print(f"Scanning {len(files)} LevelDB files in {leveldb_dir}...")

found_files = []
for f in files:
    try:
        with open(f, "rb") as fp:
            data = fp.read()
            if b"dld.srmist.edu.in" in data or b"ktretecurricula" in data:
                found_files.append((f, data))
                print(f"Found eCurricula references in: {os.path.basename(f)} ({len(data)} bytes)")
    except Exception as e:
        print("Error reading:", f, e)

# Extract key-value pairs
pattern = re.compile(rb'([a-zA-Z0-9_\-]{4,50})\x00\x01([^\x00\x01\x02]{5,500})')
tokens = []

for f, data in found_files:
    # Look for JWT tokens (starts with eyJ)
    jwt_pattern = re.compile(rb'eyJ[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}')
    for m in jwt_pattern.finditer(data):
        tokens.append(m.group(0).decode('latin1'))

print(f"Found {len(tokens)} JWT tokens:")
for t in set(tokens):
    print("  JWT:", t[:50] + "..." + t[-20:])
