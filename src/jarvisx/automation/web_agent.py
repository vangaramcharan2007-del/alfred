"""Jarvis X: Autonomous Web Navigation & Research Agent.

Navigates URLs, extracts clean article/documentation text, and performs web research.
"""

from __future__ import annotations
import os
import sys
import re
import urllib.request
from typing import Dict, Any, List


class WebAgent:
    """Autonomous web researcher and content scraper."""

    def fetch_page_text(self, url: str) -> Dict[str, Any]:
        """Fetches a URL and strips HTML into clean readable text."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # Simple regex HTML stripping
            clean = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r"<style.*?</style>", "", clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r"<.*?>", " ", clean)
            clean = re.sub(r"\s+", " ", clean).strip()

            return {
                "status": "success",
                "url": url,
                "title": url,
                "text": clean[:4000],
                "char_count": len(clean)
            }
        except Exception as e:
            return {"status": "error", "url": url, "error": str(e)}
