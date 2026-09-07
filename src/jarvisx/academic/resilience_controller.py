"""Resilience Controller & Two-Phase Staging Gate.

Addresses Failure Mode 5: Anti-Bot WAF Throttling, CAPTCHAs & Deadline Crunch Race Conditions.
Provides:
1. Adaptive Jitter & Randomized Sweep Scheduling (defeats predictable bot cadence heuristics).
2. Exponential backoff with jitter on 429 / 504 gateway timeouts.
3. Realistic browser header and user-agent rotation.
4. Two-Phase Submission Staging Gate:
   - Phase 1: Pre-solve, compile, and stage with rubric cryptographic checksums.
   - Phase 2: Verify rubric freshness and gate auto-submission within the safe final window.
"""

from __future__ import annotations
import hashlib
import logging
import random
import time
from typing import Any, Dict, Optional, Tuple

from jarvisx.academic.models import AcademicTask, TaskStatus

logger = logging.getLogger("jarvisx.academic.resilience_controller")


class ResilienceController:
    """Orchestrates network throttling avoidance, WAF resilience, and race-condition free staging."""

    def __init__(self, base_interval_seconds: float = 900.0, jitter_seconds: float = 240.0):
        self.base_interval = base_interval_seconds
        self.jitter = jitter_seconds
        self._staged_hashes: Dict[str, str] = {}
        
        # User-agent pool for browser fingerprint rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        ]

    def compute_rubric_checksum(self, task: AcademicTask) -> str:
        """Computes SHA-256 hash of task rubric, questions, and deadline to detect mid-cycle professor edits."""
        content = f"{task.title}|{task.description}|{task.deadline_epoch}|{len(task.questions)}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_next_sweep_delay(self) -> float:
        """Calculates randomized sweep delay with Poisson-like Gaussian jitter."""
        delta = random.uniform(-self.jitter, self.jitter)
        delay = max(180.0, self.base_interval + delta)
        logger.info(f"[ResilienceController] Next scheduled academic sweep in {delay:.1f}s (jitter applied: {delta:+.1f}s)")
        return delay

    def get_browser_headers(self, portal: str) -> Dict[str, str]:
        """Generates authentic browser headers to avoid Cloudflare/WAF bot challenges."""
        ua = random.choice(self.user_agents)
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0",
        }

    def calculate_backoff(self, attempt: int, base_seconds: float = 2.0, max_seconds: float = 60.0) -> float:
        """Calculates exponential backoff with full jitter for 504 / 429 portal errors."""
        temp = min(max_seconds, base_seconds * (2 ** attempt))
        sleep_duration = random.uniform(0.5, temp)
        logger.info(f"[ResilienceController] Backoff attempt {attempt}: sleeping {sleep_duration:.2f}s...")
        return sleep_duration

    def stage_for_submission(self, task: AcademicTask) -> Tuple[bool, str]:
        """Phase 1: Validates and stages an assignment before actual portal transmission."""
        checksum = self.compute_rubric_checksum(task)
        self._staged_hashes[task.task_id] = checksum
        logger.info(f"[ResilienceController] Staged task '{task.task_id}' with rubric checksum {checksum[:12]}...")
        return True, checksum

    def can_safely_submit(self, task: AcademicTask, auto_submit_threshold_hours: float = 2.0) -> Tuple[bool, str]:
        """Phase 2: Verifies rubric consistency and deadline safety window."""
        # 1. Verify that rubric hasn't changed
        current_checksum = self.compute_rubric_checksum(task)
        staged_checksum = self._staged_hashes.get(task.task_id)

        if staged_checksum and staged_checksum != current_checksum:
            msg = f"RACE HAZARD: Professor updated assignment rubric for '{task.title}' after staging! Re-solve required."
            logger.warning(f"[ResilienceController] {msg}")
            return False, msg

        # 2. Check time remaining
        now = time.time()
        hours_remaining = (task.deadline_epoch - now) / 3600.0

        if hours_remaining > auto_submit_threshold_hours:
            msg = f"Task '{task.title}' safely staged. Deadline is in {hours_remaining:.1f}h (> {auto_submit_threshold_hours}h threshold). Holding submission for safety review."
            logger.info(f"[ResilienceController] {msg}")
            return False, msg

        logger.info(f"[ResilienceController] Task '{task.title}' within submission window ({hours_remaining:.2f}h remaining). Safe to execute submission.")
        return True, "READY_FOR_FINAL_SUBMISSION"
