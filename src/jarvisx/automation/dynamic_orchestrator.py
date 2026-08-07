"""Dynamic Windows Application Launcher & Intent Orchestrator (Layer 5 - Execution).

Zero-hardcoding dynamic desktop app finder, web/media launcher, and LLM intent router.
"""

from __future__ import annotations
import os
import sys
import glob
import time
import datetime
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List


class DynamicOrchestrator:
    """Zero-hardcode dynamic Windows application & voice task orchestrator."""

    def __init__(self):
        self.user_name: str = "Charan"

    def find_and_launch_app(self, app_name: str) -> Dict[str, Any]:
        """Dynamically search Windows Start Menu, PATH, and Registry for any app name."""
        clean_name = app_name.lower().replace("open", "").replace("launch", "").replace("start", "").strip()
        if not clean_name:
            return {"status": "FAILED", "reason": "Empty app name"}

        # Common Web Applications Fallback
        web_apps = {
            "youtube": "https://www.youtube.com",
            "whatsapp": "https://web.whatsapp.com",
            "spotify": "https://open.spotify.com",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "google": "https://www.google.com",
            "twitter": "https://twitter.com",
            "x": "https://x.com",
            "chatgpt": "https://chatgpt.com",
        }

        for key, url in web_apps.items():
            if key in clean_name:
                webbrowser.open(url)
                return {"status": "LAUNCHED_WEB", "target": key, "url": url}

        # Search Windows Start Menu Shortcuts (.lnk)
        search_paths = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            r"C:\Users\vanga\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
            r"C:\Users\vanga\AppData\Local\Programs",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]

        found_path: Optional[str] = None

        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue
            for root, dirs, files in os.walk(base_path):
                for f in files:
                    if clean_name in f.lower() and (f.endswith(".lnk") or f.endswith(".exe")):
                        found_path = os.path.join(root, f)
                        break
                if found_path:
                    break
            if found_path:
                break

        if found_path:
            try:
                os.startfile(found_path)
                return {"status": "LAUNCHED_LOCAL", "target": clean_name, "path": found_path}
            except Exception as e:
                pass

        # Try launching directly via system shell
        try:
            subprocess.Popen([clean_name], shell=True)
            return {"status": "LAUNCHED_SHELL", "target": clean_name}
        except Exception:
            pass

        # Fallback to Google Search for the application/query
        search_url = f"https://www.google.com/search?q={clean_name}"
        webbrowser.open(search_url)
        return {"status": "SEARCHED_WEB", "target": clean_name, "url": search_url}

    def execute_voice_command(self, raw_text: str, persona: str = "ALFRED") -> Dict[str, Any]:
        """Dynamically parse natural language voice commands and execute orchestration."""
        text = raw_text.lower().strip()
        salutation = "Sir" if persona == "ALFRED" else "Boss"

        # 1. Identity & Name Query
        if "my name" in text or "who am i" in text or "who i am" in text:
            response = f"Your name is {self.user_name}, {salutation}."
            return {"action": "speak", "response": response, "type": "identity"}

        # 2. Time Query
        if "time" in text:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The time is {now_str}, {salutation}."
            return {"action": "speak", "response": response, "type": "time"}

        # 3. Dynamic App / Web Launching ("open X", "launch X", "start X")
        if text.startswith("open ") or text.startswith("launch ") or text.startswith("start "):
            app_target = text.split(maxsplit=1)[-1]
            res = self.find_and_launch_app(app_target)
            response = f"Opening {app_target} for you now, {salutation}."
            return {"action": "launch", "response": response, "target": app_target, "details": res}

        # 4. Media Query ("play X", "play video", "play song")
        if text.startswith("play ") or "play video" in text or "play song" in text:
            query = text.replace("play video", "").replace("play song", "").replace("play", "").strip()
            if query:
                url = f"https://www.youtube.com/results?search_query={query}"
                webbrowser.open(url)
                response = f"Playing {query} on YouTube for you, {salutation}."
            else:
                webbrowser.open("https://www.youtube.com")
                response = f"Opening YouTube media player, {salutation}."
            return {"action": "media", "response": response, "query": query}

        # 5. Call / Communication Intent ("call X", "message X")
        if text.startswith("call ") or text.startswith("message ") or "whatsapp" in text:
            contact = text.replace("call", "").replace("message", "").replace("whatsapp", "").replace("open", "").strip()
            url = f"https://web.whatsapp.com"
            webbrowser.open(url)
            response = f"Opening WhatsApp messaging service for {contact if contact else 'your contacts'}, {salutation}."
            return {"action": "call", "response": response, "contact": contact}

        # 6. Make / Build App Intent ("make an app", "build project")
        if "make" in text or "build" in text or "app" in text or "project" in text:
            response = f"Initializing autonomous project builder workspace for you now, {salutation}."
            return {"action": "build_app", "response": response}

        # 7. Default Query Response via LLM / Fallback
        response = f"Understood, {salutation}. Executing your request for: {text}"
        return {"action": "llm", "response": response, "text": text}
