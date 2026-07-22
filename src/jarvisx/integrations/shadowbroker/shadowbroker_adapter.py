import os
import time
import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional
import asyncio

class ShadowBrokerError(Exception):
    pass

class ShadowBrokerTimeout(ShadowBrokerError):
    pass

def _load_sb_client_class():
    """Dynamically load the ShadowBrokerClient from the cloned submodule."""
    # current file: src/jarvisx/integrations/shadowbroker/shadowbroker_adapter.py
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    sb_query_path = project_root / "modules" / "ShadowBroker" / "openclaw-skills" / "shadowbroker" / "sb_query.py"
    
    if not sb_query_path.exists():
        raise RuntimeError(f"ShadowBrokerClient not found at {sb_query_path}")
        
    spec = importlib.util.spec_from_file_location("sb_query", str(sb_query_path))
    if spec is None or spec.loader is None:
        raise ImportError("Failed to load sb_query spec")
        
    sb_query = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sb_query)
    return sb_query.ShadowBrokerClient


class ShadowBrokerAdapter:
    """
    Adapter for ShadowBroker capability.
    Wraps the official ShadowBrokerClient to provide connection validation,
    timeout handling, and graceful degradation. Exposes only the fast-path capabilities.
    """
    def __init__(self, base_url: Optional[str] = None, hmac_secret: Optional[str] = None, timeout_sec: int = 15):
        self.base_url = base_url or os.environ.get("SHADOWBROKER_URL", "http://127.0.0.1:8000")
        self.hmac_secret = hmac_secret or os.environ.get("SHADOWBROKER_HMAC_SECRET", "")
        self.timeout_sec = timeout_sec
        self._client_class = _load_sb_client_class()
        # The underlying client initializes its httpx/requests sessions
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = self._client_class(base_url=self.base_url, hmac_secret=self.hmac_secret)
            # Try to inject timeout if possible, though sb_query hardcodes httpx timeout to 15.
            if hasattr(self._client, "_client") and self._client._client is not None:
                self._client._client.timeout = self.timeout_sec
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.close()

    async def health_check(self) -> Dict[str, Any]:
        """
        Verify connection and HMCA authentication using the lightweight channel_status.
        """
        try:
            client = self._get_client()
            return await asyncio.wait_for(client.channel_status(), timeout=self.timeout_sec)
        except asyncio.TimeoutError:
            raise ShadowBrokerTimeout("ShadowBroker health check timed out.")
        except Exception as e:
            raise ShadowBrokerError(f"ShadowBroker health check failed: {str(e)}")

    async def ask(self, question: str, lat: Optional[float] = None, lng: Optional[float] = None, radius_km: float = 50) -> Dict[str, Any]:
        """
        Fast-path natural language query routing + execution.
        """
        try:
            client = self._get_client()
            return await asyncio.wait_for(
                client.ask(question, lat=lat, lng=lng, radius_km=radius_km),
                timeout=self.timeout_sec
            )
        except asyncio.TimeoutError:
            raise ShadowBrokerTimeout("ShadowBroker 'ask' timed out.")
        except Exception as e:
            raise ShadowBrokerError(f"ShadowBroker 'ask' failed: {str(e)}")

    async def run_playbook(self, name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a predefined server-side snapshot playbook (e.g., 'hot_snapshot').
        """
        try:
            client = self._get_client()
            return await asyncio.wait_for(
                client.run_playbook(name, args),
                timeout=self.timeout_sec
            )
        except asyncio.TimeoutError:
            raise ShadowBrokerTimeout("ShadowBroker 'run_playbook' timed out.")
        except Exception as e:
            raise ShadowBrokerError(f"ShadowBroker 'run_playbook' failed: {str(e)}")
