r"""
Alfred Vault Query & Retrieval CLI:
Searches through all ingested SRM coursework, textbooks, course notes,
WhatsApp documents, and lecture presentations in F:\Alfred_Vault.
r"""

import sys
import os
from pathlib import Path

VAULT_ROOT = Path("F:/Alfred_Vault")

def search_vault(query: str):
    if not VAULT_ROOT.exists():
        print(f"[!] Vault root {VAULT_ROOT} does not exist or drive F: is disconnected.")
        return

    print("=" * 65)
    print(f"       ALFRED VAULT SEARCH: '{query}'")
    print("=" * 65)

    matches = []
    query_lower = query.lower()

    for root, dirs, files in os.walk(VAULT_ROOT):
        for f in files:
            file_path = Path(root) / f
            rel_path = file_path.relative_to(VAULT_ROOT)
            
            # Match in file name or folder category
            if query_lower in f.lower() or query_lower in str(rel_path).lower():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                matches.append((rel_path, size_mb))

    if not matches:
        print(f"[-] No documents matching '{query}' found in Vault.")
    else:
        print(f"[+] Found {len(matches)} matching document(s):\n")
        for idx, (path, size_mb) in enumerate(matches, 1):
            category = path.parts[0] if len(path.parts) > 1 else "Root"
            filename = path.name
            print(f"  {idx:2d}. [{category}] {filename} ({size_mb:.2f} MB)")
            print(f"      Path: {VAULT_ROOT / path}")

    print("=" * 65)

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not q:
        print("Usage: python scripts/query_vault.py <search query>")
        print("Example: python scripts/query_vault.py OODP")
        print("Example: python scripts/query_vault.py Architecture")
        sys.exit(1)
    search_vault(q)
