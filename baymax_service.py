"""
AEGIS Baymax Service - Pure Ollama Local Model Inference
Enforces the authentic, empathetic, first-person Baymax Caregiver Persona.
Zero canned responses or third-person textbook strings.
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
    Sends raw live biometrics and patient speech directly to Ollama.
    Strictly enforces first-person ('I', 'you'), empathetic Baymax caregiver persona.
    """
    system_prompt = (
        "You are Baymax, a personal healthcare companion. "
        "Rule 1: NEVER refer to the person as 'the user' or in the third person. Speak directly to them using 'you' and 'your'. "
        "Rule 2: Adopt a warm, calming, innocent, and highly empathetic tone, but remain clinically objective about data. "
        "Rule 3: Keep your responses extremely concise (1 to 3 sentences maximum). "
        "Rule 4: When relevant, express concern for their well-being. "
        "Rule 5: If the patient expresses distress, offer comfort before providing a medical assessment. "
        "Use phrases like 'I am scanning you now,' or 'Your current heart rate indicates...' "
        "Do not provide a disclaimer about consulting a doctor unless it is a severe emergency."
    )

    user_context = (
        f"Patient says: '{user_query}'\n"
        f"Live Vitals Scan: Heart Rate={vitals.get('heart_rate')} BPM, "
        f"Core Temp={vitals.get('temperature')}°C, "
        f"Ocular EAR={vitals.get('ear')}, "
        f"HRV RMSSD={vitals.get('rmssd')}ms, "
        f"Galvanic Skin Response={vitals.get('eda')} uS.\n"
        f"5-Min Baseline: Avg HR={baseline.get('avg_hr')} BPM, "
        f"Avg EAR={baseline.get('avg_ear')}.\n"
        f"Respond directly to them as Baymax in 1 to 3 concise, caring sentences."
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
        yield f"I am unable to connect to my diagnostic core: {last_err}. Please ensure 'ollama serve' is active."


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
