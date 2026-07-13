import json
import os
import urllib.request
import urllib.error
from typing import Any, Optional


class SupabaseClient:
    """Minimal, dependency-free client for Supabase REST API."""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = key or os.environ.get("SUPABASE_KEY")
        
        # Remove trailing slash if present
        if self.url and self.url.endswith("/"):
            self.url = self.url[:-1]

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    def _request(self, method: str, path: str, payload: Optional[dict[str, Any]] = None) -> tuple[int, Any]:
        if not self.is_configured:
            return 0, {"error": "Supabase credentials not configured."}
            
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            
        url = f"{self.url}/rest/v1/{path}"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8")
                return e.code, json.loads(body) if body else {}
            except Exception:
                return e.code, {"error": str(e)}
        except Exception as e:
            return 0, {"error": str(e)}

    def insert(self, table: str, record: dict[str, Any]) -> tuple[bool, Any]:
        status, data = self._request("POST", table, record)
        return 200 <= status < 300, data

    def select(self, table: str, query: str = "select=*") -> tuple[bool, Any]:
        status, data = self._request("GET", f"{table}?{query}")
        return 200 <= status < 300, data

    def ping(self) -> bool:
        # A lightweight way to check if Supabase is reachable and credentials are valid
        success, _ = self.select("jarvis_health_check", "limit=1")
        return success
