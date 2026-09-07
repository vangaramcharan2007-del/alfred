"""Autonomous Web Researcher & ReAct Navigation Loop for Jarvis X.

Connects to the Playwright MCP Server via standard MCP JSON-RPC stdio, exposes DOM
and navigation tools to the LLM (e.g. Qwen / DeepSeek on the Mesh Cluster), and orchestrates
the autonomous multi-turn Reason-Act-Observe research loop.
"""

from __future__ import annotations
import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import urllib.request

try:
    import ollama
except Exception:
    ollama = None

from jarvisx.mcp.playwright_server import get_playwright_engine, PlaywrightSessionEngine

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_NODE_IP = "http://100.77.90.36:11434"
DEFAULT_MODEL = "qwen2.5-coder:1.5b"


class AutonomousWebResearcher:
    """Orchestrates autonomous multi-turn web navigation and information extraction."""

    def __init__(
        self,
        target_model: str = DEFAULT_MODEL,
        node_ip: str = DEFAULT_NODE_IP,
        max_iterations: int = 5
    ):
        self.model = target_model
        self.node_ip = node_ip
        self.max_iterations = max_iterations
        self.engine = get_playwright_engine()

        # Tool specifications for LLM function calling schema
        self.llm_tools = [
            {
                "type": "function",
                "function": {
                    "name": "browser_navigate",
                    "description": "Navigates the browser to a specific URL and returns the page title. Always do this first.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The target website URL."}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "browser_extract_text",
                    "description": "Extracts clean, readable text from a CSS selector. Use 'body' for the whole page or 'h1', 'p', 'article' for sections.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string", "description": "CSS selector to extract text from.", "default": "body"}
                        },
                        "required": ["selector"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "browser_evaluate_js",
                    "description": "Executes JavaScript in the browser context to inspect DOM properties or count elements.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "script": {"type": "string", "description": "JavaScript code to evaluate."}
                        },
                        "required": ["script"]
                    }
                }
            }
        ]

    async def execute_tool_locally(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool directly via PlaywrightSessionEngine."""
        try:
            if tool_name == "browser_navigate":
                res = await self.engine.navigate(arguments.get("url", ""))
                return res.get("message", json.dumps(res))
            elif tool_name == "browser_extract_text":
                res = await self.engine.extract_text(arguments.get("selector", "body"))
                return res.get("text", json.dumps(res))
            elif tool_name == "browser_click":
                res = await self.engine.click(arguments.get("selector", ""))
                return res.get("message", json.dumps(res))
            elif tool_name == "browser_type":
                res = await self.engine.type_text(arguments.get("selector", ""), arguments.get("text", ""))
                return res.get("message", json.dumps(res))
            elif tool_name == "browser_evaluate_js":
                res = await self.engine.evaluate_js(arguments.get("script", ""))
                return str(res.get("result", json.dumps(res)))
            else:
                return f"Error: Unknown tool '{tool_name}'"
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    async def run_research_task(self, research_goal: str) -> Dict[str, Any]:
        """Runs the ReAct autonomous loop to complete the research goal."""
        print(f"\n========================================================")
        print(f"  🌐 JARVIS X: AUTONOMOUS WEB RESEARCHER (ReAct Loop)")
        print(f"========================================================")
        print(f"  Research Goal : '{research_goal}'")
        print(f"  Target Engine : {self.model} @ {self.node_ip}")
        print(f"  Max Iterations: {self.max_iterations}")
        print(f"========================================================\n")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are NANI, an autonomous web researcher. Use the provided tools to navigate the web, "
                    "read DOM text, and answer the user's prompt. When you have sufficient information to answer "
                    "the goal, write a comprehensive, clean markdown summary without calling any more tools."
                )
            },
            {"role": "user", "content": research_goal}
        ]

        remote_client = ollama.Client(host=self.node_ip)
        actions_taken = []
        final_synthesis = ""

        for iteration in range(self.max_iterations):
            print(f"[*] NANI: Thinking & Planning... (Iteration {iteration + 1}/{self.max_iterations})")

            try:
                response = remote_client.chat(
                    model=self.model,
                    messages=messages,
                    tools=self.llm_tools
                )
            except Exception as e:
                print(f"  ⚠️ Remote cluster notice: {e}. Executing direct web inspection fallback...")
                # Direct fallback navigation
                if "wikipedia" in research_goal.lower() or "http" in research_goal:
                    url = [w for w in research_goal.split() if "http" in w or "wiki" in w][0].strip("'\",")
                    if not url.startswith("http"):
                        url = f"https://{url}"
                    print(f"  -> Direct Navigation to: {url}")
                    nav_msg = await self.execute_tool_locally("browser_navigate", {"url": url})
                    text = await self.execute_tool_locally("browser_extract_text", {"selector": "body"})
                    final_synthesis = f"### Autonomous Web Synthesis\n\n**Source:** {url}\n\n**Extracted Content:**\n{text[:1500]}..."
                    break
                else:
                    final_synthesis = f"Research loop error: {str(e)}"
                    break

            message = response.get("message", {})
            messages.append(message)

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                # LLM synthesized final response
                final_synthesis = message.get("content", "")
                print("\n========================================================")
                print("  ✅ FINAL RESEARCH SYNTHESIS")
                print("========================================================")
                print(final_synthesis)
                break

            # Execute tool calls
            for tc in tool_calls:
                fn = tc.get("function", {})
                tool_name = fn.get("name")
                tool_args = fn.get("arguments", {})

                print(f"  👉 [ACTION]: {tool_name}({tool_args})")
                tool_result_text = await self.execute_tool_locally(tool_name, tool_args)
                print(f"  👀 [OBSERVATION]: {tool_result_text[:120]}...\n")

                actions_taken.append({
                    "iteration": iteration + 1,
                    "tool": tool_name,
                    "args": tool_args,
                    "result_snippet": tool_result_text[:200]
                })

                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": tool_result_text
                })

        return {
            "status": "success",
            "goal": research_goal,
            "iterations_used": len(actions_taken) + 1,
            "actions": actions_taken,
            "synthesis": final_synthesis
        }


RealWebNavigator = AutonomousWebResearcher


def get_web_researcher() -> AutonomousWebResearcher:
    """Singleton getter for AutonomousWebResearcher."""
    return AutonomousWebResearcher()


if __name__ == "__main__":
    researcher = AutonomousWebResearcher()
    task = "Navigate to 'https://example.com' and extract the heading text and explanation."
    asyncio.run(researcher.run_research_task(task))
