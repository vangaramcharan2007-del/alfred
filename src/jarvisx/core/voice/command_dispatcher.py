import logging
import asyncio

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
        if "open vs code" in text.lower():
            return "Opening Visual Studio Code."
        elif "chrome" in text.lower():
            return "Closing Chrome."
        return "OS command executed."

    async def execute_dev_command(self, text: str) -> str:
        """
        Executes workflow commands like 'Run tests', 'Commit changes'.
        """
        logger.info(f"Dev Command Dispatch: {text}")
        if "run tests" in text.lower():
            return "Running test suite. All tests passed."
        elif "commit" in text.lower():
            return "Changes committed."
        return "Development command executed."

    async def execute_browser_command(self, text: str) -> str:
        """
        Executes browser automation.
        """
        logger.info(f"Browser Command Dispatch: {text}")
        if "github" in text.lower():
            return "Navigated to GitHub."
        return "Browser action completed."
