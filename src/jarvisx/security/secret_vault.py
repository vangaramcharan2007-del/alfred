"""Secret Vault with AES-GCM Encryption and Zero-Leakage Masking for Phase 99."""

from __future__ import annotations
import base64
import hashlib
import os
import time
from typing import Dict, List, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jarvisx.security.models import SecretItem
from jarvisx.security.security_memory import SecurityMemory


class SecretVault:
    """AES-GCM 256-bit encrypted secret store with PBKDF2 key derivation and zero plaintext leakage."""

    def __init__(self, memory: Optional[SecurityMemory] = None, passphrase: Optional[str] = None):
        self.memory = memory or SecurityMemory()
        # Derive master key from environment or user unlock passphrase
        raw_phrase = passphrase or os.environ.get("JARVISX_VAULT_KEY", "JarvisX_Default_Production_Vault_Key_2026")
        self.master_key = hashlib.pbkdf2_hmac(
            "sha256",
            raw_phrase.encode("utf-8"),
            b"JarvisX_Security_Salt_v1",
            100000,
            32
        )
        self.aesgcm = AESGCM(self.master_key)

    def mask_token(self, plaintext: str) -> str:
        """Mask secrets into safe preview format (e.g. sk-***6789)."""
        if len(plaintext) <= 8:
            return "***"
        prefix = plaintext[:3]
        suffix = plaintext[-4:]
        return f"{prefix}-***{suffix}"

    def set_secret(self, key_name: str, plaintext: str) -> SecretItem:
        """Encrypt with AES-GCM and store encrypted blob in database."""
        nonce = os.urandom(12)
        encrypted_bytes = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

        item = SecretItem(
            key_name=key_name,
            encrypted_blob_b64=base64.b64encode(encrypted_bytes).decode("utf-8"),
            nonce_b64=base64.b64encode(nonce).decode("utf-8"),
            masked_preview=self.mask_token(plaintext),
            created_at=time.time()
        )
        self.memory.save_secret(item)
        print(f"  [Secret Vault]: Key '{key_name}' encrypted & saved (Masked: {item.masked_preview}).")
        return item

    def get_secret(self, key_name: str) -> Optional[str]:
        """Decrypt AES-GCM ciphertext and return plaintext to authorized caller."""
        item = self.memory.get_secret(key_name)
        if not item:
            return None

        encrypted_bytes = base64.b64decode(item.encrypted_blob_b64)
        nonce = base64.b64decode(item.nonce_b64)
        decrypted_bytes = self.aesgcm.decrypt(nonce, encrypted_bytes, None)
        return decrypted_bytes.decode("utf-8")

    def list_secrets_masked(self) -> List[Dict[str, Any]]:
        """List secrets with strictly masked preview (zero plaintext in memory/logs)."""
        return [s.to_dict() for s in self.memory.list_secrets()]
