"""
Living Task Tree HUD & Ambient Harness Dashboard for Jarvis OS.
Renders an on-screen Devin/Manus-style hierarchical task tree, ambient context tracker,
and clipboard error interceptor.
"""

from __future__ import annotations

import asyncio
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.harness.active_context_sensor import ActiveWindowContextSensor, WindowContext
from jarvisx.harness.autonomous_reloop_engine import AutonomousReActHarness, LivingTaskTree
from jarvisx.harness.clipboard_sensor import AmbientClipboardSensor, ClipboardEvent


class LivingTaskTreeHUD:
    """The master Devin/Manus style hierarchical task tree & ambient harness HUD."""

    def __init__(self):
        self.context_sensor = ActiveWindowContextSensor()
        self.clipboard_sensor = AmbientClipboardSensor()
        self.reloop_harness = AutonomousReActHarness()

        # Connect event listeners
        self.context_sensor.add_listener(self._on_context_change)
        self.clipboard_sensor.add_listener(self._on_clipboard_event)
        self.reloop_harness.add_tree_listener(self._on_task_tree_update)

        self.context_sensor.start()
        self.clipboard_sensor.start()

        self.root = tk.Tk()
        self.root.title("JARVIS OS — SOVEREIGN AI HARNESS & LIVING TASK TREE")
        self.root.geometry("960x700+180+60")
        self.root.configure(bg="#080c14")

        self.last_clipboard_event: Optional[ClipboardEvent] = None
        self.current_context: Optional[WindowContext] = None

        self._build_ui()

    def _build_ui(self):
        # 1. Top Cybernetic Header
        header = tk.Frame(self.root, bg="#101726", padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="⚡ JARVIS OS — AUTONOMOUS AI HARNESS",
            font=("Segoe UI", 16, "bold"),
            fg="#00d2ff",
            bg="#101726"
        ).pack(side="left")

        self.badge_lbl = tk.Label(
            header,
            text="● AMBIENT HARNESS ACTIVE",
            font=("Consolas", 10, "bold"),
            fg="#00ff88",
            bg="#16233b",
            padx=10,
            pady=4,
            relief="groove"
        )
        self.badge_lbl.pack(side="right")

        # 2. Ambient Environmental Context Bar
        context_bar = tk.Frame(self.root, bg="#131d2e", padx=20, pady=8)
        context_bar.pack(fill="x")

        self.context_lbl = tk.Label(
            context_bar,
            text="🎯 Active Window Context: Detecting...",
            font=("Consolas", 10, "bold"),
            fg="#fbc531",
            bg="#131d2e"
        )
        self.context_lbl.pack(side="left")

        # 3. Ambient Clipboard Interceptor Banner
        self.clip_frame = tk.Frame(self.root, bg="#1a2538", padx=20, pady=8)
        self.clip_frame.pack(fill="x", pady=2)

        self.clip_lbl = tk.Label(
            self.clip_frame,
            text="📋 Clipboard Sensor: Listening for copied errors, URLs, and code...",
            font=("Consolas", 9),
            fg="#8fa3bf",
            bg="#1a2538"
        )
        self.clip_lbl.pack(side="left")

        # 4. Main Middle: Living Hierarchical Task Tree (Devin Style)
        tree_container = tk.Frame(self.root, bg="#080c14", padx=20, pady=10)
        tree_container.pack(fill="both", expand=True)

        tk.Label(
            tree_container,
            text="🌳 LIVING HIERARCHICAL TASK TREE (AUTONOMOUS REACT REPL)",
            font=("Segoe UI", 12, "bold"),
            fg="#70a1ff",
            bg="#080c14"
        ).pack(anchor="w", pady=(0, 6))

        # Task Tree Canvas / List
        self.tree_frame = tk.Frame(tree_container, bg="#0d1320", padx=15, pady=10, relief="ridge", bd=1)
        self.tree_frame.pack(fill="both", expand=True)

        self.mission_title_lbl = tk.Label(
            self.tree_frame,
            text="[No Active Mission — Standing by for autonomous goals]",
            font=("Segoe UI", 11, "italic"),
            fg="#718093",
            bg="#0d1320"
        )
        self.mission_title_lbl.pack(anchor="w", pady=(0, 10))

        self.nodes_frame = tk.Frame(self.tree_frame, bg="#0d1320")
        self.nodes_frame.pack(fill="both", expand=True)

        # 5. Bottom Interactive Command Dispatch
        bottom_f = tk.Frame(self.root, bg="#101726", padx=20, pady=12)
        bottom_f.pack(fill="x")

        tk.Label(bottom_f, text="⚡ Autonomous Macro Goal:", font=("Segoe UI", 10, "bold"), fg="#e0e0e0", bg="#101726").pack(side="left", padx=(0, 8))

        self.goal_entry = tk.Entry(bottom_f, font=("Segoe UI", 11), bg="#182338", fg="#ffffff", insertbackground="#00d2ff", relief="flat")
        self.goal_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.goal_entry.bind("<Return>", lambda e: self._dispatch_macro_goal())

        btn = tk.Button(
            bottom_f,
            text="EXECUTE HARNESS 🚀",
            font=("Segoe UI", 9, "bold"),
            bg="#00a8ff",
            fg="#ffffff",
            relief="flat",
            padx=14,
            command=self._dispatch_macro_goal
        )
        btn.pack(side="right")

    def _on_context_change(self, ctx: WindowContext):
        """Called when active window changes."""
        text = f"🎯 Focused App: {ctx.process_name} ({ctx.window_title[:35]}...) | Mode: [{ctx.context_mode}]"
        self.context_lbl.configure(text=text)

    def _on_clipboard_event(self, ev: ClipboardEvent):
        """Called when clipboard changes."""
        if ev.event_type == "PYTHON_ERROR":
            msg = f"🚨 INTERCEPTED PYTHON ERROR: {ev.parsed_metadata.get('error_summary')} in {ev.parsed_metadata.get('file_path')}"
            self.clip_lbl.configure(text=msg, fg="#ff4757", font=("Consolas", 9, "bold"))
        elif ev.event_type == "TERMINAL_COMMAND":
            msg = f"⚡ INTERCEPTED TERMINAL COMMAND: {ev.parsed_metadata.get('command')}"
            self.clip_lbl.configure(text=msg, fg="#00d2ff", font=("Consolas", 9))
        elif ev.event_type == "WEB_URL":
            msg = f"🌐 INTERCEPTED RESEARCH URL: {ev.parsed_metadata.get('url')}"
            self.clip_lbl.configure(text=msg, fg="#2ed573", font=("Consolas", 9))
        else:
            msg = f"📋 Clipboard Content: {ev.event_type} ({len(ev.content)} chars)"
            self.clip_lbl.configure(text=msg, fg="#a4b0be", font=("Consolas", 9))

    def _on_task_tree_update(self, tree: LivingTaskTree):
        """Renders the hierarchical task tree."""
        self.mission_title_lbl.configure(
            text=f"🎯 Active Mission: '{tree.goal}' | Status: [{tree.overall_status}]",
            fg="#00d2ff",
            font=("Segoe UI", 11, "bold")
        )

        # Clear existing nodes
        for widget in self.nodes_frame.winfo_children():
            widget.destroy()

        for idx, node in enumerate(tree.nodes):
            row = tk.Frame(self.nodes_frame, bg="#121a2b", padx=12, pady=6)
            row.pack(fill="x", pady=3)

            # Icon based on status
            if node.status == "COMPLETED":
                icon = "✔"
                color = "#00ff88"
            elif node.status == "RUNNING":
                icon = "⟳"
                color = "#fbc531"
            elif node.status == "RETRYING":
                icon = "⚡ Self-Healing..."
                color = "#ff6b81"
            elif node.status == "FAILED":
                icon = "✖"
                color = "#ff4757"
            else:
                icon = "○"
                color = "#718093"

            tk.Label(row, text=f"[{icon}]", font=("Consolas", 11, "bold"), fg=color, bg="#121a2b", width=14, anchor="w").pack(side="left")
            tk.Label(row, text=f"Step {idx+1}: {node.description}", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#121a2b").pack(side="left", padx=8)
            tk.Label(row, text=f"({node.assigned_agent} -> {node.tool})", font=("Consolas", 9), fg="#70a1ff", bg="#121a2b").pack(side="right")

    def _dispatch_macro_goal(self):
        goal = self.goal_entry.get().strip()
        if not goal:
            return
        self.goal_entry.delete(0, "end")

        def run_harness():
            asyncio.run(self.reloop_harness.execute_macro_goal_async(goal))

        threading.Thread(target=run_harness, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    hud = LivingTaskTreeHUD()
    hud.run()
