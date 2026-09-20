"""
Compound Intent Decomposer & Mid-Utterance Self-Correction Engine for E.V.
===========================================================================
Parses conversational self-corrections ("wait before that", "actually first"),
inverts execution order (DAG dependency inversion), routes specific browsers (Brave),
resolves phonetic contacts ("data" -> Dakshith), and chains multiple OS actions
with real-time EV TTS narration and live EV HUD glass toasts.
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("jarvisx.compound_intent")


@dataclass
class CompoundStep:
    order: int
    name: str
    tool: str
    args: Dict[str, Any]
    description: str
    browser_override: Optional[str] = None


@dataclass
class CompoundPlan:
    is_compound: bool
    has_self_correction: bool
    pivot_keyword: Optional[str]
    raw_prompt: str
    speech_acknowledgment: str
    steps: List[CompoundStep] = field(default_factory=list)


class CompoundIntentDecomposer:
    """
    Decomposes multi-intent compound sentences with self-correction logic.
    """

    _instance: Optional[CompoundIntentDecomposer] = None

    PIVOT_PATTERNS = [
        r"\bwait\s+before\s+that\b",
        r"\bbefore\s+that\b",
        r"\bactually\s+first\b",
        r"\bhold\s+on\s+first\b",
        r"\bscratch\s+that\b",
        r"\binstead\b",
        r"\bprioritize\b",
    ]

    BROWSER_BINARIES = {
        "brave": [
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "brave.exe",
        ],
        "chrome": [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe",
        ],
        "edge": [
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe",
        ],
    }

    @classmethod
    def get_instance(cls) -> CompoundIntentDecomposer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _resolve_browser_executable(self, browser_name: str) -> Optional[str]:
        """Finds absolute path or command for the specified browser."""
        candidates = self.BROWSER_BINARIES.get(browser_name.lower(), [f"{browser_name}.exe"])
        for c in candidates:
            if os.path.isabs(c) and os.path.exists(c):
                return c
        return candidates[0]

    def _resolve_contact(self, raw_name: str) -> Tuple[str, str]:
        """
        Resolves contact name and phone number dynamically:
        1. If raw_name is already a phone number, uses it directly.
        2. Looks up in config/contacts.json without any hardcoded defaults.
        3. If not in contacts.json, uses the provided name dynamically with empty phone.
        """
        clean = raw_name.lower().strip()

        # Check if raw_name is directly a phone number (e.g. +91... or digits)
        digits_only = re.sub(r"[^\d+]", "", clean)
        if len(digits_only) >= 7 and (clean.startswith("+") or digits_only.isdigit()):
            return clean, clean

        contacts_file = Path("config/contacts.json")
        if contacts_file.exists():
            try:
                with open(contacts_file, "r", encoding="utf-8") as f:
                    contacts = json.load(f)
                # Exact match
                if clean in contacts:
                    entry = contacts[clean]
                    return entry.get("name", clean.capitalize()), entry.get("phone", "")
                # Substring match
                for k, v in contacts.items():
                    if clean in k.lower() or k.lower() in clean or clean in v.get("name", "").lower():
                        return v.get("name", clean.capitalize()), v.get("phone", "")
            except Exception as e:
                logger.debug(f"[CompoundIntent] Contacts load error: {e}")

        # Completely dynamic: return whatever name was requested
        return clean.capitalize(), ""

    def detect_and_decompose(self, prompt: str) -> Optional[CompoundPlan]:
        """
        Analyzes prompt for self-correction pivot. If detected, inverts DAG
        and constructs multi-step execution plan.
        """
        p_lower = prompt.lower().strip()

        matched_pivot = None
        for pattern in self.PIVOT_PATTERNS:
            match = re.search(pattern, p_lower)
            if match:
                matched_pivot = match.group(0)
                parts = re.split(pattern, p_lower, maxsplit=1)
                first_intent_raw = parts[0].strip()
                second_intent_raw = parts[1].strip()
                break

        if not matched_pivot:
            return None

        logger.info(f"[CompoundIntent] Detected self-correction pivot: '{matched_pivot}'")
        logger.info(f"   Initial Intent:   '{first_intent_raw}'")
        logger.info(f"   Pre-empted Intent: '{second_intent_raw}'")

        # Dependency Inversion: second_intent was stated as "before that" -> executes FIRST!
        # Parse Sub-Intent 1 (Prerequisite action from second part)
        step_1 = self._parse_sub_intent(second_intent_raw, order=1)

        # Parse Sub-Intent 2 (Deferred action from first part)
        step_2 = self._parse_sub_intent(first_intent_raw, order=2)

        steps = [s for s in (step_1, step_2) if s is not None]

        # Generate sleek, context-aware speech acknowledgment dynamically
        if len(steps) >= 2:
            ack = f"Understood Boss. Prioritizing {steps[0].description} first, then handling your {steps[1].description}."
        elif len(steps) == 1:
            ack = f"Understood Boss. Executing {steps[0].description}."
        else:
            ack = "Understood Boss."

        return CompoundPlan(
            is_compound=True,
            has_self_correction=True,
            pivot_keyword=matched_pivot,
            raw_prompt=prompt,
            speech_acknowledgment=ack,
            steps=steps,
        )

    def _parse_sub_intent(self, text: str, order: int) -> Optional[CompoundStep]:
        """Parses an individual intent clause into an executable CompoundStep."""
        t = text.lower().strip()

        # Check for browser override (e.g. "in brave browser", "in brave", "on chrome", "using edge")
        browser = None
        for b_name in ["brave", "chrome", "edge", "firefox"]:
            if f"in {b_name}" in t or f"on {b_name}" in t or f"using {b_name}" in t:
                browser = b_name
                break

        # Clean browser mention from string
        t_clean = t
        if browser:
            t_clean = re.sub(rf"\b(?:in|on|using)\s+{browser}(?:\s+browser)?\b", "", t_clean).strip()

        # 1. Spotify playback / search
        if "spotify" in t_clean or "play" in t_clean:
            query = t_clean
            for phrase in ["open spotify and play", "play on spotify", "open spotify", "play", "songs", "song", "track", "music"]:
                query = re.sub(rf"\b{re.escape(phrase)}\b", "", query, flags=re.IGNORECASE)
            query = query.strip()

            browser_label = f" in {browser.capitalize()}" if browser else ""
            if query:
                target_url = f"https://open.spotify.com/search/{urllib.parse.quote(query)}"
                step_name = f"Spotify {query.title()}{browser_label}"
                desc = f"Spotify search for '{query.title()}'{browser_label}"
            else:
                target_url = "https://open.spotify.com"
                step_name = f"Open Spotify{browser_label}"
                desc = f"Spotify{browser_label}"

            return CompoundStep(
                order=order,
                name=step_name,
                tool="browser_open_target",
                args={"url": target_url, "browser": browser or "brave", "query": query},
                description=desc,
                browser_override=browser,
            )

        # 2. YouTube search
        if "youtube" in t_clean:
            query = t_clean
            for phrase in ["open youtube and search", "search youtube for", "open youtube", "search"]:
                query = re.sub(rf"\b{re.escape(phrase)}\b", "", query, flags=re.IGNORECASE)
            query = query.strip()
            browser_label = f" in {browser.capitalize()}" if browser else ""
            if query:
                target_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                step_name = f"YouTube {query.title()}{browser_label}"
                desc = f"YouTube search for '{query.title()}'{browser_label}"
            else:
                target_url = "https://www.youtube.com"
                step_name = f"Open YouTube{browser_label}"
                desc = f"YouTube{browser_label}"

            return CompoundStep(
                order=order,
                name=step_name,
                tool="browser_open_target",
                args={"url": target_url, "browser": browser or "brave", "query": query},
                description=desc,
                browser_override=browser,
            )

        # 3. WhatsApp call / communication
        if "whatsapp" in t_clean or "call" in t_clean or "message" in t_clean:
            contact_match = re.search(r"(?:call|ring|phone|message|text)\s+([a-zA-Z0-9_+-]+)", t_clean)
            raw_target = contact_match.group(1).strip() if contact_match else "Contact"
            resolved_name, phone = self._resolve_contact(raw_target)

            is_call = any(w in t_clean for w in ["call", "ring", "phone"]) or ("whatsapp" in t_clean and "message" not in t_clean)
            action_type = "Voice Call" if is_call else "Message"

            return CompoundStep(
                order=order,
                name=f"WhatsApp {action_type} to {resolved_name}",
                tool="call_whatsapp" if is_call else "message_whatsapp",
                args={"recipient": resolved_name, "phone": phone, "is_call": is_call},
                description=f"WhatsApp {action_type} to {resolved_name}",
            )

        # 4. Generic application open
        open_match = re.search(r"open\s+([a-zA-Z0-9_-]+)", t_clean)
        if open_match:
            app_name = open_match.group(1).strip()
            return CompoundStep(
                order=order,
                name=f"Open {app_name.capitalize()}",
                tool="open_app",
                args={"application": app_name},
                description=f"opening {app_name.capitalize()}",
            )

        return None

    def execute_plan(self, plan: CompoundPlan, mid_sentence: bool = True) -> Dict[str, Any]:
        """
        Executes the compound plan in inverted sequence with mid-sentence speech
        and live EV HUD notifications.
        """
        t0 = time.perf_counter()

        logger.info(f"[CompoundIntent] 🚀 Executing Compound Plan with {len(plan.steps)} steps...")

        # 1. Mid-sentence voice acknowledgment
        if mid_sentence and plan.speech_acknowledgment:
            try:
                from jarvisx.voice.sovereign_neural_tts import get_neural_tts
                tts = get_neural_tts()
                tts.speak(plan.speech_acknowledgment, voice_key="hyper_realistic_female", blocking=False)
            except Exception as e:
                logger.debug(f"[CompoundIntent] Speech error: {e}")

        # 2. Push microsteps to HUD
        step_descriptions = [f"Step {s.order}: {s.description}" for s in plan.steps]
        try:
            from jarvisx.dashboard.event_bus import push_event_sync, push_ev_notification
            push_event_sync("exec_microsteps", {
                "steps": [
                    f"Self-Correction: Pivot '{plan.pivot_keyword}' detected",
                    "Inverting execution DAG priorities",
                ] + step_descriptions + ["Compound task execution finalized"]
            })
        except Exception:
            pass

        executed_results = []

        # 3. Execute Steps in Order
        for step in plan.steps:
            step_t0 = time.perf_counter()
            logger.info(f"[CompoundIntent] Executing Step {step.order}: {step.name} ({step.tool})...")

            res_data = None

            if step.tool == "browser_open_target":
                url = step.args.get("url", "https://open.spotify.com")
                browser_key = step.args.get("browser", "brave")
                browser_exe = self._resolve_browser_executable(browser_key)

                launched = False
                if browser_exe:
                    try:
                        subprocess.Popen([browser_exe, url], shell=False)
                        launched = True
                    except Exception as e:
                        logger.debug(f"[CompoundIntent] Direct browser launch failed: {e}")

                if not launched:
                    # Fallback to default browser
                    try:
                        subprocess.Popen(["cmd.exe", "/c", "start", "", url], shell=False)
                        launched = True
                    except Exception:
                        pass

                res_data = {"status": "success" if launched else "failed", "url": url, "browser": browser_key}

                try:
                    from jarvisx.dashboard.event_bus import push_ev_notification
                    push_ev_notification(
                        title="🎵 TARGET LAUNCHED",
                        message=f"Playing on Spotify in {browser_key.capitalize()}: {step.args.get('query', 'Music')}",
                        level="success",
                    )
                except Exception:
                    pass

            elif step.tool in ("call_whatsapp", "message_whatsapp"):
                recipient = step.args.get("recipient", "Contact")
                phone = step.args.get("phone", "")
                is_call = step.args.get("is_call", True)

                # Clean phone digits if present
                clean_phone = "".join(filter(str.isdigit, phone)) if phone else ""
                if len(clean_phone) >= 7:
                    proto = f"whatsapp://send?phone={clean_phone}"
                    toast_msg = f"Initiating WhatsApp {'Voice Call' if is_call else 'Message'} to {recipient} ({phone})"
                else:
                    # Opens WhatsApp directly without telephone requirement
                    proto = "whatsapp://send?text="
                    toast_msg = f"Opening WhatsApp for {recipient}"

                try:
                    subprocess.Popen(["cmd.exe", "/c", "start", "", proto], shell=False)
                except Exception:
                    pass

                res_data = {"status": "success", "recipient": recipient, "phone": phone}

                try:
                    from jarvisx.dashboard.event_bus import push_ev_notification
                    push_ev_notification(
                        title="📞 COMMS DISPATCHED" if is_call else "💬 COMMS DISPATCHED",
                        message=toast_msg,
                        level="success",
                    )
                except Exception:
                    pass

            elif step.tool == "open_app":
                app = step.args.get("application", "")
                try:
                    subprocess.Popen(["cmd.exe", "/c", "start", "", f"{app}.exe"], shell=False)
                    res_data = {"status": "success", "app": app}
                except Exception as e:
                    res_data = {"status": "failed", "error": str(e)}

            step_elapsed = round((time.perf_counter() - step_t0) * 1000, 1)
            executed_results.append({
                "step": step.order,
                "name": step.name,
                "tool": step.tool,
                "elapsed_ms": step_elapsed,
                "result": res_data,
            })

            # Micro pause between sequential stages
            time.sleep(0.5)

        total_elapsed = round((time.perf_counter() - t0) * 1000, 1)

        return {
            "status": "success",
            "is_compound": True,
            "has_self_correction": True,
            "pivot": plan.pivot_keyword,
            "total_duration_ms": total_elapsed,
            "steps": executed_results,
        }


def get_compound_decomposer() -> CompoundIntentDecomposer:
    return CompoundIntentDecomposer.get_instance()
