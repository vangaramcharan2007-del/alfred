"""Local encryption helpers for sensitive AEGIS records.

The key remains on the user's device and is never sent to the API client or a
remote service. Deployments may instead supply ``AEGIS_DATA_KEY`` (a Fernet
key) through their secret manager.
"""

import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


class LocalDataProtector:
    """Encrypt selected SQLite text columns while keeping local analytics usable."""

    _PREFIX = "enc:v1:"

    def __init__(self, database_path: str) -> None:
        key = os.getenv("AEGIS_DATA_KEY")
        self.key_path = Path(f"{database_path}.key")
        if not key:
            if self.key_path.exists():
                key = self.key_path.read_text(encoding="utf-8").strip()
            else:
                key = Fernet.generate_key().decode("ascii")
                self.key_path.write_text(key, encoding="utf-8")
                try:
                    os.chmod(self.key_path, 0o600)
                except OSError:
                    # Windows ACLs are managed by the account that owns the file.
                    pass
        self._fernet = Fernet(key.encode("ascii"))

    def encrypt(self, value: Optional[str]) -> Optional[str]:
        if value is None or value.startswith(self._PREFIX):
            return value
        token = self._fernet.encrypt(value.encode("utf-8")).decode("ascii")
        return f"{self._PREFIX}{token}"

    def decrypt(self, value: Optional[str]) -> Optional[str]:
        if value is None or not value.startswith(self._PREFIX):
            # Legacy rows remain readable and are migrated at AegisMemory startup.
            return value
        try:
            return self._fernet.decrypt(value[len(self._PREFIX):].encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt AEGIS data: use the original AEGIS_DATA_KEY.") from exc
