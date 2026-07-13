import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Optional

from jarvisx.agents.base import BaseAgent
from jarvisx.agents.registry import AgentRegistry
from jarvisx.core.logging import StructuredLogger


class PluginLoader:
    """Discovers and registers agents dynamically from a plugins directory."""

    def __init__(self, registry: AgentRegistry, logger: Optional[StructuredLogger] = None):
        self.registry = registry
        self.logger = logger or StructuredLogger()

    def load_from_directory(self, plugins_dir: Path) -> None:
        """Scans the directory for .py files, imports them, and registers any BaseAgent subclasses."""
        if not plugins_dir.exists() or not plugins_dir.is_dir():
            self.logger.write("warning", "plugin_loader.dir_not_found", path=str(plugins_dir))
            return

        for py_file in plugins_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            module_name = f"jarvisx.plugins.{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec is None or spec.loader is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # We want subclasses of BaseAgent, but not BaseAgent itself
                    if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        # Instantiate the agent. We inject an empty tools dict and logger for now.
                        # Complex tools injection for plugins might require a tool registry in the future.
                        try:
                            agent_instance = obj(tools={}, logger=self.logger)
                            # Register unless it's already there
                            if self.registry.maybe_get(agent_instance.agent_id) is None:
                                self.registry.register(agent_instance)
                                self.logger.write("info", "plugin_loader.registered", agent_id=agent_instance.agent_id, source=py_file.name)
                        except Exception as e:
                            self.logger.write("error", "plugin_loader.instantiation_failed", agent_class=name, error=str(e))
                            
            except Exception as e:
                self.logger.write("error", "plugin_loader.import_failed", file=py_file.name, error=str(e))
