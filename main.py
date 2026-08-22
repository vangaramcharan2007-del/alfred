"""
AEGIS Health Companion - FastAPI Backend
Handles telemetry ingestion, anomaly evaluation via aegis_engine,
asynchronous escalation webhook dispatching, and localized LLM streaming via baymax_service.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from typing import Optional

import httpx
from fastapi import FastAPI, BackgroundTasks, status
from pydantic import BaseModel, Field

from aegis_engine import AnomalyDetector, EvaluationResult
from baymax_service import generate_explanation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aegis_backend")

WEBHOOK_URL = "http://localhost:5678/webhook/aegis-escalation"

# Global detector instance
detector: Optional[AnomalyDetector] = None


async def dispatch_webhook_escalation(heart_rate: int, temperature: float, risk_score: str) -> None:
    """
    Fires an asynchronous HTTP POST request to the n8n escalation webhook when an anomaly is detected.
    """
    payload = {
        "event": "AEGIS_ANOMALY_ESCALATION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": heart_rate,
        "temperature": temperature,
        "risk_score": risk_score,
        "message": f"Critical physiological anomaly detected: HR={heart_rate} BPM, Temp={temperature}°C",
        "system": "AEGIS-Phase1-Core"
    }
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(WEBHOOK_URL, json=payload)
            logger.info("Escalation webhook response: HTTP %s", response.status_code)
    except Exception as exc:
        logger.warning("Escalation webhook dispatch note (n8n offline or unreachable): %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector
    logger.info("Initializing AEGIS AnomalyDetector ML Core on startup...")
    detector = AnomalyDetector()
    logger.info("AEGIS AnomalyDetector initialized and trained on baseline data.")
    yield


app = FastAPI(
    title="AEGIS Offline-First Health Companion API",
    version="1.1.0",
    description="Offline-first telemetry ingestion, anomaly detection, and localized LLM advice engine.",
    lifespan=lifespan
)


class TelemetryPayload(BaseModel):
    heart_rate: int = Field(..., description="Heart rate in beats per minute (BPM)")
    temperature: float = Field(..., description="Body temperature in Celsius (°C)")


class TelemetryResponse(BaseModel):
    status: str = "success"
    risk_score: str
    is_anomaly: bool
    heart_rate: int
    temperature: float
    escalated: bool = False


class ExplainRiskPayload(BaseModel):
    heart_rate: int = Field(..., description="Heart rate in beats per minute (BPM)")
    temperature: float = Field(..., description="Body temperature in Celsius (°C)")
    risk_score: Optional[str] = Field(None, description="Optional pre-evaluated risk score ('Normal' or 'High')")


@app.get("/")
def read_root():
    return {
        "service": "AEGIS Health Companion",
        "version": "1.1.0",
        "status": "online",
        "engine": "IsolationForest Active",
        "llm_assistant": "aegis-baymax (Ollama)"
    }


@app.post("/ingest-telemetry", response_model=TelemetryResponse, status_code=status.HTTP_200_OK)
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    """
    Ingest physiological telemetry data, evaluate with ML model,
    and trigger background escalation webhook if anomaly is detected.
    """
    global detector
    if detector is None:
        detector = AnomalyDetector()

    result: EvaluationResult = detector.evaluate(payload.heart_rate, payload.temperature)
    escalated = False

    if result.is_anomaly:
        logger.warning(
            "⚠️ ANOMALY DETECTED: HR=%d BPM, Temp=%.1f°C -> Risk: %s. Scheduling escalation webhook.",
            payload.heart_rate,
            payload.temperature,
            result.risk_score
        )
        background_tasks.add_task(
            dispatch_webhook_escalation,
            payload.heart_rate,
            payload.temperature,
            result.risk_score
        )
        escalated = True
    else:
        logger.info(
            "Normal telemetry: HR=%d BPM, Temp=%.1f°C -> Risk: %s",
            payload.heart_rate,
            payload.temperature,
            result.risk_score
        )

    return TelemetryResponse(
        status="success",
        risk_score=result.risk_score,
        is_anomaly=result.is_anomaly,
        heart_rate=payload.heart_rate,
        temperature=payload.temperature,
        escalated=escalated
    )


@app.post("/explain-risk")
async def explain_risk(payload: ExplainRiskPayload):
    """
    Translate telemetry anomalies and risk scores into actionable safety advice
    streaming from localized aegis-baymax LLM.
    """
    global detector
    if detector is None:
        detector = AnomalyDetector()

    risk_score = payload.risk_score
    if not risk_score:
        result = detector.evaluate(payload.heart_rate, payload.temperature)
        risk_score = result.risk_score

    return await generate_explanation(
        hr=payload.heart_rate,
        temp=payload.temperature,
        risk_score=risk_score
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
