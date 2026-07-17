"""Vision Analyzer — summarizes visual information and OCR text."""
import re

class VisionAnalyzer:
    """Analyzes text extracted from screen to detect likely intent or errors."""

    @classmethod
    def analyze_error(cls, text: str) -> str:
        """Analyze text specifically looking for errors to explain."""
        if not text:
            return ""

        # Traceback / ModuleNotFoundError
        match = re.search(r"ModuleNotFoundError:\s*No module named\s*['\"]([^'\"]+)['\"]", text)
        if match:
            pkg = match.group(1)
            return (f"The application failed because it could not import the {pkg} package. "
                    f"Installing it with pip install {pkg} should resolve the issue.")
        
        if "Traceback" in text:
            return "There appears to be a Python traceback visible in the terminal."

        # Web errors
        if "404 Page Not Found" in text or "404 Not Found" in text:
            return "The webpage appears unavailable due to a 404 error."

        return "I can see some text, but I did not detect a recognized error pattern."

    @classmethod
    def summarize_page(cls, text: str, window_title: str) -> str:
        """Provide a general summary of the page."""
        if not text and not window_title:
            return "I cannot see any recognizable content or application."

        summary = ""
        if window_title:
            summary += f"I can see {window_title}.\n\n"

        if "Traceback" in text or "Error" in text:
            summary += "There appears to be an error or traceback visible.\n"
            
        if "def " in text or "import " in text or "class " in text:
            summary += "It looks like you are viewing some Python source code.\n"
            
        if not summary:
            summary = "I can see the application, but the content is generic."

        return summary.strip()
