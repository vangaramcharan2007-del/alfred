"""
AEGIS Health Companion - FastAPI Backend
Handles telemetry ingestion, WESAD multi-modal anomaly classification,
companion voice interaction, n8n webhook escalation, and localized LLM streaming.
"""

from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from typing import Optional, List, Dict, Any

import httpx
import ollama
from fastapi import FastAPI, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from aegis_engine import (
    AnomalyDetector,
    EvaluationResult,
    WESADPhysiologicalDetector,
    WESADEvaluationResult
)
from baymax_service import generate_explanation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aegis_backend")

WEBHOOK_URL = "http://localhost:5678/webhook/aegis-escalation"

# Global detector instances & history buffer
detector: Optional[AnomalyDetector] = None
wesad_detector: Optional[WESADPhysiologicalDetector] = None
telemetry_history: deque = deque(maxlen=60)
async_ollama_client = ollama.AsyncClient()


async def dispatch_webhook_escalation(
    heart_rate: float,
    temperature: float,
    risk_score: str,
    rmssd: Optional[float] = None,
    eda: Optional[float] = None
) -> None:
    """
    Fires an asynchronous HTTP POST request to the n8n escalation webhook when an anomaly is detected.
    """
    payload = {
        "event": "AEGIS_ANOMALY_ESCALATION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": heart_rate,
        "temperature": temperature,
        "rmssd": rmssd,
        "eda": eda,
        "risk_score": risk_score,
        "message": f"Critical physiological anomaly detected: HR={heart_rate} BPM, Temp={temperature}°C, HRV={rmssd}ms",
        "system": "AEGIS-WESAD-BaymaxCore"
    }
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(WEBHOOK_URL, json=payload)
            logger.info("Escalation webhook response: HTTP %s", response.status_code)
    except Exception as exc:
        logger.warning("Escalation webhook dispatch note (n8n offline or unreachable): %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector, wesad_detector
    logger.info("Initializing AEGIS AnomalyDetector & WESAD Classifier on startup...")
    detector = AnomalyDetector()
    wesad_detector = WESADPhysiologicalDetector()
    logger.info("AEGIS ML models ready.")
    
    # Populate initial baseline seed data in history buffer
    now = datetime.now(timezone.utc)
    for i in range(5):
        telemetry_history.append({
            "id": i + 1,
            "timestamp": now.strftime("%H:%M:%S"),
            "heart_rate": 72,
            "temperature": 36.8,
            "rmssd": 45.0,
            "eda": 1.5,
            "risk_score": "Normal",
            "is_anomaly": False,
            "escalated": False
        })
    yield


app = FastAPI(
    title="AEGIS Baymax Companion Core API",
    version="2.0.0",
    description="Offline-first physiological intelligence, WESAD classification, and voice companion engine.",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    timestamp: str = ""


class ExplainRiskPayload(BaseModel):
    heart_rate: int = Field(..., description="Heart rate in beats per minute (BPM)")
    temperature: float = Field(..., description="Body temperature in Celsius (°C)")
    risk_score: Optional[str] = Field(None, description="Optional pre-evaluated risk score ('Normal' or 'High')")


class CompanionChatRequest(BaseModel):
    user_speech: str = Field(..., description="Transcribed user query or voice input")
    heart_rate: float = Field(72.0, description="Heart rate in BPM")
    rmssd: float = Field(45.0, description="HRV RMSSD in ms")
    temperature: float = Field(36.8, description="Skin/Core temperature in °C")
    temp_slope: float = Field(0.0, description="Temperature slope (°C/min)")
    eda: float = Field(1.5, description="Electrodermal activity / GSR (µS)")


class CompanionChatResponse(BaseModel):
    reply_text: str
    is_anomaly: bool
    risk_level: str
    confidence: float
    vital_summary: Dict[str, float]
    escalated: bool = False


@app.get("/")
def read_root():
    return {
        "service": "AEGIS Baymax Health Companion",
        "version": "2.0.0",
        "status": "online",
        "ml_engine": "WESAD Multi-Modal Random Forest + IsolationForest",
        "companion_persona": "aegis-baymax (Ollama Local LLM)"
    }


@app.get("/telemetry-history", response_model=List[Dict[str, Any]])
def get_telemetry_history():
    """Return historical telemetry readings for the Next.js frontend."""
    return list(telemetry_history)


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
    current_time_str = datetime.now(timezone.utc).strftime("%H:%M:%S")

    if result.is_anomaly:
        logger.warning(
            "⚠️ ANOMALY DETECTED: HR=%d BPM, Temp=%.1f°C -> Risk: %s. Scheduling escalation webhook.",
            payload.heart_rate,
            payload.temperature,
            result.risk_score
        )
        background_tasks.add_task(
            dispatch_webhook_escalation,
            float(payload.heart_rate),
            float(payload.temperature),
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

    history_item = {
        "id": len(telemetry_history) + 1,
        "timestamp": current_time_str,
        "heart_rate": payload.heart_rate,
        "temperature": payload.temperature,
        "risk_score": result.risk_score,
        "is_anomaly": result.is_anomaly,
        "escalated": escalated
    }
    telemetry_history.append(history_item)

    return TelemetryResponse(
        status="success",
        risk_score=result.risk_score,
        is_anomaly=result.is_anomaly,
        heart_rate=payload.heart_rate,
        temperature=payload.temperature,
        escalated=escalated,
        timestamp=current_time_str
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


@app.post("/companion-interact", response_model=CompanionChatResponse)
async def companion_interact(req: CompanionChatRequest, background_tasks: BackgroundTasks):
    """
    Two-way interactive Baymax companion endpoint.
    Evaluates 5-feature WESAD physiological parameters and produces vocal-ready guidance.
    """
    global wesad_detector
    if wesad_detector is None:
        wesad_detector = WESADPhysiologicalDetector()

    # 1. Multi-modal physiological evaluation
    eval_res: WESADEvaluationResult = wesad_detector.evaluate(
        heart_rate=req.heart_rate,
        rmssd=req.rmssd,
        temperature=req.temperature,
        temp_slope=req.temp_slope,
        eda=req.eda
    )

    escalated = False
    if eval_res.is_anomaly:
        logger.warning(
            "⚠️ WESAD ANOMALY TRIGGERED: HR=%.1f, HRV=%.1fms, Temp=%.1f°C, EDA=%.1fµS -> Status: %s",
            req.heart_rate,
            req.rmssd,
            req.temperature,
            req.eda,
            eval_res.risk_level
        )
        background_tasks.add_task(
            dispatch_webhook_escalation,
            req.heart_rate,
            req.temperature,
            eval_res.risk_level,
            req.rmssd,
            req.eda
        )
        escalated = True

    # 2. Contextual LLM Voice Prompt
    prompt = (
        f"User said: '{req.user_speech}'. "
        f"Vitals Context: Heart Rate={req.heart_rate:.0f} BPM, HRV/RMSSD={req.rmssd:.0f}ms, Core Temp={req.temperature:.1f}°C, EDA={req.eda:.1f}µS. "
        f"Physical State: {eval_res.risk_level}. "
        "Reply as Baymax: a calm, soothing personal healthcare companion. "
        "Speak directly to the user in a gentle, reassuring manner. Keep your response strictly under 2 sentences."
    )

    reply_text = ""
    try:
        response = await async_ollama_client.chat(
            model="aegis-baymax",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_text = response.get("message", {}).get("content", "")
    except Exception as exc:
        logger.warning("Ollama unavailable (%s). Using specialized Baymax offline voice heuristic.", exc)
        if eval_res.is_anomaly:
            reply_text = (
                "I detect an acute elevation in your thermal baseline and sympathetic arousal. "
                "Please sit down, hydrate with cool water, and allow me to initiate a cooldown protocol."
            )
        elif "how" in req.user_speech.lower() and ("am" in req.user_speech.lower() or "vital" in req.user_speech.lower() or "feel" in req.user_speech.lower()):
            reply_text = (
                f"Your vitals indicate optimal cardiovascular equilibrium with a heart rate of {int(req.heart_rate)} BPM "
                f"and healthy heart rate variability. You are in good condition."
            )
        elif "hello" in req.user_speech.lower() or "hi" in req.user_speech.lower():
            reply_text = "Hello, I am Baymax, your personal healthcare companion. How may I assist your well-being today?"
        else:
            reply_text = (
                f"I am monitoring your biometrics. Your heart rate is {int(req.heart_rate)} BPM and temperature is {req.temperature:.1f}°C, "
                "both within standard resting parameters."
            )

    return CompanionChatResponse(
        reply_text=reply_text,
        is_anomaly=eval_res.is_anomaly,
        risk_level=eval_res.risk_level,
        confidence=eval_res.confidence,
        vital_summary=eval_res.features,
        escalated=escalated
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
