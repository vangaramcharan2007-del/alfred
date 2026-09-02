"""
Security Hardening Module — Encryption, Auth, and Input Sanitization for Jarvis X.
"""

import os
import json
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from base64 import b64encode, b64decode

logger = logging.getLogger(__name__)


class SecureVault:
    """Encrypted secret storage using Fernet symmetric encryption."""

    def __init__(self, vault_path: str = None):
        self._vault_path = Path(vault_path or os.path.join("var", "db", "secure_vault.enc"))
        self._vault_path.parent.mkdir(parents=True, exist_ok=True)
        self._key_path = Path(os.path.join("var", "db", ".vault_key"))
        self._key = self._load_or_create_key()
        self._secrets: Dict[str, str] = self._load_vault()

    def _load_or_create_key(self) -> bytes:
        if self._key_path.exists():
            return self._key_path.read_bytes()
        try:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
        except ImportError:
            key = secrets.token_bytes(32)
        self._key_path.write_bytes(key)
        return key

    def _encrypt(self, plaintext: str) -> str:
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key)
            return f.encrypt(plaintext.encode()).decode()
        except ImportError:
            # Fallback: base64 + XOR (not secure, but functional)
            xor_key = hashlib.sha256(self._key).digest()
            encrypted = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(plaintext.encode()))
            return b64encode(encrypted).decode()

    def _decrypt(self, ciphertext: str) -> str:
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key)
            return f.decrypt(ciphertext.encode()).decode()
        except ImportError:
            xor_key = hashlib.sha256(self._key).digest()
            encrypted = b64decode(ciphertext)
            decrypted = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(encrypted))
            return decrypted.decode()

    def _load_vault(self) -> Dict[str, str]:
        if self._vault_path.exists():
            try:
                data = json.loads(self._vault_path.read_text(encoding="utf-8"))
                return {k: self._decrypt(v) for k, v in data.items()}
            except Exception:
                return {}
        return {}

    def _save_vault(self):
        encrypted = {k: self._encrypt(v) for k, v in self._secrets.items()}
        self._vault_path.write_text(json.dumps(encrypted, indent=2), encoding="utf-8")

    def set_secret(self, key: str, value: str):
        self._secrets[key] = value
        self._save_vault()

    def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)

    def list_keys(self):
        return list(self._secrets.keys())

    def delete_secret(self, key: str):
        if key in self._secrets:
            del self._secrets[key]
            self._save_vault()


class HUDAuth:
    """Simple token-based auth for the HUD dashboard."""

    def __init__(self):
        self._token_path = Path("var/db/.hud_token")
        self._token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token = self._load_or_create_token()

    def _load_or_create_token(self) -> str:
        if self._token_path.exists():
            return self._token_path.read_text(encoding="utf-8").strip()
        token = secrets.token_urlsafe(32)
        self._token_path.write_text(token, encoding="utf-8")
        logger.info(f"[HUDAuth] New token generated. Access: http://localhost:8765?token={token}")
        return token

    def validate(self, provided_token: str) -> bool:
        return secrets.compare_digest(self.token, provided_token)


class InputSanitizer:
    """Sanitize user inputs to prevent injection attacks."""

    BLOCKED_PATTERNS = [
        "rm -rf", "format c:", "del /f", "DROP TABLE", "DELETE FROM",
        "; rm", "& del", "| rm", "`rm", "$(rm", "__import__",
        "os.system", "subprocess", "eval(", "exec(",
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Remove dangerous patterns from user input."""
        cleaned = text
        for pattern in cls.BLOCKED_PATTERNS:
            if pattern.lower() in cleaned.lower():
                cleaned = cleaned.replace(pattern, "[BLOCKED]")
                logger.warning(f"[Sanitizer] Blocked dangerous input: '{pattern}'")
        return cleaned

    @classmethod
    def is_safe(cls, text: str) -> bool:
        for pattern in cls.BLOCKED_PATTERNS:
            if pattern.lower() in text.lower():
                return False
        return True
