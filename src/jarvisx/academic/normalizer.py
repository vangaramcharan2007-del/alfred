"""Academic Task Normalizer & Urgency Classifier.

Parses raw communication bodies, calculates deadlines, assigns priority tiers,
and standardizes tasks into normalized AcademicTask instances.
"""

from __future__ import annotations
import re
import time
from typing import Any, Dict, List, Optional

from jarvisx.academic.models import (
    AcademicTask,
    ChannelSource,
    TaskPriority,
    TaskType,
)


class AssignmentNormalizer:
    """Normalizes raw unstructured notices into structured AcademicTask specifications."""

    @staticmethod
    def calculate_priority(deadline_epoch: float) -> TaskPriority:
        """Determines urgency tier based on hours remaining until deadline."""
        diff_hours = (deadline_epoch - time.time()) / 3600.0
        if diff_hours <= 12:
            return TaskPriority.EMERGENCY
        elif diff_hours <= 24:
            return TaskPriority.URGENT
        elif diff_hours <= 72:
            return TaskPriority.NORMAL
        else:
            return TaskPriority.LOW

    @classmethod
    def normalize_message(
        cls,
        channel: ChannelSource,
        sender: str,
        subject: str,
        body: str,
        task_id: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> AcademicTask:
        """Parses a communication event and generates a normalized AcademicTask."""
        # 1. Detect Course Code
        course_match = re.search(r'(21[A-Z]{2,4}\d{3}[A-Z]|NPTEL-[A-Z0-9]+|STEP-[A-Z]+)', subject + " " + body)
        course_code = course_match.group(1) if course_match else "ACAD2026"

        # 2. Extract Deadline
        now = time.time()
        deadline_epoch = now + 86400  # Default 24 hours
        if re.search(r'(today|tonight|by 11:59 pm|by 5 pm today)', body, re.IGNORECASE):
            deadline_epoch = now + 3600 * 6
        elif re.search(r'(tomorrow|within 24 hours|due tomorrow)', body, re.IGNORECASE):
            deadline_epoch = now + 3600 * 20
        elif re.search(r'(this friday|in 3 days|end of week)', body, re.IGNORECASE):
            deadline_epoch = now + 3600 * 72

        priority = cls.calculate_priority(deadline_epoch)

        # 3. Detect Task Type
        if "mcq" in body.lower() or "quiz" in body.lower():
            task_type = TaskType.MCQ_ASSESSMENT
        elif "nptel" in subject.lower() or channel == ChannelSource.NPTEL:
            task_type = TaskType.NPTEL_ASSIGNMENT
        elif "java" in subject.lower() or "java" in body.lower() or channel == ChannelSource.SRM_STEP_JAVA:
            task_type = TaskType.JAVA_CODING_CHALLENGE
        elif "project" in body.lower() or "code" in body.lower() or "implementation" in body.lower():
            task_type = TaskType.CODING_PROJECT
        else:
            task_type = TaskType.WORKSHEET

        # 4. Extract Questions/Prompt
        questions: List[Dict[str, Any]] = []
        raw_qs = re.findall(r'(?:Q\d+[:.]|Question \d+[:.]|\d+\.)\s*([^\n\r]+)', body)
        if raw_qs:
            for i, q in enumerate(raw_qs, 1):
                questions.append({"q_id": f"Q{i}", "text": q.strip()})
        else:
            questions.append({"q_id": "Q1", "text": body.strip()[:300]})

        clean_id = task_id or f"{channel.value}-{int(time.time() * 1000) % 100000}"

        return AcademicTask(
            task_id=clean_id,
            channel=channel,
            course_code=course_code,
            course_name=subject.strip(),
            title=subject.strip(),
            description=body.strip(),
            deadline_epoch=deadline_epoch,
            priority=priority,
            task_type=task_type,
            faculty_name=sender,
            questions=questions,
        )
