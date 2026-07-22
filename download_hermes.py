import urllib.request
import zipfile
import io
import os
import shutil

print("Downloading...")
url = "https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
response = urllib.request.urlopen(url)
data = response.read()

print("Extracting...")
with zipfile.ZipFile(io.BytesIO(data)) as z:
    z.extractall("modules/")
    
if os.path.exists("modules/HermesAgent"):
    shutil.rmtree("modules/HermesAgent")

os.rename("modules/hermes-agent-main", "modules/HermesAgent")
print("Done.")
