import inspect
import logging
import asyncio
import time
import hashlib
from typing import Dict, Any, List, Optional
from jarvisx.config.settings import DeveloperSettings

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Universal tool registry supporting self-registration, runtime discovery, and dynamic dispatch."""

    _instance: Optional['ToolRegistry'] = None

    def __init__(self):
        self._tools: Dict[str, Any] = {}  # name -> instance
        self._schemas: Dict[str, Dict[str, Any]] = {}  # name -> schema cache
        self._auto_register_defaults()

    def _auto_register_defaults(self):
        """Automatically registers standard capability tools."""
        try:
            from jarvisx.core.tools.execution.file_ops import FileOps
            self.register(FileOps(), "file_ops")
        except ImportError:
            pass

    def load_generated_skills(self):
        """Automatically discover and register generated skills."""
        import os
        import importlib.util
        import sys
        
        skills_dir = "src/jarvisx/skills"
        if not os.path.exists(skills_dir):
            return
            
        for filename in os.listdir(skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(skills_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(f"jarvisx.skills.{module_name}", file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[f"jarvisx.skills.{module_name}"] = module
                        spec.loader.exec_module(module)
                        
                        # Find the skill class and register it
                        for attr_name in dir(module):
                            if attr_name.endswith("Skill"):
                                skill_class = getattr(module, attr_name)
                                if isinstance(skill_class, type):
                                    # Instantiate and register
                                    self.register(skill_class(), module_name)
                except Exception as e:
                    logger.error(f"Failed to load generated skill {module_name}: {e}")

    def get_capability_count(self) -> int:
        """Expose the number of registered capabilities."""
        return len(self._tools)
            
        try:
            from jarvisx.core.tools.execution.command_executor import CommandExecutor
            self.register(CommandExecutor(), "command_executor")
        except ImportError:
            pass

        try:
            from jarvisx.core.tools.desktop_ops import DesktopOps
            self.register(DesktopOps(), "desktop_ops")
        except ImportError:
            pass

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton for testing."""
        cls._instance = None

    def register(self, tool_instance: Any, name: Optional[str] = None) -> None:
        """Register a tool instance under a canonical name."""
        tool_name = name or self._derive_name(tool_instance)
        self._tools[tool_name] = tool_instance
        self._schemas[tool_name] = self._introspect(tool_instance, tool_name)
        logger.info(f"Registered tool: {tool_name} with methods: {list(self._schemas[tool_name]['methods'].keys())}")

    def unregister(self, tool_name: str) -> bool:
        if tool_name in self._tools:
            del self._tools[tool_name]
            del self._schemas[tool_name]
            return True
        return False

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def has_method(self, tool_name: str, method_name: str) -> bool:
        if tool_name not in self._schemas:
            return False
        return method_name in self._schemas[tool_name]['methods']

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def list_methods(self, tool_name: str) -> List[str]:
        if tool_name not in self._schemas:
            raise KeyError(f"Tool '{tool_name}' not registered")
        return list(self._schemas[tool_name]['methods'].keys())

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        if tool_name not in self._schemas:
            raise KeyError(f"Tool '{tool_name}' not registered")
        return self._schemas[tool_name]

    def get_capability_manifest(self) -> List[Dict[str, Any]]:
        """Returns a structured capability list for LLM prompt injection."""
        manifest = []
        for tool_name, schema in self._schemas.items():
            entry = {
                "tool": tool_name,
                "methods": []
            }
            for method_name, method_info in schema['methods'].items():
                entry["methods"].append({
                    "name": method_name,
                    "parameters": method_info['parameters']
                })
            manifest.append(entry)
        return manifest

    async def execute(self, tool_name: str, method_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool method and return structured evidence."""
        if tool_name not in self._tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not registered",
                "evidence": {}
            }

        tool_instance = self._tools[tool_name]

        if not hasattr(tool_instance, method_name):
            return {
                "success": False,
                "error": f"Method '{method_name}' not found on tool '{tool_name}'",
                "evidence": {}
            }

        method = getattr(tool_instance, method_name)
        start_time = time.time()

        try:
            if DeveloperSettings.TRACE_TOOL_EXECUTION:
                logger.info(f"[TRACE] Executing {tool_name}.{method_name} with {arguments}")
                
            if asyncio.iscoroutinefunction(method):
                result = await method(**arguments)
            else:
                result = await asyncio.to_thread(method, **arguments)
                
            if DeveloperSettings.TRACE_TOOL_EXECUTION:
                logger.info(f"[TRACE] Completed {tool_name}.{method_name} -> {result}")

            duration_ms = int((time.time() - start_time) * 1000)

            # Build evidence
            evidence = {
                "tool": tool_name,
                "method": method_name,
                "args": arguments,
                "duration_ms": duration_ms,
                "timestamp": time.time()
            }

            # Normalize result
            if isinstance(result, dict):
                success = result.get("success", True)
                evidence["output"] = result
            elif isinstance(result, bool):
                success = result
                evidence["output"] = {"result": result}
            elif isinstance(result, str):
                success = True
                evidence["output"] = {"result": result}
                evidence["checksum"] = hashlib.sha256(result.encode('utf-8', errors='replace')).hexdigest()[:16]
            elif result is None:
                success = False
                evidence["output"] = {"result": None}
            else:
                success = True
                evidence["output"] = {"result": str(result)}

            return {
                "success": success,
                "evidence": evidence
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Execution failed: {tool_name}.{method_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "evidence": {
                    "tool": tool_name,
                    "method": method_name,
                    "args": arguments,
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                    "exception": str(e)
                }
            }

    @staticmethod
    def _derive_name(tool_instance: Any) -> str:
        """Derives a snake_case name from the class name."""
        name = type(tool_instance).__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)

    @staticmethod
    def _introspect(tool_instance: Any, tool_name: str) -> Dict[str, Any]:
        """Introspects tool instance to discover callable public methods and their signatures."""
        schema = {
            "tool": tool_name,
            "class": type(tool_instance).__name__,
            "methods": {}
        }

        for attr_name in dir(tool_instance):
            if attr_name.startswith('_'):
                continue

            attr = getattr(tool_instance, attr_name)
            if not callable(attr):
                continue

            try:
                sig = inspect.signature(attr)
            except (ValueError, TypeError):
                continue

            params = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                param_info = {"required": param.default is inspect.Parameter.empty}
                if param.annotation != inspect.Parameter.empty:
                    param_info["type"] = str(param.annotation)
                if param.default is not inspect.Parameter.empty:
                    param_info["default"] = str(param.default)
                params[param_name] = param_info

            schema["methods"][attr_name] = {
                "parameters": params
            }

        return schema
