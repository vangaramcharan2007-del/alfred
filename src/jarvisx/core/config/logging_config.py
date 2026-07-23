import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Common log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def _setup_logger(name: str, log_file: str, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=5 * 1024 * 1024, # 5MB
        backupCount=5
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding handlers multiple times in the same process
    if not logger.handlers:
        logger.addHandler(handler)
        
        # Add console handler for critical errors
        if log_file == "errors.log":
            console = logging.StreamHandler()
            console.setLevel(logging.ERROR)
            console.setFormatter(formatter)
            logger.addHandler(console)

    return logger

def setup_logging():
    """Initializes all the core structured loggers for the system."""
    loggers = {
        "runtime": _setup_logger("jarvisx.runtime", "runtime.log"),
        "errors": _setup_logger("jarvisx.errors", "errors.log", level=logging.ERROR),
        "voice": _setup_logger("jarvisx.voice", "voice.log"),
        "llm": _setup_logger("jarvisx.llm", "llm.log"),
        "skills": _setup_logger("jarvisx.skills", "skills.log"),
        "mission": _setup_logger("jarvisx.mission", "mission.log")
    }
    return loggers

def get_logger(name: str):
    """Get a specific logger. Will fall back to runtime if unknown."""
    valid_names = ["jarvisx.runtime", "jarvisx.errors", "jarvisx.voice", "jarvisx.llm", "jarvisx.skills", "jarvisx.mission"]
    if name not in valid_names:
        name = "jarvisx.runtime"
    return logging.getLogger(name)
