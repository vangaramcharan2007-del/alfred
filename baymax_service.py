"""
AEGIS Baymax Service - Localized LLM Advice Streaming Engine
Integrates with Ollama AsyncClient using the localized aegis-baymax model.
"""

import logging
from typing import AsyncGenerator
import ollama
from fastapi.responses import StreamingResponse

logger = logging.getLogger("baymax_service")


async def generate_explanation(hr: int, temp: float, risk_score: str) -> StreamingResponse:
    """
    Generate real-time streaming safety advice for physiological telemetry using Ollama.

    Args:
        hr: Heart rate in BPM
        temp: Body temperature in Celsius
        risk_score: Assessed risk level ("Normal" or "High")

    Returns:
        FastAPI StreamingResponse yielding tokens asynchronously.
    """
    prompt = (
        f"Physiological Telemetry -> Heart Rate: {hr} BPM, Body Temperature: {temp:.1f}°C, Risk Score: {risk_score}. "
        "Translate this physiological data into calm, actionable safety advice strictly under 2 sentences. Do not diagnose."
    )

    async def token_stream() -> AsyncGenerator[str, None]:
        try:
            client = ollama.AsyncClient()
            stream = await client.chat(
                model="aegis-baymax",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            async for chunk in stream:
                if isinstance(chunk, dict):
                    content = chunk.get("message", {}).get("content", "")
                elif hasattr(chunk, "message") and hasattr(chunk.message, "content"):
                    content = chunk.message.content
                else:
                    content = str(chunk)
                if content:
                    yield content
        except Exception as exc:
            logger.warning(
                "Ollama aegis-baymax offline or unreachable (%s). Emitting offline fallback advice.",
                exc
            )
            if str(risk_score).lower() == "high":
                yield (
                    "Critical physiological elevation detected. "
                    "Please rest immediately in a cool area, hydrate with water, and monitor your symptoms carefully."
                )
            else:
                yield (
                    "Vitals appear stable and within standard resting baseline. "
                    "Continue normal routine and maintain adequate hydration."
                )

    return StreamingResponse(token_stream(), media_type="text/plain")
