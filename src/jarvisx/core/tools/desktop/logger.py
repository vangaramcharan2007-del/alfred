import logging

class DesktopLogger:
    _logger = logging.getLogger("JarvisDesktop")
    _logger.setLevel(logging.DEBUG)
    
    if not _logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [ACTION] %(message)s')
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

    @classmethod
    def log_action(cls, component: str, action: str, details: str, status: str = "SUCCESS"):
        cls._logger.info(f"{component} | {action} | {details} | {status}")

    @classmethod
    def log_error(cls, component: str, action: str, error: str):
        cls._logger.error(f"{component} | {action} | ERROR | {error}")
