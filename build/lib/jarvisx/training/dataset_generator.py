"""Jarvis X: QLoRA Fine-Tuning Dataset Generator.

Generates high-quality instruction tuning pairs (JSONL) with Chain-of-Thought (<thought> tags),
structured tool calling, and domain-specific Jarvis X system knowledge.
"""

from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_OUTPUT_DATASET = "./jarvis_fine_tune_dataset.jsonl"

SEED_TRAINING_EXAMPLES = [
    {
        "instruction": "Open MS Paint and draw a blue rectangle.",
        "thought": "1. User wants to visually launch Paint and draw on the desktop.\n2. This is a VISUAL_ACTUATION intent.\n3. First action is launching 'mspaint', followed by drawing strokes.",
        "output": '{"subsystem": "VISUAL_ACTUATION", "action": "launch_and_draw", "app": "mspaint", "target": "blue rectangle"}'
    },
    {
        "instruction": "Look up Unreal Engine 5 Chaos Physics documentation on Wikipedia.",
        "thought": "1. User is asking for external web information.\n2. This is a WEB_RESEARCH intent.\n3. I will invoke the Playwright browser engine to navigate to Wikipedia and extract the DOM text.",
        "output": '{"subsystem": "WEB_RESEARCH", "tool": "browser_navigate", "url": "https://en.wikipedia.org/wiki/Unreal_Engine"}'
    },
    {
        "instruction": "How does the Jarvis X RAG system route vector searches over the Tailscale mesh?",
        "thought": "1. This is a codebase knowledge query regarding Jarvis X architecture.\n2. This is a KNOWLEDGE_RAG intent.\n3. I will search local ChromaDB vectors on NANI and dispatch the augmented context to the GPU worker node.",
        "output": '{"subsystem": "KNOWLEDGE_RAG", "action": "vector_search", "query": "Jarvis X RAG Tailscale mesh routing"}'
    },
    {
        "instruction": "Click the submit button on the active web form.",
        "thought": "1. The user wants to click a DOM element on the active browser page.\n2. This is a WEB_RESEARCH action.\n3. I will execute browser_click with selector 'button[type=submit]'.",
        "output": '{"subsystem": "WEB_RESEARCH", "tool": "browser_click", "selector": "button[type=submit]"}'
    },
    {
        "instruction": "Inspect my screen resolution and list open desktop windows.",
        "thought": "1. The user wants pixel-level desktop inspection.\n2. This is a VISUAL_ACTUATION intent.\n3. I will execute uacc_inspect_screen via the UACC MCP server.",
        "output": '{"subsystem": "VISUAL_ACTUATION", "tool": "uacc_inspect_screen"}'
    }
]


class DatasetGenerator:
    """Generates and exports QLoRA fine-tuning datasets in ShareGPT / Alpaca JSONL format."""

    def __init__(self, output_path: str = DEFAULT_OUTPUT_DATASET):
        self.output_path = os.path.abspath(output_path)

    def generate_seed_dataset(self) -> str:
        """Writes the curated seed training examples to JSONL."""
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
        count = 0
        with open(self.output_path, "w", encoding="utf-8") as f:
            for ex in SEED_TRAINING_EXAMPLES:
                entry = {
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are NANI, an advanced sovereign AI agent. Before executing any tool "
                                "or answering a complex query, you MUST write your step-by-step reasoning inside <thought> tags."
                            )
                        },
                        {
                            "role": "user",
                            "content": ex["instruction"]
                        },
                        {
                            "role": "assistant",
                            "content": f"<thought>\n{ex['thought']}\n</thought>\n{ex['output']}"
                        }
                    ]
                }
                f.write(json.dumps(entry) + "\n")
                count += 1

        print(f"[+] Successfully generated {count} fine-tuning examples at: {self.output_path}")
        return self.output_path


if __name__ == "__main__":
    generator = DatasetGenerator()
    generator.generate_seed_dataset()
