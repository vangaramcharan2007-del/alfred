import logging
import asyncio
from jarvisx.core.tools.execution import CommandExecutor, AppLauncher, GitOps

logger = logging.getLogger(__name__)

class CommandDispatcher:
    """
    Executes specific OS and browser automation commands based on categorized intents.
    Interfaces directly with the underlying operating system (Windows/macOS/Linux).
    """
    def __init__(self):
        pass

    async def execute_os_command(self, text: str) -> str:
        """
        Executes operations like 'Open VS Code' or 'Increase brightness'.
        """
        logger.info(f"OS Command Dispatch: {text}")
        text_lower = text.lower()
        if "open vs code" in text_lower or "code" in text_lower:
            success = AppLauncher.launch("code")
            return "Visual Studio Code opened successfully." if success else "Failed to open VS Code."
        elif "chrome" in text_lower:
            if "open" in text_lower:
                success = AppLauncher.launch("chrome")
                return "Chrome opened successfully." if success else "Failed to open Chrome."
            elif "close" in text_lower:
                success = AppLauncher.close("chrome")
                return "Chrome closed successfully." if success else "Failed to close Chrome."
        elif "notepad" in text_lower:
            success = AppLauncher.launch("notepad")
            return "Notepad opened successfully." if success else "Failed to open Notepad."
            
        return "OS command executed but not explicitly handled."

    async def execute_dev_command(self, text: str) -> str:
        """
        Executes workflow commands like 'Run tests', 'Commit changes'.
        """
        logger.info(f"Dev Command Dispatch: {text}")
        text_lower = text.lower()
        if "run tests" in text_lower:
            res = CommandExecutor.execute("pytest")
            return f"Tests executed. Result: {res['stdout']}" if res['success'] else f"Tests failed: {res['stderr']} {res['stdout']}"
        elif "commit" in text_lower:
            success = GitOps.commit("Automated voice commit")
            return "Changes committed." if success else "Failed to commit changes."
        elif "push" in text_lower:
            success = GitOps.push()
            return "Changes pushed." if success else "Failed to push changes."
            
        return "Development command executed but not explicitly handled."

    async def execute_browser_command(self, text: str) -> str:
        """
        Executes browser automation. Currently falls back to generic OS launch.
        """
        logger.info(f"Browser Command Dispatch: {text}")
        if "github" in text.lower():
            success = CommandExecutor.execute("start https://github.com")
            return "Navigated to GitHub." if success['success'] else "Failed to open browser."
        return "Browser action completed."

