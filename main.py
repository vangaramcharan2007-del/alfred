"""
AEGIS Health Companion - FastAPI Backend
Provides telemetry ingestion, WESAD physiological ML evaluation,
live OpenCV MJPEG video streaming (/video-feed), persistent SQLite memory inspection (/memory-records),
and dynamic non-repetitive Baymax health intelligence (/companion-interact).
"""

from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from typing import Optional, List, Dict, Any

import httpx
import ollama
from fastapi import FastAPI, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from aegis_engine import (
    AnomalyDetector,
    EvaluationResult,
    WESADPhysiologicalDetector,
    WESADEvaluationResult
)
from aegis_memory import AegisMemory
from aegis_vision import global_scanner
from baymax_service import DynamicBaymaxEngine, generate_explanation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aegis_backend")

WEBHOOK_URL = "http://localhost:5678/webhook/aegis-escalation"

detector: Optional[AnomalyDetector] = None
wesad_detector: Optional[WESADPhysiologicalDetector] = None
aegis_memory: Optional[AegisMemory] = None
telemetry_history: deque = deque(maxlen=60)
async_ollama_client = ollama.AsyncClient()


async def dispatch_webhook_escalation(
    heart_rate: float,
    temperature: float,
    risk_score: str,
    rmssd: Optional[float] = None,
    eda: Optional[float] = None
) -> None:
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
    global detector, wesad_detector, aegis_memory
    logger.info("Initializing AEGIS AnomalyDetector, WESAD Classifier, and SQLite Memory...")
    detector = AnomalyDetector()
    wesad_detector = WESADPhysiologicalDetector()
    aegis_memory = AegisMemory(db_path="aegis_core.db")
    logger.info("AEGIS Core Systems Online.")

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
    title="AEGIS Medical Intelligence Workstation Core",
    version="3.0.0",
    description="Offline-first clinical intelligence, live camera streaming, WESAD classification, and dynamic voice persona.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TelemetryPayload(BaseModel):
    heart_rate: int = Field(..., description="Heart rate in BPM")
    temperature: float = Field(..., description="Body temperature in °C")


class TelemetryResponse(BaseModel):
    status: str = "success"
    risk_score: str
    is_anomaly: bool
    heart_rate: int
    temperature: float
    escalated: bool = False
    timestamp: str = ""


class ExplainRiskPayload(BaseModel):
    heart_rate: int = Field(...)
    temperature: float = Field(...)
    risk_score: Optional[str] = Field(None)


class CompanionChatRequest(BaseModel):
    user_speech: str = Field(..., description="User query or voice transcript")
    heart_rate: float = Field(72.0)
    rmssd: float = Field(45.0)
    temperature: float = Field(36.8)
    temp_slope: float = Field(0.0)
    eda: float = Field(1.5)
    ear: Optional[float] = Field(None)


class CompanionChatResponse(BaseModel):
    reply_text: str
    is_anomaly: bool
    risk_level: str
    confidence: float
    vital_summary: Dict[str, float]
    escalated: bool = False
    fatigue_detected: bool = False


@app.get("/")
def read_root():
    return {
        "service": "AEGIS Clinical Workstation Backend",
        "version": "3.0.0",
        "status": "online",
        "video_stream": "GET /video-feed (MJPEG)",
        "memory_inspector": "GET /memory-records",
        "ml_engine": "WESAD Multi-Modal Random Forest + IsolationForest",
        "nlp_engine": "DynamicBaymaxEngine"
    }


@app.get("/video-feed")
def video_feed():
    """
    Live OpenCV MJPEG Video Stream with facial ROI tracking,
    Eye Aspect Ratio, and Forehead rPPG waveform.
    """
    return StreamingResponse(
        global_scanner.generate_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/live-vision-metrics")
def get_live_vision_metrics():
    """Fetch the latest live optical metrics from SQLite memory."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")

    latest = aegis_memory.get_latest_vital()
    if not latest:
        return {
            "status": "no_data",
            "heart_rate": 72.0,
            "eye_aspect_ratio": 0.30,
            "fatigue_flag": False,
            "rppg_signal": 128.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    return {"status": "active", **latest}


@app.get("/memory-records")
def get_memory_records(limit: int = 30):
    """
    Fetch live rows from vitals_log and memory_context with calculated rolling averages.
    """
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")

    raw_vitals = aegis_memory.get_recent_baseline(limit=limit)
    vitals_list = []
    hr_vals, ear_vals = [], []
    fatigue_count = 0

    for r in raw_vitals:
        hr_vals.append(r[0])
        ear_vals.append(r[1])
        if r[2]:
            fatigue_count += 1
        vitals_list.append({
            "heart_rate": round(r[0], 1),
            "eye_aspect_ratio": round(r[1], 3),
            "fatigue_flag": bool(r[2]),
            "rppg_signal": round(r[3], 1)
        })

    rolling_stats = {
        "record_count": len(vitals_list),
        "avg_heart_rate": round(sum(hr_vals) / max(1, len(hr_vals)), 1) if hr_vals else 72.0,
        "avg_ear": round(sum(ear_vals) / max(1, len(ear_vals)), 3) if ear_vals else 0.30,
        "fatigue_events_in_window": fatigue_count
    }

    conversation_history = aegis_memory.get_conversation_context(limit=10)

    return {
        "rolling_stats": rolling_stats,
        "vitals_log": vitals_list,
        "conversation_context": conversation_history
    }


@app.post("/clear-memory")
def clear_memory():
    """Clear memory logs and reset database baseline."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    aegis_memory.clear_memory()
    return {"status": "memory_cleared"}


@app.get("/telemetry-history", response_model=List[Dict[str, Any]])
def get_telemetry_history():
    return list(telemetry_history)


@app.post("/ingest-telemetry", response_model=TelemetryResponse)
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    global detector
    if detector is None:
        detector = AnomalyDetector()

    result: EvaluationResult = detector.evaluate(payload.heart_rate, payload.temperature)
    escalated = False
    current_time_str = datetime.now(timezone.utc).strftime("%H:%M:%S")

    if result.is_anomaly:
        background_tasks.add_task(
            dispatch_webhook_escalation,
            float(payload.heart_rate),
            float(payload.temperature),
            result.risk_score
        )
        escalated = True

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
    Evaluates 5-feature WESAD parameters, checks live EAR & fatigue from camera,
    and synthesizes non-repetitive contextual speech advice.
    """
    global wesad_detector, aegis_memory
    if wesad_detector is None:
        wesad_detector = WESADPhysiologicalDetector()
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")

    # Fetch recent baseline for rolling context
    recent_records = aegis_memory.get_recent_baseline(limit=20)
    avg_hr = sum(r[0] for r in recent_records) / max(1, len(recent_records)) if recent_records else req.heart_rate

    # Determine EAR and Fatigue
    ear_val = req.ear if req.ear is not None else 0.30
    fatigue_detected = bool(ear_val < 0.22)

    # 1. WESAD Physiological Evaluation
    eval_res: WESADEvaluationResult = wesad_detector.evaluate(
        heart_rate=req.heart_rate,
        rmssd=req.rmssd,
        temperature=req.temperature,
        temp_slope=req.temp_slope,
        eda=req.eda
    )

    escalated = False
    if eval_res.is_anomaly or fatigue_detected:
        risk_level = "HIGH RISK"
        background_tasks.add_task(
            dispatch_webhook_escalation,
            req.heart_rate,
            req.temperature,
            risk_level,
            req.rmssd,
            req.eda
        )
        escalated = True
    else:
        risk_level = eval_res.risk_level

    # Record user message to persistent SQLite memory
    aegis_memory.add_conversation(role="user", content=req.user_speech)
    recent_convos = aegis_memory.get_conversation_context(limit=6)

    # 2. Dynamic Healthcare Intelligence Synthesis
    prompt = (
        f"User speech: '{req.user_speech}'. "
        f"Vitals: HR={req.heart_rate:.0f} BPM, HRV={req.rmssd:.0f}ms, Temp={req.temperature:.1f}°C, EDA={req.eda:.1f}µS. "
        f"Vision: EAR={ear_val:.3f}, Drowsiness={fatigue_detected}. "
        "As Baymax, provide calm, concise medical guidance strictly under 2 sentences."
    )

    reply_text = ""
    try:
        response = await async_ollama_client.chat(
            model="aegis-baymax",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_text = response.get("message", {}).get("content", "")
    except Exception:
        # High-order dynamic synthesis engine
        reply_text = DynamicBaymaxEngine.synthesize_response(
            user_speech=req.user_speech,
            heart_rate=req.heart_rate,
            rmssd=req.rmssd,
            temperature=req.temperature,
            temp_slope=req.temp_slope,
            eda=req.eda,
            ear=ear_val,
            is_fatigued=fatigue_detected,
            is_anomaly=eval_res.is_anomaly,
            recent_history=recent_convos,
            baseline_stats={"avg_hr": avg_hr}
        )

    # Record Baymax reply to persistent SQLite memory
    aegis_memory.add_conversation(role="baymax", content=reply_text)

    return CompanionChatResponse(
        reply_text=reply_text,
        is_anomaly=eval_res.is_anomaly or fatigue_detected,
        risk_level=risk_level,
        confidence=eval_res.confidence,
        vital_summary=eval_res.features,
        escalated=escalated,
        fatigue_detected=fatigue_detected
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
