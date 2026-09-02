from __future__ import annotations
import packaging.version

class CapabilityVersion:
    @staticmethod
    def is_compatible(current_version: str, required_version: str) -> bool:
        try:
            curr = packaging.version.parse(current_version)
            req = packaging.version.parse(required_version)
            return curr >= req
        except Exception:
            return current_version == required_version
