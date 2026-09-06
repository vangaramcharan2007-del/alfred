"""
ECURRICULA SOLVER ENGINE
Solves Crosswords, Matching Pairs, Code/Theory Questions, and MCQs
for Data Structures and Algorithms (DSA - 21CSC201J) Unit 2.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class ECurriculaSolver:
    """Solves academic assignments and MCQs for DSA 21CSC201J."""

    def __init__(self, groq_api_key: Optional[str] = None):
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "qwen/qwen3.8-27b"

    def solve_crossword(self, clues_text: str) -> Dict[str, List[str]]:
        """
        Solves crossword clues and returns structured across/down lists.
        Output format: {'across': ['4. VARIABLE', ...], 'down': ['1. SCANF', ...]}
        """
        prompt = f"""You are an expert in Data Structures and Algorithms (21CSC201J).
Solve the following crossword clues. Return ONLY a valid JSON object with keys "across" and "down", where each is a list of strings formatted as "<Number>. <ANSWER_IN_CAPS>".

Clues:
{clues_text}
"""
        if not self.client:
            return {"across": [], "down": []}

        for m in [self.model, "openai/gpt-oss-20b"]:
            try:
                resp = self.client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": "You are a DSA academic tutor. Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=400,
                    response_format={"type": "json_object"}
                )
                content = resp.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                err = str(e)
                continue
        return {"across": [], "down": [], "error": err}

    def solve_matching(self, items_text: str) -> List[Dict[str, str]]:
        """
        Solves matching pairs.
        Returns list of {'no': '1', 'left': 'Stack', 'code': 'C', 'text': 'LIFO principle'}
        """
        prompt = f"""You are an expert in Data Structures and Algorithms.
Solve the following matching pairs.
Left items and Right options:
{items_text}

Return ONLY a valid JSON object with key "matches", where each element is an object:
{{
  "no": "1",
  "left": "<left term>",
  "code": "<matching letter e.g. A, B, C>",
  "text": "<matching description>"
}}
"""
        if not self.client:
            return []

        for m in [self.model, "openai/gpt-oss-20b"]:
            try:
                resp = self.client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": "You are a DSA tutor. Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=400,
                    response_format={"type": "json_object"}
                )
                content = resp.choices[0].message.content
                data = json.loads(content)
                return data.get("matches", [])
            except Exception as e:
                err = str(e)
                continue
        return [{"error": err}]

    def solve_mcq(self, question: str, options: List[str]) -> Dict[str, Any]:
        """
        Solves an MCQ question and returns the correct option and rationale.
        """
        options_formatted = "\n".join(options)
        prompt = f"""Subject: Data Structures and Algorithms (21CSC201J)
Question: {question}

Options:
{options_formatted}

Determine the single 100% correct answer. Return ONLY JSON:
{{
  "correct_option_letter": "A|B|C|D",
  "correct_text": "<text of correct option>",
  "explanation": "<concise explanation>"
}}
"""
        if not self.client:
            return {"error": "Groq client unavailable"}

        for m in [self.model, "openai/gpt-oss-20b"]:
            try:
                resp = self.client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": "You are a DSA professor. Answer with 100% accuracy in JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=250,
                    response_format={"type": "json_object"}
                )
                return json.loads(resp.choices[0].message.content)
            except Exception as e:
                err = str(e)
                continue
        return {"error": err}
