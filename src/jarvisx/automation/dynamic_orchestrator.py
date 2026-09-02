"""Dynamic Windows Application Launcher & Work Execution Orchestrator (Layer 5 - Execution).

Executes genuine end-to-end work automation: PC cleaning, App generation, Test debugging, 
Workspace briefings, and Kernel mission orchestration.
"""

from __future__ import annotations
import os
import sys
import re
import glob
import time
import asyncio
import datetime
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.automation.real_system_cleaner import RealSystemCleaner
from jarvisx.automation.real_project_builder import RealProjectBuilder
from jarvisx.llm.llm_router import LLMRouter


class DynamicOrchestrator:
    """Zero-hardcode dynamic Windows application & work execution orchestrator."""

    def __init__(
        self,
        os_kernel: Optional[PersonalOSKernel] = None,
        llm_router: Optional[LLMRouter] = None,
        memory_engine: Optional[Any] = None,
    ):
        self.user_name: str = "Charan"
        self.kernel = os_kernel or PersonalOSKernel()
        self.cleaner = RealSystemCleaner()
        self.builder = RealProjectBuilder()
        self.llm_router = llm_router or LLMRouter()
        self._memory_engine = memory_engine

    @property
    def memory_engine(self):
        if self._memory_engine is None:
            try:
                from jarvisx.memory_intelligence.memory_engine import MemoryIntelligenceEngine
                self._memory_engine = MemoryIntelligenceEngine()
            except Exception as e:
                print(f"[MEMORY] Memory engine initialization fallback: {e}")
                self._memory_engine = None
        return self._memory_engine

    def find_and_launch_app(self, app_name: str) -> Dict[str, Any]:
        """Dynamically search Windows protocols, Start Menu, PATH, and Registry for any app name."""
        clean_name = app_name.lower().replace("open", "").replace("launch", "").replace("start", "").strip()
        if not clean_name:
            return {"status": "FAILED", "reason": "Empty app name"}

        # 1. Native Windows Protocol Schemes (Launches direct native desktop apps)
        native_protocols = {
            "whatsapp": "whatsapp:",
            "spotify": "spotify:",
            "discord": "discord:",
            "telegram": "tg:",
            "calc": "calc:",
            "calculator": "calc:",
            "settings": "ms-settings:",
            "store": "ms-windows-store:",
            "notepad": "notepad",
            "terminal": "wt",
            "cmd": "cmd",
            "code": "code",
            "vscode": "code",
            "chrome": "chrome",
            "edge": "msedge",
            "file explorer": "explorer",
            "explorer": "explorer",
        }

        for key, proto in native_protocols.items():
            if key == clean_name or clean_name in key:
                try:
                    subprocess.Popen(f"start {proto}", shell=True)
                    return {"status": "LAUNCHED_DESKTOP", "target": key, "protocol": proto, "app_name": key.title()}
                except Exception:
                    pass

        # 2. Search Windows Start Menu Shortcuts (.lnk) and Executables
        _home = os.path.expanduser("~")
        search_paths = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.join(_home, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(_home, "AppData", "Local", "Programs"),
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]

        found_path: Optional[str] = None

        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue
            for root, dirs, files in os.walk(base_path):
                dirs[:] = [d for d in dirs if d not in ('.git', '.venv', '__pycache__', 'node_modules')]
                for f in files:
                    if clean_name in f.lower() and (f.endswith(".lnk") or f.endswith(".exe")):
                        found_path = os.path.join(root, f)
                        break
                if found_path:
                    break
            if found_path:
                break

        if found_path:
            try:
                os.startfile(found_path)
                return {"status": "LAUNCHED_DESKTOP", "target": clean_name, "path": found_path, "app_name": clean_name.title()}
            except Exception as e:
                logger.warning(f"Could not open file {found_path}: {e}")

        # 3. Fallback: Common Web Applications
        web_apps = {
            "youtube": "https://www.youtube.com",
            "u tube": "https://www.youtube.com",
            "instagram": "https://www.instagram.com",
            "insta": "https://www.instagram.com",
            "whatsapp": "https://web.whatsapp.com",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "google": "https://www.google.com",
            "twitter": "https://twitter.com",
            "x": "https://x.com",
            "chatgpt": "https://chatgpt.com",
            "facebook": "https://www.facebook.com",
            "reddit": "https://www.reddit.com",
            "linkedin": "https://www.linkedin.com",
            "netflix": "https://www.netflix.com",
        }

        for key, url in web_apps.items():
            if key in clean_name:
                webbrowser.open(url)
                return {"status": "LAUNCHED_WEB", "target": key, "url": url, "app_name": key.title()}


        if found_path:
            try:
                os.startfile(found_path)
                return {"status": "LAUNCHED_LOCAL", "target": clean_name, "path": found_path}
            except Exception:
                pass

        # Fallback to direct Web URL opening
        target_url = f"https://www.{clean_name}.com" if not clean_name.startswith("http") else clean_name
        try:
            webbrowser.open(target_url)
            return {"status": "LAUNCHED_WEB_DIRECT", "target": clean_name, "url": target_url}
        except Exception:
            search_url = f"https://www.google.com/search?q={clean_name}"
            webbrowser.open(search_url)
            return {"status": "SEARCHED_WEB", "target": clean_name, "url": search_url}

    def _decompose_multitask(self, raw_text: str) -> List[str]:
        """Decompose compound multi-intent requests into discrete, ordered tasks."""
        split_pattern = r'\s+(?:also|and also|and then|and additionally|additionally|plus|;)\s+'
        parts = [p.strip() for p in re.split(split_pattern, raw_text, flags=re.IGNORECASE) if p.strip()]

        final_tasks = []
        for part in parts:
            # Check for "open X and (send|say|tell|text|message|play|explain|type|book|search|find) Y"
            multi_verb_match = re.match(
                r'^(open\s+[\w\s]+?)\s+and\s+((?:send|sent|say|tell|text|message|play|explain|type|book|search|find|create|clean|fix|write)\b.+)$',
                part,
                re.IGNORECASE
            )
            if multi_verb_match:
                final_tasks.append(multi_verb_match.group(1).strip())
                final_tasks.append(multi_verb_match.group(2).strip())
            else:
                final_tasks.append(part)

        return final_tasks

    def execute_voice_command(self, raw_text: str, persona: str = "ALFRED") -> Dict[str, Any]:
        """Dynamically execute real work automation tasks with multi-tasking and robust intent parsing."""
        salutation = "Sir" if persona == "ALFRED" else "Boss"
        sub_tasks = self._decompose_multitask(raw_text)

        # If compound multi-task detected, execute each task in sequence
        if len(sub_tasks) > 1:
            responses = []
            details_list = []
            for idx, task_str in enumerate(sub_tasks, 1):
                sub_res = self._execute_single_voice_command(task_str, persona=persona)
                details_list.append(sub_res)
                resp_text = sub_res.get("response", "").strip()
                if resp_text:
                    responses.append(f"{idx}. {resp_text}")

            combined_response = f"Multitasking {len(sub_tasks)} tasks for you, {salutation}:\n" + "\n".join(responses)
            return {
                "action": "multitask",
                "response": combined_response,
                "sub_tasks": sub_tasks,
                "details": details_list,
            }

        return self._execute_single_voice_command(raw_text, persona=persona)

    def _execute_single_voice_command(self, raw_text: str, persona: str = "ALFRED") -> Dict[str, Any]:
        """Execute a single focused command intent through unified AlfredOrganism ReAct intelligence."""
        import re
        import asyncio
        salutation = "Sir" if persona == "ALFRED" else "Boss"
        clean_text = re.sub(r'[^\w\s]', '', raw_text.lower()).strip()

        # 0. Sub-millisecond direct clock fast-path
        if clean_text in ("what time is it", "what is the time", "current time", "tell me the time", "time"):
            import datetime
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            return {
                "action": "speak",
                "response": f"The current time is {time_str} on {date_str}, {salutation}.",
            }

        # 1. Full Agentic ReAct Execution via Living Organism (replaces all static if-statement keyword traps)
        try:
            from jarvisx.organism import get_organism
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    res = pool.submit(lambda: asyncio.run(get_organism().react_turn(raw_text))).result(timeout=35)
            else:
                res = asyncio.run(get_organism().react_turn(raw_text))

            action_type = res.get("decision", "speak")
            if res.get("tool"):
                action_type = res.get("tool")

            return {
                "action": action_type,
                "response": res.get("response") or res.get("spoken") or "Mission completed.",
                "details": res,
            }
        except Exception as e:
            return self.execute_llm_request(raw_text, persona=persona)

    def execute_mission(
        self,
        goal: str,
        persona: str = "ALFRED",
        interactive: bool = True,
        max_steps: int = 10,
        max_replans: int = 2,
    ) -> Dict[str, Any]:
        """Execute complex multi-step goal through UnifiedMissionPlanner."""
        from jarvisx.missions.unified_mission_planner import UnifiedMissionPlanner
        planner = UnifiedMissionPlanner(llm_router=self.llm_router, memory_engine=self.memory_engine)
        return planner.execute_mission(
            goal=goal,
            persona=persona,
            interactive=interactive,
            max_steps=max_steps,
            max_replans=max_replans,
        )

    def execute_llm_request(
        self,
        raw_text: str,
        persona: str = "ALFRED",
        interactive: bool = True,
        max_tool_steps: int = 5,
    ) -> Dict[str, Any]:
        """Execute request through LLMRouter with bounded multi-step structured tool kernel execution."""
        salutation = "Sir" if persona == "ALFRED" else "Boss"
        print(f"[VOICE] Routing general request to LLMRouter: '{raw_text}'")
        try:
            import json
            from jarvisx.tools.tool_executor import ToolExecutor
            from jarvisx.tools.tool_kernel import ToolRegistry
            from jarvisx.tools.builtin_tools import register_builtin_tools

            # Bootstrap tool registry (idempotent)
            registry = ToolRegistry.get_instance()
            if not registry.list_tools():
                register_builtin_tools(registry)

            executor = ToolExecutor(registry=registry)
            tool_system_prompt = executor.build_tool_system_prompt()

            # Retrieve relevant long-term memory
            memory_block = ""
            if self.memory_engine:
                try:
                    pcontext = self.memory_engine.get_personal_context(query=raw_text)
                    if pcontext and pcontext.prompt_block:
                        memory_block = (
                            f"\n\n{pcontext.prompt_block}\n"
                            f"*(Note: Retrieved memory is background context. Prioritize explicit instructions in the current user request if they contradict prior preferences.)*"
                        )
                except Exception as me:
                    print(f"[MEMORY] Context retrieval warning: {me}")

            executed_steps: List[Dict[str, Any]] = []
            current_prompt = f"{tool_system_prompt}{memory_block}\n\nUser request: {raw_text}"
            last_tool_result: Optional[Dict[str, Any]] = None
            last_tool_name: Optional[str] = None
            history_str = ""

            for step_idx in range(max_tool_steps + 1):
                llm_res = self.llm_router.route_request_sync(prompt=current_prompt)
                out = llm_res.get("result", {})
                response = out.get("response", "")

                if not response or out.get("status") != "AVAILABLE" or llm_res.get("status") == "provider_unavailable":
                    if executed_steps:
                        response = f"Tool execution completed with {len(executed_steps)} step(s), {salutation}."
                        self._persist_turn_memory(raw_text)
                        return {
                            "action": "tool_call",
                            "response": response,
                            "tool": last_tool_name,
                            "tool_result": last_tool_result,
                            "execution_steps": executed_steps,
                            "text": raw_text,
                        }
                    else:
                        response = f"I am unable to reach the LLM provider at this time, {salutation}."
                        return {"action": "llm", "response": response, "text": raw_text, "details": llm_res}

                tool_call = executor.parse_tool_call(response)

                # Case 1: Normal conversational response (no tool requested)
                if not tool_call:
                    self._persist_turn_memory(raw_text)
                    if not executed_steps:
                        return {"action": "llm", "response": response, "text": raw_text, "details": llm_res}
                    else:
                        # LLM has provided the final summary after tools completed
                        return {
                            "action": "tool_call",
                            "response": response,
                            "tool": last_tool_name,
                            "tool_result": last_tool_result,
                            "execution_steps": executed_steps,
                            "text": raw_text,
                        }

                # Case 2: LLM requested a tool
                # Check max step guard: if already executed max_tool_steps, reject further tool calls
                if len(executed_steps) >= max_tool_steps:
                    print(f"[TOOL] Max tool steps ({max_tool_steps}) reached. Aborting further tool calls.")
                    err_msg = f"Maximum tool execution limit ({max_tool_steps} steps) reached."
                    response = f"Reached maximum action limit of {max_tool_steps} steps, {salutation}."
                    self._persist_turn_memory(raw_text)
                    return {
                        "action": "tool_call",
                        "response": response,
                        "tool": tool_call.get("tool"),
                        "tool_result": {"status": "failed", "tool": tool_call.get("tool"), "error": err_msg, "verified": False},
                        "execution_steps": executed_steps,
                        "error": err_msg,
                        "text": raw_text,
                    }

                tool_name = tool_call["tool"]
                tool_args = tool_call.get("arguments", {})
                last_tool_name = tool_name
                print(f"[TOOL] Step {len(executed_steps) + 1}/{max_tool_steps}: Requested '{tool_name}' with args {tool_args}")

                tool_result = executor.execute(tool_name, tool_args, interactive=interactive)
                last_tool_result = tool_result.to_dict()
                print(f"[TOOL] Step {len(executed_steps) + 1} Result: status={tool_result.status}, verified={tool_result.verified}")

                step_record = {
                    "step": len(executed_steps) + 1,
                    "tool": tool_name,
                    "arguments": tool_args,
                    "result": last_tool_result,
                    "status": tool_result.status,
                    "verified": tool_result.verified,
                    "error": tool_result.error,
                }
                executed_steps.append(step_record)

                # Check if tool execution or verification failed / was denied
                if tool_result.status != "success" or not tool_result.verified:
                    err_detail = tool_result.error or "Tool verification failed"
                    response = f"Tool {tool_name} failed: {err_detail}, {salutation}."
                    self._persist_turn_memory(raw_text)
                    return {
                        "action": "tool_call",
                        "response": response,
                        "tool": tool_name,
                        "tool_result": last_tool_result,
                        "execution_steps": executed_steps,
                        "text": raw_text,
                    }

                # If successful and verified, build next prompt with execution history
                history_lines = []
                for s in executed_steps:
                    history_lines.append(
                        f"- Step {s['step']}: Tool '{s['tool']}' was called with {json.dumps(s['arguments'])} and returned:\n"
                        f"  Status: {s['result'].get('status')}\n"
                        f"  Verified: {s['result'].get('verified')}\n"
                        f"  Result: {json.dumps(s['result'].get('result'))}"
                    )
                history_str = "\n".join(history_lines)

                current_prompt = (
                    f"{tool_system_prompt}{memory_block}\n\n"
                    f"User request: {raw_text}\n\n"
                    f"Execution history so far:\n{history_str}\n\n"
                    f"Based on the tool results above, if you need another tool to complete the request, respond with a JSON tool call:\n"
                    f'{{"type": "tool_call", "tool": "<tool_name>", "arguments": {{<args>}}}}\n\n'
                    f"If you have enough information to fulfill the user's request, provide your final natural spoken answer. Address the user as '{salutation}'."
                )

            # If loop exited after max steps without final natural response, generate final synthesis
            summary_prompt = (
                f"The user asked: \"{raw_text}\"\n\n"
                f"Execution history:\n{history_str}\n\n"
                f"Provide a brief, natural spoken response summarizing the completed actions and findings. "
                f"Address the user as '{salutation}'."
            )
            try:
                summary_res = self.llm_router.route_request_sync(prompt=summary_prompt)
                summary_out = summary_res.get("result", {})
                summary_text = summary_out.get("response", "")
                if summary_text and summary_out.get("status") == "AVAILABLE":
                    response = summary_text
                else:
                    response = f"Executed {len(executed_steps)} tool step(s) successfully, {salutation}."
            except Exception:
                response = f"Executed {len(executed_steps)} tool step(s) successfully, {salutation}."

            self._persist_turn_memory(raw_text)
            return {
                "action": "tool_call",
                "response": response,
                "tool": last_tool_name,
                "tool_result": last_tool_result,
                "execution_steps": executed_steps,
                "text": raw_text,
            }

        except Exception as e:
            err_resp = f"LLM Routing Error: {str(e)}"
            return {"action": "llm", "response": err_resp, "error": str(e), "text": raw_text}

    def _persist_turn_memory(self, raw_text: str):
        """Persist non-trivial facts, goals, and preferences from user turn into long-term memory."""
        if self.memory_engine:
            try:
                self.memory_engine.extract_and_store_from_conversation(text=raw_text)
            except Exception as me:
                print(f"[MEMORY] Memory persistence warning: {me}")

    # =========================================================================
    # SPRINT 1-4 GRAND UNIFICATION: SEMANTIC CLASSIFIER & MASTER ORCHESTRATION
    # =========================================================================

    @property
    def voice_engine(self):
        if not hasattr(self, "_voice_engine") or self._voice_engine is None:
            from jarvisx.interface.voice_duplex_engine import VoiceDuplexEngine
            self._voice_engine = VoiceDuplexEngine()
        return self._voice_engine

    @property
    def mesh_router(self):
        if not hasattr(self, "_mesh_router") or self._mesh_router is None:
            from jarvisx.mesh.mesh_router import MeshRouter
            self._mesh_router = MeshRouter()
        return self._mesh_router

    @property
    def vision_bridge(self):
        if not hasattr(self, "_vision_bridge") or self._vision_bridge is None:
            from jarvisx.automation.vision_mcp_bridge import VisionActuationBridge
            self._vision_bridge = VisionActuationBridge()
        return self._vision_bridge

    @property
    def web_researcher(self):
        if not hasattr(self, "_web_researcher") or self._web_researcher is None:
            from jarvisx.automation.real_web_navigator import AutonomousWebResearcher
            self._web_researcher = AutonomousWebResearcher()
        return self._web_researcher

    def _classify_intent(self, user_prompt: str, node_ip: str = "http://localhost:11434", model: str = "qwen2.5-coder:1.5b") -> str:
        """Semantically classifies user's prompt into VISUAL_ACTUATION, WEB_RESEARCH, or KNOWLEDGE_RAG."""
        print(f"[*] Semantic Intent Classification for: '{user_prompt}'")
        
        system_instruction = (
            "You are the routing brain for an AI agent. Classify the user's prompt into EXACTLY ONE of these categories:\n"
            "1. VISUAL_ACTUATION: The user wants to click something, type on the local screen, or wants you to look at their screen.\n"
            "2. WEB_RESEARCH: The user wants to search the internet, navigate to a website, or scrape web data.\n"
            "3. KNOWLEDGE_RAG: The user is asking a general question, wants coding help, or is making conversation.\n\n"
            "Output ONLY the category name. Do not explain your reasoning."
        )

        try:
            import urllib.request
            import json
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }
            req = urllib.request.Request(
                f"{node_ip}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                category = res_data.get("message", {}).get("content", "").strip().upper()
                if category in ["VISUAL_ACTUATION", "WEB_RESEARCH", "KNOWLEDGE_RAG"]:
                    return category
        except Exception:
            pass

        # Deterministic heuristic fallback
    @property
    def mission_planner(self):
        if not hasattr(self, "_mission_planner") or self._mission_planner is None:
            from jarvisx.missions.unified_mission_planner import UnifiedMissionPlanner
            from jarvisx.tools.tool_kernel import ToolRegistry
            from jarvisx.tools.builtin_tools import register_builtin_tools
            reg = ToolRegistry.get_instance()
            register_builtin_tools(reg)
            self._mission_planner = UnifiedMissionPlanner(tool_registry=reg)
        return self._mission_planner

    async def execute_llm_react_turn_async(self, prompt: str, persona: str = "ALFRED") -> Dict[str, Any]:
        """
        Pure Autonomous LLM ReAct Reasoning & Execution Engine:
        1. Queries real tool definitions from ToolRegistry.
        2. LLM reasons on the user's intent and dynamically decides to call a tool or chat.
        3. If tool call is generated, executes the tool sandbox and returns real results to LLM.
        4. LLM synthesizes natural, charismatic, British butler spoken response.
        """
        import json
        import re
        import logging
        logger = logging.getLogger("jarvisx.orchestrator.react")
        salutation = "Sir" if persona == "ALFRED" else "Boss"

        from jarvisx.tools.tool_kernel import ToolRegistry
        from jarvisx.tools.builtin_tools import register_builtin_tools
        from jarvisx.tools.tool_executor import ToolExecutor
        from jarvisx.llm.llm_router import LLMRouter

        reg = ToolRegistry.get_instance()
        register_builtin_tools(reg)
        executor = ToolExecutor(registry=reg)
        router = LLMRouter()

        tools_schemas = reg.get_schemas_for_llm()
        tools_summary = "\n".join([f"- {s['name']}: {s['description']}" for s in tools_schemas])

        system_prompt = f"""You are Alfred, Charan's sovereign AI operating system and intelligent British butler.
Address Charan respectfully as '{salutation}'.

Available Local OS Tools:
{tools_summary}

User Directive: "{prompt}"

Decision Rules:
1. If the user wants to execute an action (e.g. open an application, create an AI agent, list agents, check system info/time, read/write files, search web, control game/cooling), generate a tool call:
   {{"action": "tool_call", "tool": "<tool_name>", "args": {{...}}}}
2. If the user is asking a conversational question, inquiring about a topic (e.g. Nepal, coding, history, science), or chatting, respond directly:
   {{"action": "speak", "response": "<concise, intelligent, charismatic British butler response>"}}

Respond ONLY with valid JSON.
"""

        print(f"\n[*] 🧠 PURE LLM REACT INFERENCE ON: '{prompt}'")
        res = await router.route_request(system_prompt, require_offline=False)
        raw = res.get("result", {}).get("response", "").strip()

        # Parse JSON decision robustly
        decision = None
        import re
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                decision = json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"JSON parse error on LLM output: {e}")

        if not decision or not isinstance(decision, dict):
            # If plain text returned, use it directly as speech
            clean_speech = raw.replace("```json", "").replace("```", "").strip()
            return {"status": "success", "action": "speak", "response": clean_speech or f"Standing by for your command, {salutation}."}


        # Detect Tool Call from LLM Decision (Supports both tool_call action and direct tool action)
        tool_name = None
        tool_args = {}

        if decision.get("action") == "tool_call" and decision.get("tool"):
            tool_name = decision.get("tool")
            tool_args = decision.get("args", {})
        elif decision.get("tool") and decision.get("tool") not in ("speak", "chat", "none"):
            tool_name = decision.get("tool")
            tool_args = decision.get("args", decision)
        elif decision.get("action") and decision.get("action") not in ("speak", "message", "chat", "none", "unknown"):
            tool_name = decision.get("action")
            tool_args = {k: v for k, v in decision.items() if k != "action"}

        # Handle Autonomous Tool Call Execution
        if tool_name and reg.get(tool_name):
            print(f"    [+] Autonomous Tool Decided by LLM: '{tool_name}' with args {tool_args}")
            tool_res = executor.execute(tool_name, tool_args)
            
            # Pass output back to LLM for charismatic synthesis
            synthesis_prompt = f"""You are Alfred, Charan's witty, charismatic British AI butler.
You just executed the tool '{tool_name}' with arguments {json.dumps(tool_args)} for the goal: "{prompt}".
Tool Output: {json.dumps(tool_res.to_dict(), indent=2)}

Speak conversationally and charismatically to {salutation} in 1 to 2 sentences about the completed action.
Do NOT mention JSON schemas, validation codes, or raw tool logs.
"""
            synth_res = await router.route_request(synthesis_prompt, require_offline=False)
            spoken = synth_res.get("result", {}).get("response", "").strip()
            if not spoken:
                spoken = f"I have taken care of that for you, {salutation}."

            return {
                "status": "success",
                "action": "tool_call",
                "tool": tool_name,
                "tool_result": tool_res.to_dict(),
                "response": spoken
            }

        # Handle Direct Conversational Speech

        if decision.get("action") == "speak" and decision.get("response"):
            return {
                "status": "success",
                "action": "speak",
                "response": decision.get("response")
            }

        return {"status": "success", "action": "speak", "response": raw}

    async def _execute_subsystem(self, category: str, prompt: str) -> Dict[str, Any]:
        """
        Pure Autonomous LLM Multi-Agent Reasoning Engine.
        Executes single-turn and multi-step directives through genuine LLM reasoning and ToolExecutor.
        """
        prompt_clean = prompt.strip()
        if not prompt_clean:
            return {"status": "success", "response": "Standing by, Sir."}

        # 1. Pure LLM ReAct Turn (Autonomous Tool Selection + Conversational Speech)
        react_res = await self.execute_llm_react_turn_async(prompt_clean, persona="ALFRED")
        resp_text = react_res.get("response", "Mission completed.")
        try:
            self.voice_engine.speak(resp_text)
        except Exception:
            pass

        print(f"\n[JARVIS X]: {resp_text}")
        return react_res





    async def run_continuous_loop_async(self):
        """The Master Async Control Loop. Listens endlessly for voice/text input and orchestrates via LLM."""
        self.voice_engine.speak("All systems initialized. Jarvis X is online and listening.")
        
        while True:
            try:
                user_input = self.voice_engine.listen_and_transcribe()
                if not user_input:
                    continue
                if user_input.lower() in ["shut down", "go to sleep", "exit", "stop", "quit"]:
                    self.voice_engine.speak("Shutting down core processes. Goodbye.")
                    break

                # Route directly through LLM Autonomous Tool Calling
                await self._execute_subsystem("AGENT", user_input)
            except Exception as e:
                print(f"[!] Orchestrator Error: {e}")
                self.voice_engine.speak("I encountered an error processing that request.")
                await asyncio.sleep(1)


    def run_continuous_loop(self):
        """Synchronous wrapper for run_continuous_loop_async."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If already inside an event loop, run task in executor or create task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(lambda: asyncio.run(self.run_continuous_loop_async())).result()
        else:
            asyncio.run(self.run_continuous_loop_async())


def main():
    orchestrator = DynamicOrchestrator()
    orchestrator.run_continuous_loop()


if __name__ == "__main__":
    main()






