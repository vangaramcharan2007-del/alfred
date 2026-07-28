import pytest
from jarvisx.security.network_security import NetworkSecurityLayer, SignedEnvelope
from jarvisx.network.agent_protocol import Envelope

def test_security_layer():
    sec = NetworkSecurityLayer("secret123")
    
    msg = Envelope(
        message_id="msg_1",
        trace_id="tr1",
        timestamp="100",
        type="test",
        payload={"data": 123}
    )
    
    signed = sec.sign_message(msg)
    
    assert signed.message_id == "msg_1"
    assert signed.signature is not None
    
    # Verify valid
    assert sec.verify_message(signed) is True
    
    # Tamper with payload
    tampered = SignedEnvelope(
        message_id=signed.message_id,
        signature=signed.signature,
        payload={"data": 456}
    )
    assert sec.verify_message(tampered) is False
    
    # Unwrap valid
    unwrapped = sec.reject_invalid_message(signed)
    assert unwrapped is not None
    assert unwrapped.type == "test"
    
    # Unwrap tampered
    assert sec.reject_invalid_message(tampered) is None
