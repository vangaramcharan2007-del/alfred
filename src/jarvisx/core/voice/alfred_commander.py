"""Alfred Commander — maps spoken commands to existing Jarvis X subsystems.

This is NOT a new orchestrator.  It is a thin dispatch layer that translates
natural-language voice commands into calls to the systems that already exist.
"""
import time
import datetime
import re
from typing import Optional, Tuple, Dict, Any

from jarvisx.core.presence_manager import PresenceManager
from jarvisx.core.diagnostics_console import DiagnosticsConsole
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.mission_continuity import MissionContinuityManager
from jarvisx.core.alfred_summarizer import AlfredSummarizer
from jarvisx.core.notification_policy import NotificationPolicy, NotificationLevel
from jarvisx.core.os_control.app_launcher import AppLauncher
from jarvisx.core.os_control.browser_launcher import BrowserLauncher
from jarvisx.core.browser.browser_controller import BrowserController


class AlfredCommander:
    """Thin dispatch layer — voice command -> existing subsystem."""

    def __init__(
        self,
        presence: PresenceManager,
        diagnostics: DiagnosticsConsole,
        objective_store: ObjectiveStore,
        continuity: MissionContinuityManager,
        notification_policy: NotificationPolicy,
    ):
        self.presence = presence
        self.diagnostics = diagnostics
        self.store = objective_store
        self.continuity = continuity
        self.policy = notification_policy
        self.summarizer = AlfredSummarizer()
        self.browser_controller = BrowserController.get_instance()

        # Intent definitions with keyword sets for fuzzy matching
        self.intents = {
            "GREETING": ["hello", "hi", "hey", "greetings", "good morning", "good evening", "good afternoon", "alfred"],
            "TIME_QUERY": ["what time", "current time", "tell me the time", "time please", "the time"],
            "STATUS_QUERY": ["what are you doing", "what r u doing", "status", "current status", "what are you working on", "what's going on"],
            "DIAGNOSTICS": ["diagnostics", "show diagnostics", "show diag", "show di", "system report"],
            "CONTINUITY": ["continue my work", "resume work", "continue objective", "resume previous task", "continue", "resume"],
            "STOP": ["stop", "exit", "quit", "goodbye", "shut down", "shutdown", "bye"],
            "OPEN_APPLICATION": ["open vscode", "open visual studio code", "open chrome", "open browser", "open notepad", "open calculator", "open file explorer", "launch vscode", "start vscode"],
            "OPEN_WEBSITE": ["open youtube", "open github", "open chatgpt", "open the openai github page"],
            "SEARCH_GOOGLE": ["search google for", "search google"],
            "SEARCH_YOUTUBE": ["search youtube for", "search youtube"],
            "SEARCH_GITHUB": ["search github for", "search github"]
        }

    def _normalize_transcript(self, text: str) -> str:
        """Normalize common speech-to-text abbreviations and quirks."""
        lower = text.lower().strip()
        # Expand common abbreviations
        replacements = {
            r"\bu\b": "you",
            r"\br\b": "are",
            r"\bdi\b": "diagnostics",
            r"\bdiag\b": "diagnostics",
            r"\bal\b": "alfred"
        }
        normalized = lower
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized

    def _classify_intent(self, normalized_text: str) -> Tuple[str, float, str]:
        """Classify the intent using fuzzy keyword matching.
        Returns (intent, confidence, target)
        """
        best_intent = "UNKNOWN"
        max_score = 0.0
        target = ""

        words = set(normalized_text.split())

        for intent, keywords in self.intents.items():
            score = 0.0
            matched_keyword = ""
            for keyword in keywords:
                # Exact phrase match gives highest confidence
                if keyword in normalized_text:
                    score = max(score, 0.95)
                    matched_keyword = keyword
                else:
                    # Partial word match
                    keyword_words = set(keyword.split())
                    match_count = len(words.intersection(keyword_words))
                    if match_count > 0:
                        current_score = 0.5 + (0.4 * (match_count / len(keyword_words)))
                        if current_score > score:
                            score = current_score
                            matched_keyword = keyword

            if score > max_score:
                max_score = score
                best_intent = intent
                
                # Extract target for OPEN intents
                if best_intent in ("OPEN_APPLICATION", "OPEN_WEBSITE"):
                    if "open " in matched_keyword:
                        target = matched_keyword.replace("open ", "").strip()
                    elif "launch " in matched_keyword:
                        target = matched_keyword.replace("launch ", "").strip()
                    elif "start " in matched_keyword:
                        target = matched_keyword.replace("start ", "").strip()
                    else:
                        target = matched_keyword
                elif best_intent in ("SEARCH_GOOGLE", "SEARCH_YOUTUBE", "SEARCH_GITHUB"):
                    if "for " in normalized_text:
                        target = normalized_text.split("for ", 1)[1].strip()
                    else:
                        target = ""
                else:
                    target = ""

        return best_intent, max_score, target

    def handle(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Process spoken text.

        Returns (spoken_reply, optional_display_text).
        spoken_reply is what Alfred says aloud.
        display_text is optional extra output for the terminal (e.g. diagnostics).
        """
        print(f"\nRaw transcript:\n{text}")
        normalized = self._normalize_transcript(text)
        print(f"\nNormalized transcript:\n{normalized}")

        intent, confidence, target = self._classify_intent(normalized)
        print(f"\nIntent: \n{intent}")
        if target:
            if intent in ("SEARCH_GOOGLE", "SEARCH_YOUTUBE", "SEARCH_GITHUB"):
                print(f"Query:\n{target}")
            else:
                print(f"Target:\n{target}")
        print(f"Confidence: {confidence:.2f}")

        # Threshold for acting on intent
        if confidence < 0.6:
            intent = "UNKNOWN"

        if intent == "OPEN_APPLICATION":
            success = AppLauncher.launch(target)
            if success:
                print("Action:\nSUCCESS\n")
                if "vscode" in target or "visual studio code" in target:
                    return "Opening Visual Studio Code.", None
                else:
                    return f"Opening {target.title()}.", None
            else:
                print("Action:\nFAILURE\n")
                return "I could not locate that application on this system.", None

        elif intent == "OPEN_WEBSITE":
            success = False
            if "github" in target:
                success = self.browser_controller.open_github()
            elif "chatgpt" in target:
                success = self.browser_controller.open_chatgpt()
            else:
                success = BrowserLauncher.launch(target)
                
            if success:
                print("Action:\nSUCCESS\n")
                return f"Opening {target.title()}.", None
            else:
                print("Action:\nFAILURE\n")
                return "I don't currently know how to open that website.", None

        elif intent == "SEARCH_GOOGLE":
            print(f"Action:\nSUCCESS\n")
            self.browser_controller.search_google(target)
            return f"Searching Google for {target}. Search completed.", None

        elif intent == "SEARCH_YOUTUBE":
            print(f"Action:\nSUCCESS\n")
            self.browser_controller.search_youtube(target)
            return f"Searching YouTube for {target}. Search completed.", None

        elif intent == "SEARCH_GITHUB":
            print(f"Action:\nSUCCESS\n")
            self.browser_controller.search_github(target)
            return f"Searching GitHub for {target}. Search completed.", None

        elif intent == "GREETING":
            hour = datetime.datetime.now().hour
            if hour < 12:
                greeting = "Good morning."
            elif hour < 17:
                greeting = "Good afternoon."
            else:
                greeting = "Good evening."
            return f"{greeting} How may I assist you?", None

        elif intent == "TIME_QUERY":
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"It is currently {now}.", None

        elif intent == "DIAGNOSTICS":
            display = self.diagnostics.render()
            return "Here are the current diagnostics.", display

        elif intent == "STATUS_QUERY":
            summary = self.presence.get_active_summary()
            agents = self.presence.get_running_agent_names()
            agent_note = self.summarizer.summarize_agents_hidden(agents)
            return f"{summary} {agent_note}", None

        elif intent == "CONTINUITY":
            interrupted = self.continuity.detect_interrupted_work()
            if interrupted:
                count = len(interrupted)
                titles = ", ".join(o.get("title", "unknown") for o in interrupted[:3])
                return (
                    f"I found {count} interrupted objective{'s' if count > 1 else ''}: {titles}. "
                    "Resuming execution now.",
                    None,
                )
            else:
                return "There is no interrupted work. Standing by.", None

        elif intent == "STOP":
            return "Understood. Shutting down. Good night.", "__EXIT__"

        else:
            fallback_msg = (
                "I didn't understand that request.\n\n"
                "You can ask me things such as:\n"
                "- what time is it\n"
                "- what are you doing\n"
                "- continue my work\n"
                "- show diagnostics\n"
                "- open vscode\n"
                "- search youtube for python tutorials"
            )
            # Spoken fallback is shorter, display is full
            return "I didn't understand that request. Please try asking about the time, my status, or searching for something.", fallback_msg


