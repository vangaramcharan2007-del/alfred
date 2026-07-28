import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.network.agent_protocol import Envelope

@dataclass
class SignedEnvelope:
    message_id: str
    signature: str
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
        
    @staticmethod
    def from_json(data: str) -> "SignedEnvelope":
        parsed = json.loads(data)
        return SignedEnvelope(**parsed)


class NetworkSecurityLayer:
    """
    Handles payload verification and integrity checking for distributed nodes.
    Designed to be extensible for future TLS and zero-trust mechanisms.
    """
    def __init__(self, secret_key: str, logger: Optional[StructuredLogger] = None):
        self.secret_key = secret_key
        self.logger = logger or StructuredLogger()

    def _generate_hash(self, payload: Dict[str, Any]) -> str:
        """Generates a SHA-256 HMAC-style hash without external crypto libs."""
        payload_str = json.dumps(payload, sort_keys=True)
        raw = f"{self.secret_key}:{payload_str}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def sign_message(self, envelope: Envelope) -> SignedEnvelope:
        """Sign a standard envelope, converting it to a SignedEnvelope."""
        payload = asdict(envelope)
        signature = self._generate_hash(payload)
        return SignedEnvelope(
            message_id=envelope.message_id,
            signature=signature,
            payload=payload
        )

    def verify_message(self, signed_envelope: SignedEnvelope) -> bool:
        """Verify the integrity of a SignedEnvelope."""
        expected_signature = self._generate_hash(signed_envelope.payload)
        is_valid = expected_signature == signed_envelope.signature
        if not is_valid:
            self.logger.write("warning", "security.verification_failed", message_id=signed_envelope.message_id)
        return is_valid

    def reject_invalid_message(self, signed_envelope: SignedEnvelope) -> Optional[Envelope]:
        """
        Verifies and unwraps the payload.
        Returns the original Envelope if valid, None if invalid.
        """
        if self.verify_message(signed_envelope):
            return Envelope(**signed_envelope.payload)
        return None
