"""Task Planner — converts natural language objectives into structured deterministic plans."""
import re
import uuid
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TaskPlanner:
    """Parses predefined objective patterns into actionable execution steps."""
    
    def plan(self, objective: str) -> Optional[Dict[str, Any]]:
        """Attempt to plan the objective. Returns None if unknown."""
        text = objective.strip()
        
        # Pattern 1: create a file called X containing Y
        if match := re.search(r"create a file called\s+(.+?)\s+containing\s+(.+)", text, re.IGNORECASE):
            filename = match.group(1).strip()
            content = match.group(2).strip()
            return self._plan_create_file(filename, content)
            
        # Pattern 2: create a folder called/named X on desktop
        if match := re.search(r"create a folder (?:called|named)\s+(.*?)(?:\s+on\s+the\s+desktop)?$", text, re.IGNORECASE):
            foldername = match.group(1).strip()
            return self._plan_create_folder(foldername)
            
        # Pattern 3: search google for X
        if match := re.search(r"search google for\s+(.+)", text, re.IGNORECASE):
            query = match.group(1).strip()
            return self._plan_google_search(query)
            
        # Pattern 4: open vscode and create X
        if match := re.search(r"open vscode and create\s+(.+)", text, re.IGNORECASE):
            filename = match.group(1).strip()
            return self._plan_vscode_create(filename)
            
        # Pattern 5: Open Google in Browser (for fallback testing)
        if match := re.search(r"open google in\s+(.+)", text, re.IGNORECASE):
            browser = match.group(1).strip()
            return self._plan_open_google_in(browser)
            
        # Pattern 6: Create file at absolute path (for permission testing)
        if match := re.search(r"create file at\s+(.+)", text, re.IGNORECASE):
            target = match.group(1).strip()
            return self._plan_create_file_direct(target)
            
        # Pattern 7: Launch app (for capability fallback testing)
        if match := re.search(r"launch\s+(.+)", text, re.IGNORECASE):
            app = match.group(1).strip()
            return self._plan_launch_app(app)
            
        return None

    def _plan_create_file(self, filename: str, content: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "CREATE_FILE",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Opening Notepad.",
                    "action_type": "OPEN_APPLICATION",
                    "target": "notepad",
                    "verification": "WINDOW_EXISTS"
                },
                {
                    "step_id": 2,
                    "description": "Typing content.",
                    "action_type": "TYPE_TEXT",
                    "target": content,
                    "verification": "NONE"
                },
                {
                    "step_id": 3,
                    "description": "Saving file.",
                    "action_type": "PRESS_SHORTCUT",
                    "target": "ctrl s",
                    "verification": "NONE"
                },
                {
                    "step_id": 4,
                    "description": "Entering filename.",
                    "action_type": "TYPE_TEXT",
                    "target": f"${{DESKTOP}}/{filename}",
                    "verification": "NONE"
                },
                {
                    "step_id": 5,
                    "description": "Confirming save.",
                    "action_type": "PRESS_SHORTCUT",
                    "target": "enter",
                    "verification": "FILE_EXISTS",
                    "verification_target": filename
                }
            ]
        }

    def _plan_create_folder(self, foldername: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "CREATE_FOLDER",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Opening Desktop context.",
                    "action_type": "OPEN_APPLICATION",
                    "target": "explorer shell:::{00000000-0000-0000-0000-000000000000}", # Workaround or just rely on file creation
                    "verification": "NONE"
                },
                {
                    "step_id": 2,
                    "description": "Creating folder via system.",
                    "action_type": "CREATE_FOLDER_DIRECT",
                    "target": foldername,
                    "verification": "FOLDER_EXISTS",
                    "verification_target": foldername
                }
            ]
        }
        
    def _plan_google_search(self, query: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "GOOGLE_SEARCH",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Opening browser.",
                    "action_type": "SEARCH_GOOGLE",
                    "target": query,
                    "verification": "BROWSER_URL_MATCHES",
                    "verification_target": "google.com/search"
                }
            ]
        }
        
    def _plan_vscode_create(self, filename: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "CREATE_VSCODE_FILE",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Opening Visual Studio Code.",
                    "action_type": "OPEN_APPLICATION",
                    "target": "vscode",
                    "verification": "WINDOW_EXISTS",
                    "verification_target": "Visual Studio Code"
                },
                {
                    "step_id": 2,
                    "description": "Creating new file.",
                    "action_type": "PRESS_SHORTCUT",
                    "target": "ctrl n",
                    "verification": "NONE"
                },
                {
                    "step_id": 3,
                    "description": "Triggering save dialog.",
                    "action_type": "PRESS_SHORTCUT",
                    "target": "ctrl s",
                    "verification": "NONE"
                },
                {
                    "step_id": 4,
                    "description": "Typing filename.",
                    "action_type": "TYPE_TEXT",
                    "target": f"${{DESKTOP}}/{filename}",
                    "verification": "NONE"
                },
                {
                    "step_id": 5,
                    "description": "Confirming save.",
                    "action_type": "PRESS_SHORTCUT",
                    "target": "enter",
                    "verification": "FILE_EXISTS",
                    "verification_target": filename
                }
            ]
        }

    def _plan_open_google_in(self, browser: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "OPEN_GOOGLE",
            "steps": [
                {
                    "step_id": 1,
                    "description": f"Opening {browser}.",
                    "action_type": "OPEN_APPLICATION",
                    "target": browser.lower(),
                    "verification": "WINDOW_EXISTS",
                    "verification_target": browser
                },
                {
                    "step_id": 2,
                    "description": "Searching Google.",
                    "action_type": "SEARCH_GOOGLE",
                    "target": "hello", # Dummy search to trigger browser loading google
                    "verification": "NONE"
                }
            ]
        }
        
    def _plan_create_file_direct(self, target: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "CREATE_FILE_DIRECT",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Creating file.",
                    "action_type": "CREATE_FILE_DIRECT",
                    "target": target,
                    "verification": "FILE_EXISTS",
                    "verification_target": target
                }
            ]
        }

    def _plan_launch_app(self, app: str) -> Dict[str, Any]:
        return {
            "objective_id": str(uuid.uuid4()),
            "objective_type": "LAUNCH_APP",
            "steps": [
                {
                    "step_id": 1,
                    "description": f"Launching {app}.",
                    "action_type": "OPEN_APPLICATION",
                    "target": app.lower(),
                    "verification": "WINDOW_EXISTS",
                    "verification_target": app
                }
            ]
        }
