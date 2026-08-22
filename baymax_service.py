"""
AEGIS Baymax Service - Pure Ollama Local Model Inference
Routes raw live biometrics and user inquiries directly to Ollama.
Zero canned responses or heuristic fallbacks.
"""

import sys
from typing import Dict, Any, Optional, AsyncGenerator
import ollama
from fastapi.responses import StreamingResponse

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async_client = ollama.AsyncClient()


async def stream_baymax_reasoning(
    user_query: str,
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    model: str = "aegis-baymax"
) -> AsyncGenerator[str, None]:
    """
    Sends raw live biometrics and user query directly to Ollama.
    Zero canned responses or heuristic fallbacks.
    """
    system_prompt = (
        "You are Baymax, an offline personal healthcare companion. "
        "Analyze the user's inquiry strictly in the context of their real-time biometric readings. "
        "Be empathetic, calm, and clinically concise (2 to 3 sentences maximum). "
        "Do not diagnose severe conditions; provide actionable self-care or escalation guidance."
    )

    user_context = (
        f"User Inquiry: '{user_query}'\n"
        f"Live Biometrics: Heart Rate={vitals.get('heart_rate')} BPM, "
        f"Core Temp={vitals.get('temperature')}°C, "
        f"Ocular EAR={vitals.get('ear')}, "
        f"HRV (RMSSD)={vitals.get('rmssd')}ms, "
        f"Galvanic Skin Response={vitals.get('eda')} uS.\n"
        f"5-Min Rolling Baseline: Avg HR={baseline.get('avg_hr')} BPM, "
        f"Avg EAR={baseline.get('avg_ear')}.\n"
        f"Provide your real-time assessment."
    )

    models_to_try = [model, "llama3.2:1b", "llama3", "tinyllama"]
    success = False
    last_err = ""

    for m in models_to_try:
        try:
            response_stream = await async_client.chat(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                stream=True
            )
            async for chunk in response_stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
            success = True
            break
        except Exception as e:
            last_err = str(e)
            continue

    if not success:
        yield f"Error communicating with local Ollama core: {last_err}. Please ensure 'ollama serve' is running."


async def generate_baymax_reply_text(
    user_query: str,
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    model: str = "aegis-baymax"
) -> str:
    """
    Non-streaming one-shot caller for JSON endpoint responses.
    """
    reply_parts = []
    async for chunk in stream_baymax_reasoning(user_query, vitals, baseline, model):
        reply_parts.append(chunk)
    return "".join(reply_parts)


async def generate_explanation(hr: int, temp: float, risk_score: str) -> StreamingResponse:
    """
    Legacy streaming endpoint adapter.
    """
    vitals = {"heart_rate": hr, "temperature": temp, "ear": 0.30, "rmssd": 45, "eda": 1.5}
    baseline = {"avg_hr": hr, "avg_ear": 0.30}
    return StreamingResponse(
        stream_baymax_reasoning(
            user_query=f"Explain my current physiological risk score of {risk_score}.",
            vitals=vitals,
            baseline=baseline
        ),
        media_type="text/plain"
    )
