"""
AEGIS Health Companion - FastAPI Backend
Provides telemetry ingestion, WESAD physiological ML evaluation,
live OpenCV MJPEG video streaming, persistent SQLite memory & EHR inspection (/memory-records, /patient-profile),
Offline Medical RAG knowledge base (/medical-protocols),
HL7 / FHIR v4.0.1 Emergency Clinical Handover Export (/clinical-handover/fhir, /clinical-handover/triage-report),
and Doctor-Level Multi-Turn Ollama LLaMA health intelligence (/companion-interact).
"""

from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from typing import Optional, List, Dict, Any

import httpx
from fastapi import FastAPI, BackgroundTasks, status, Response
from fastapi.responses import StreamingResponse, HTMLResponse
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
from medical_rag import OfflineMedicalRAG
from fhir_exporter import generate_fhir_bundle, generate_html_triage_report
from baymax_service import generate_baymax_reply_text, generate_explanation, is_third_party_query

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aegis_backend")

WEBHOOK_URL = "http://localhost:5678/webhook/aegis-escalation"

detector: Optional[AnomalyDetector] = None
wesad_detector: Optional[WESADPhysiologicalDetector] = None
aegis_memory: Optional[AegisMemory] = None
medical_rag: Optional[OfflineMedicalRAG] = None
telemetry_history: deque = deque(maxlen=60)
latest_vitals_snapshot: Dict[str, Any] = {
    "heart_rate": 72.0,
    "temperature": 36.8,
    "rmssd": 45.0,
    "temp_slope": 0.0,
    "eda": 1.5,
    "ear": 0.32,
    "posture_status": "ERECT_NOMINAL",
    "head_tilt_deg": 0.0,
    "syncope_detected": False
}


async def dispatch_webhook_escalation(
    heart_rate: float,
    temperature: float,
    risk_score: str,
    rmssd: Optional[float] = None,
    eda: Optional[float] = None,
    posture_status: Optional[str] = None
) -> None:
    payload = {
        "event": "AEGIS_ANOMALY_ESCALATION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": heart_rate,
        "temperature": temperature,
        "rmssd": rmssd,
        "eda": eda,
        "risk_score": risk_score,
        "posture_status": posture_status or "ERECT_NOMINAL",
        "message": f"Critical anomaly detected: HR={heart_rate} BPM, Temp={temperature}°C, HRV={rmssd}ms, Posture={posture_status}",
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
    global detector, wesad_detector, aegis_memory, medical_rag
    logger.info("Initializing AEGIS AnomalyDetector, WESAD Classifier with XAI, SQLite EHR Memory, and Medical RAG...")
    detector = AnomalyDetector()
    wesad_detector = WESADPhysiologicalDetector()
    aegis_memory = AegisMemory(db_path="aegis_core.db")
    medical_rag = OfflineMedicalRAG()
    logger.info("AEGIS Core Doctor-Level Systems Online with FHIR & XAI support.")

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
    version="3.6.0",
    description="Offline-first clinical intelligence, HL7/FHIR Handover Export, Explainable AI (XAI), and Syncope Fall Detection.",
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


class PatientProfileUpdatePayload(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    allergies: Optional[str] = None
    active_medications: Optional[str] = None
    chronic_conditions: Optional[str] = None


class CompanionChatRequest(BaseModel):
    user_speech: str = Field(..., description="User query or voice transcript")
    heart_rate: float = Field(72.0)
    rmssd: float = Field(45.0)
    temperature: float = Field(36.8)
    temp_slope: float = Field(0.0)
    eda: float = Field(1.5)
    ear: Optional[float] = Field(None)
    head_tilt_deg: Optional[float] = Field(0.0)
    syncope_detected: Optional[bool] = Field(False)
    posture_status: Optional[str] = Field("ERECT_NOMINAL")
    language: Optional[str] = Field("en", description="Target language code (en, te, hi, ta, kn)")


class CompanionChatResponse(BaseModel):
    reply_text: str
    is_anomaly: bool
    risk_level: str
    confidence: float
    vital_summary: Dict[str, float]
    feature_contributions: Dict[str, float]
    top_driver: str
    escalated: bool = False
    fatigue_detected: bool = False
    syncope_detected: bool = False
    posture_status: str = "ERECT_NOMINAL"
    matched_protocol: Optional[Dict[str, Any]] = None
    allergy_warning: bool = False
    patient_profile: Optional[Dict[str, Any]] = None


@app.get("/")
def read_root():
    return {
        "service": "AEGIS Doctor-Level Clinical Workstation Backend",
        "version": "3.6.0",
        "status": "online",
        "llm_engine": "Ollama Local LLaMA 3 Model",
        "medical_rag": "OfflineMedicalRAG Active",
        "fhir_interoperability": "HL7 FHIR v4.0.1 Enabled",
        "xai_engine": "Explainable AI Biomarker Attribution Active",
        "vision_fall_detection": "Syncope & Head Tilt Posture Detector Active"
    }


@app.get("/patient-profile")
def get_patient_profile():
    """Retrieve the active patient's Electronic Health Record (EHR)."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.get_patient_profile()


@app.get("/patients")
def list_patients():
    """List all registered village & hospital patients."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.list_all_patients()


class SwitchPatientPayload(BaseModel):
    patient_uid: str


@app.post("/patients/switch")
def switch_active_patient(payload: SwitchPatientPayload):
    """Switch active patient for offline clinical triage."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.set_active_patient(payload.patient_uid)


class TakeMedicationPayload(BaseModel):
    medication_id: int


class AddMedicationPayload(BaseModel):
    patient_uid: str
    medication_name: str
    dosage: str
    frequency: str
    time_slot: str
    instructions: Optional[str] = "Take with water after meals"


@app.get("/medications")
def get_medications(patient_uid: Optional[str] = None):
    """Retrieve patient medication schedule and adherence."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.get_patient_medications(patient_uid)


@app.post("/medications/take")
def take_medication(payload: TakeMedicationPayload):
    """Mark a scheduled medication dose as taken."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.mark_medication_taken(payload.medication_id)


@app.post("/medications/add")
def add_medication(payload: AddMedicationPayload):
    """Add a new medication reminder to patient schedule."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.add_medication(
        patient_uid=payload.patient_uid,
        medication_name=payload.medication_name,
        dosage=payload.dosage,
        frequency=payload.frequency,
        time_slot=payload.time_slot,
        instructions=payload.instructions or "Take with water"
    )


@app.get("/sync-queue/status")
def get_sync_status():
    """Get offline Store-and-Forward FHIR sync queue metrics."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.get_sync_queue_status()


from aegis_diagnostics import MultimodalDiagnostics


class AnemiaScreeningPayload(BaseModel):
    erythema_index: float = Field(2.5, description="Capillary erythema index")
    r_channel_mean: float = Field(145.0, description="Red channel optical mean")


class CoughAcousticPayload(BaseModel):
    spectral_flux: float = Field(0.72, description="Acoustic spectral flux")
    peak_frequency_hz: float = Field(1550.0, description="Peak frequency in Hertz")


class QSOFAPayload(BaseModel):
    heart_rate: float = Field(108.0)
    temperature: float = Field(39.1)
    temp_slope: float = Field(0.12)
    syncope_detected: bool = Field(False)
    respiratory_rate: float = Field(24.0)
    systolic_bp: float = Field(88.0)


class SatelliteSOSPayload(BaseModel):
    patient_uid: Optional[str] = None
    gps_coords: Optional[str] = "17.9689 N, 79.5941 E"


@app.post("/diagnostics/anemia")
def screen_anemia(payload: AnemiaScreeningPayload):
    """Optical conjunctival & capillary colorimetry anemia screener."""
    return MultimodalDiagnostics.estimate_anemia_from_pallor(
        erythema_index=payload.erythema_index,
        r_channel_mean=payload.r_channel_mean
    )


@app.post("/diagnostics/cough")
def analyze_cough(payload: CoughAcousticPayload):
    """Acoustic cough biomarker frequency spectrogram classifier."""
    return MultimodalDiagnostics.analyze_cough_acoustics(
        spectral_flux=payload.spectral_flux,
        peak_frequency_hz=payload.peak_frequency_hz
    )


@app.post("/diagnostics/qsofa")
def calculate_qsofa_sepsis(payload: QSOFAPayload):
    """Predictive Clinical Decision Support (CDS) for qSOFA Sepsis Shock Trajectory."""
    return MultimodalDiagnostics.evaluate_qsofa_sepsis_trajectory(
        heart_rate=payload.heart_rate,
        temperature=payload.temperature,
        temp_slope=payload.temp_slope,
        syncope_detected=payload.syncope_detected,
        estimated_respiratory_rate=payload.respiratory_rate,
        estimated_systolic_bp=payload.systolic_bp
    )


@app.post("/diagnostics/satellite-sos")
def generate_sos_packet(payload: SatelliteSOSPayload):
    """Generate 140-byte compact encrypted telemetry string for LoRa / Satellite SOS."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    
    patient = aegis_memory.get_patient_profile(payload.patient_uid)
    p_uid = patient.get("patient_uid", "PAT-RAM-2026")
    b_type = patient.get("blood_type", "O+")

    latest_v = latest_vitals_snapshot or {"heart_rate": 72.0, "temperature": 36.8, "temp_slope": 0.0, "syncope_detected": False}
    qsofa = MultimodalDiagnostics.evaluate_qsofa_sepsis_trajectory(
        heart_rate=latest_v.get("heart_rate", 72.0),
        temperature=latest_v.get("temperature", 36.8),
        temp_slope=latest_v.get("temp_slope", 0.0),
        syncope_detected=latest_v.get("syncope_detected", False)
    )

    return MultimodalDiagnostics.generate_satellite_sos_packet(
        patient_uid=p_uid,
        blood_type=b_type,
        heart_rate=latest_v.get("heart_rate", 72.0),
        temperature=latest_v.get("temperature", 36.8),
        qsofa_score=qsofa["qsofa_score"],
        shock_probability=qsofa["shock_probability"],
        gps_coords=payload.gps_coords or "17.9689 N, 79.5941 E"
    )


@app.post("/sync-queue/trigger")
def trigger_hospital_sync():
    """Trigger opportunistic batch sync to District Hospital / ABDM gateway."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.trigger_sync_batch()


# ============================================================================
# ADVANCED CLINICAL SCANNERS: Medicine OCR, ABHA QR, Chest X-Ray, Hand Gesture
# ============================================================================
from aegis_scanners import scan_medicine_strip, decode_abha_qr, classify_chest_xray, map_hand_to_organ


class MedicineOCRPayload(BaseModel):
    ocr_text: str = Field(..., description="Raw OCR text extracted from medicine strip image")
    patient_uid: Optional[str] = Field(None, description="Optional patient UID to cross-reference allergies")
    patient_allergies: Optional[List[str]] = Field(None, description="Optional explicit allergies list")


class ABHAQRPayload(BaseModel):
    qr_payload: str = Field(..., description="Raw decoded string from ABHA QR code scanner")


class ChestXRayPayload(BaseModel):
    pixel_intensity_mean: float = Field(128.0)
    lung_opacity_ratio: float = Field(0.15)
    contrast_score: float = Field(0.65)
    cardiac_silhouette_ratio: float = Field(0.48)
    upper_lobe_density: float = Field(0.12)
    lower_lobe_density: float = Field(0.18)
    bilateral: bool = Field(False)


class HandGesturePayload(BaseModel):
    index_tip_x: float = Field(0.5, description="Normalized X of index finger tip (0-1)")
    index_tip_y: float = Field(0.3, description="Normalized Y of index finger tip (0-1)")
    wrist_x: float = Field(0.5, description="Normalized X of wrist (0-1)")
    wrist_y: float = Field(0.7, description="Normalized Y of wrist (0-1)")
    hand_detected: bool = Field(True)
    is_pointing: bool = Field(True)


@app.post("/scanner/medicine-ocr")
def scanner_medicine_ocr(payload: MedicineOCRPayload):
    """Scan medicine strip text via OCR and identify drug, dosage, allergy cross-ref."""
    if payload.patient_allergies is not None:
        allergies = payload.patient_allergies
    else:
        global aegis_memory
        if aegis_memory is None:
            aegis_memory = AegisMemory(db_path="aegis_core.db")
        patient = aegis_memory.get_patient_profile(patient_uid=payload.patient_uid or "p-001")
        allergies = patient.get("allergies_list", ["ibuprofen", "nsaids", "aspirin"])
    return scan_medicine_strip(ocr_text=payload.ocr_text, patient_allergies=allergies)


@app.post("/scanner/abha-qr")
def scanner_abha_qr(payload: ABHAQRPayload):
    """Decode Ayushman Bharat (ABHA) National Health ID from QR code."""
    return decode_abha_qr(qr_payload=payload.qr_payload)


@app.post("/scanner/chest-xray")
def scanner_chest_xray(payload: ChestXRayPayload):
    """Classify chest X-ray features for pneumonia, TB, or cardiomegaly screening."""
    return classify_chest_xray(
        pixel_intensity_mean=payload.pixel_intensity_mean,
        lung_opacity_ratio=payload.lung_opacity_ratio,
        contrast_score=payload.contrast_score,
        cardiac_silhouette_ratio=payload.cardiac_silhouette_ratio,
        upper_lobe_density=payload.upper_lobe_density,
        lower_lobe_density=payload.lower_lobe_density,
        bilateral=payload.bilateral,
    )


@app.post("/scanner/hand-gesture")
def scanner_hand_gesture(payload: HandGesturePayload):
    """Map hand gesture raycast to anatomical organ zone on 3D Digital Twin."""
    return map_hand_to_organ(
        index_tip_x=payload.index_tip_x,
        index_tip_y=payload.index_tip_y,
        wrist_x=payload.wrist_x,
        wrist_y=payload.wrist_y,
        hand_detected=payload.hand_detected,
        is_pointing=payload.is_pointing,
    )


# ============================================================================
# MULTI-LINGUAL AUDIO SUITE: Genuine Telugu/Hindi/Tamil/Kannada/English TTS & STT
# ============================================================================
from aegis_audio import synthesize_speech, transcribe_audio_payload


class TTSPayload(BaseModel):
    text: str = Field(..., description="Text to synthesize into natural speech")
    language: str = Field("en", description="Target language code (te, hi, ta, kn, en)")


class STTPayload(BaseModel):
    audio_b64: Optional[str] = Field(None, description="Optional Base64 recorded audio data")
    language: str = Field("en", description="Language code (te, hi, ta, kn, en)")
    sample_index: Optional[int] = Field(None, description="Optional preset trigger index")


@app.post("/audio/tts")
def audio_tts_synthesize(payload: TTSPayload):
    """Synthesize native voice audio in Telugu, Hindi, Tamil, Kannada, or English."""
    return synthesize_speech(text=payload.text, lang=payload.language)


@app.post("/audio/stt")
def audio_stt_transcribe(payload: STTPayload):
    """Transcribe speech into native Telugu, Hindi, Tamil, Kannada, or English."""
    return transcribe_audio_payload(audio_b64=payload.audio_b64, lang=payload.language, sample_index=payload.sample_index)


@app.post("/patient-profile")
def update_patient_profile(payload: PatientProfileUpdatePayload):
    """Update patient EHR record."""
    global aegis_memory
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    return aegis_memory.update_patient_profile(
        name=payload.name,
        age=payload.age,
        allergies=payload.allergies,
        active_medications=payload.active_medications,
        chronic_conditions=payload.chronic_conditions
    )


@app.get("/medical-protocols")
def get_medical_protocols():
    """Retrieve full offline medical knowledge base protocol index."""
    global medical_rag
    if medical_rag is None:
        medical_rag = OfflineMedicalRAG()
    return medical_rag.list_all_protocols()


@app.get("/clinical-handover/fhir")
def export_fhir_handover():
    """
    Generate and export an HL7 / FHIR v4.0.1 compliant Document Bundle JSON
    containing Patient demographics, AllergyIntolerances, Observation timeline, and CarePlan.
    """
    global aegis_memory, medical_rag, wesad_detector, latest_vitals_snapshot
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    if medical_rag is None:
        medical_rag = OfflineMedicalRAG()
    if wesad_detector is None:
        wesad_detector = WESADPhysiologicalDetector()

    patient_ehr = aegis_memory.get_patient_profile()
    recent_baseline = aegis_memory.get_recent_baseline(limit=20)
    avg_hr = sum(r[0] for r in recent_baseline) / max(1, len(recent_baseline)) if recent_baseline else 72.0

    # Calculate XAI attributions
    xai = wesad_detector.calculate_xai_attributions(
        hr=latest_vitals_snapshot.get("heart_rate", 72.0),
        rmssd=latest_vitals_snapshot.get("rmssd", 45.0),
        temp=latest_vitals_snapshot.get("temperature", 36.8),
        temp_slope=latest_vitals_snapshot.get("temp_slope", 0.0),
        eda=latest_vitals_snapshot.get("eda", 1.5)
    )

    matched_proto = medical_rag.retrieve_protocol("fever tachycardia anomaly")

    bundle = generate_fhir_bundle(
        patient_profile=patient_ehr,
        vitals=latest_vitals_snapshot,
        baseline={"avg_hr": avg_hr},
        matched_protocol=matched_proto,
        xai_attributions=xai
    )
    return bundle


@app.get("/clinical-handover/triage-report", response_class=HTMLResponse)
def export_html_triage_report():
    """
    Generate an official, printable Clinical Emergency Triage & Handover HTML Document.
    """
    global aegis_memory, medical_rag, wesad_detector, latest_vitals_snapshot
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    if medical_rag is None:
        medical_rag = OfflineMedicalRAG()
    if wesad_detector is None:
        wesad_detector = WESADPhysiologicalDetector()

    patient_ehr = aegis_memory.get_patient_profile()
    recent_baseline = aegis_memory.get_recent_baseline(limit=20)
    avg_hr = sum(r[0] for r in recent_baseline) / max(1, len(recent_baseline)) if recent_baseline else 72.0

    xai = wesad_detector.calculate_xai_attributions(
        hr=latest_vitals_snapshot.get("heart_rate", 72.0),
        rmssd=latest_vitals_snapshot.get("rmssd", 45.0),
        temp=latest_vitals_snapshot.get("temperature", 36.8),
        temp_slope=latest_vitals_snapshot.get("temp_slope", 0.0),
        eda=latest_vitals_snapshot.get("eda", 1.5)
    )

    matched_proto = medical_rag.retrieve_protocol(
        "fever" if latest_vitals_snapshot.get("temperature", 36.8) > 38.0 else "nominal"
    )

    html_content = generate_html_triage_report(
        patient_profile=patient_ehr,
        vitals=latest_vitals_snapshot,
        baseline={"avg_hr": avg_hr},
        matched_protocol=matched_proto,
        xai_attributions=xai
    )
    return HTMLResponse(content=html_content)


@app.get("/video-feed")
def video_feed():
    """Live OpenCV MJPEG Video Stream."""
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
            "head_tilt_deg": 0.0,
            "syncope_detected": False,
            "posture_status": "ERECT_NOMINAL",
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
        "conversation_context": conversation_history,
        "patient_profile": aegis_memory.get_patient_profile()
    }


@app.post("/clear-memory")
def clear_memory():
    """Clear memory logs and reset database baseline."""
    global aegis_memory, latest_vitals_snapshot
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    aegis_memory.clear_memory()
    latest_vitals_snapshot = {
        "heart_rate": 72.0,
        "temperature": 36.8,
        "rmssd": 45.0,
        "temp_slope": 0.0,
        "eda": 1.5,
        "ear": 0.32,
        "posture_status": "ERECT_NOMINAL",
        "head_tilt_deg": 0.0,
        "syncope_detected": False
    }
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
    Doctor-Level Multi-Turn Baymax Companion Endpoint with XAI and Syncope Posture support.
    """
    global wesad_detector, aegis_memory, medical_rag, latest_vitals_snapshot
    if wesad_detector is None:
        wesad_detector = WESADPhysiologicalDetector()
    if aegis_memory is None:
        aegis_memory = AegisMemory(db_path="aegis_core.db")
    if medical_rag is None:
        medical_rag = OfflineMedicalRAG()

    # 1. Update Snapshot
    ear_val = req.ear if req.ear is not None else 0.32
    fatigue_detected = bool(ear_val < 0.22)
    syncope_detected = bool(req.syncope_detected or (req.head_tilt_deg and req.head_tilt_deg > 35.0))
    posture_status = "SYNCOPE_COLLAPSE_DETECTED" if syncope_detected else req.posture_status or "ERECT_NOMINAL"

    latest_vitals_snapshot = {
        "heart_rate": req.heart_rate,
        "temperature": req.temperature,
        "rmssd": req.rmssd,
        "temp_slope": req.temp_slope,
        "eda": req.eda,
        "ear": ear_val,
        "head_tilt_deg": req.head_tilt_deg or 0.0,
        "syncope_detected": syncope_detected,
        "posture_status": posture_status
    }

    # 2. Fetch Rolling Baseline, Patient EHR, and Recent Conversation History
    recent_records = aegis_memory.get_recent_baseline(limit=20)
    avg_hr = sum(r[0] for r in recent_records) / max(1, len(recent_records)) if recent_records else req.heart_rate
    avg_ear = sum(r[1] for r in recent_records) / max(1, len(recent_records)) if recent_records else 0.32

    patient_ehr = aegis_memory.get_patient_profile()
    chat_history = aegis_memory.get_conversation_context(limit=6)

    is_third_party = is_third_party_query(req.user_speech, chat_history)

    # 3. WESAD Physiological Evaluation + XAI Decomposition
    eval_res: WESADEvaluationResult = wesad_detector.evaluate(
        heart_rate=req.heart_rate,
        rmssd=req.rmssd,
        temperature=req.temperature,
        temp_slope=req.temp_slope,
        eda=req.eda
    )

    escalated = False
    if not is_third_party and (eval_res.is_anomaly or fatigue_detected or syncope_detected):
        risk_level = "HIGH RISK"
        background_tasks.add_task(
            dispatch_webhook_escalation,
            req.heart_rate,
            req.temperature,
            risk_level,
            req.rmssd,
            req.eda,
            posture_status
        )
        escalated = True
    else:
        risk_level = "THIRD-PARTY ADVISORY" if is_third_party else eval_res.risk_level

    # 4. Medical RAG Protocol & Drug Safety Check
    search_query = req.user_speech
    if len(req.user_speech.split()) <= 3 and chat_history:
        for turn in reversed(chat_history):
            if turn.get("role") == "user":
                search_query = f"{turn.get('content', '')} {req.user_speech}"
                break

    matched_protocol = medical_rag.retrieve_protocol(search_query)
    safety_check = medical_rag.evaluate_drug_safety(req.user_speech, patient_ehr.get("allergies_list", []))

    # 5. Doctor-Level Baymax Reasoning with Multi-Turn History
    vitals_dict = {
        "heart_rate": req.heart_rate,
        "temperature": req.temperature,
        "ear": ear_val,
        "rmssd": req.rmssd,
        "eda": req.eda,
        "posture_status": posture_status,
        "syncope_detected": syncope_detected
    }
    baseline_dict = {
        "avg_hr": round(avg_hr, 1),
        "avg_ear": round(avg_ear, 3)
    }

    reply_text = await generate_baymax_reply_text(
        user_query=req.user_speech,
        vitals=vitals_dict,
        baseline=baseline_dict,
        patient_profile=patient_ehr,
        conversation_history=chat_history,
        language=req.language or "en"
    )

    # 6. Record user and Baymax turns to SQLite
    aegis_memory.add_conversation(role="user", content=req.user_speech)
    aegis_memory.add_conversation(role="baymax", content=reply_text)

    return CompanionChatResponse(
        reply_text=reply_text,
        is_anomaly=(eval_res.is_anomaly or fatigue_detected or syncope_detected) if not is_third_party else False,
        risk_level=risk_level,
        confidence=eval_res.confidence,
        vital_summary=eval_res.features,
        feature_contributions=eval_res.feature_contributions,
        top_driver=eval_res.top_driver,
        escalated=escalated,
        fatigue_detected=fatigue_detected if not is_third_party else False,
        syncope_detected=syncope_detected,
        posture_status=posture_status,
        matched_protocol=matched_protocol,
        allergy_warning=safety_check["is_contraindicated"],
        patient_profile=patient_ehr
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
