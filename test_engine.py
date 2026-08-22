"""
Unit and Integration Tests for AEGIS Engine, WESAD Multi-Modal Classifier,
FastAPI Ingestion, Pure Ollama LLM Service, Baymax Voice Companion,
Real-Time Computer Vision, Persistent SQLite Memory & EHR Layer,
and Offline Medical RAG with Multi-Turn Conversation Memory.
"""

import os
import asyncio
from unittest.mock import patch, AsyncMock
import numpy as np
import pytest
from fastapi.testclient import TestClient

from aegis_engine import (
    AnomalyDetector,
    EvaluationResult,
    WESADPhysiologicalDetector,
    WESADEvaluationResult
)
from aegis_memory import AegisMemory
from aegis_vision import VitalScanner
from medical_rag import OfflineMedicalRAG
from baymax_service import (
    stream_baymax_reasoning,
    generate_baymax_reply_text,
    generate_explanation,
    is_third_party_query
)
from main import app, dispatch_webhook_escalation


@pytest.fixture
def detector():
    """Fixture providing an initialized and trained AnomalyDetector instance."""
    return AnomalyDetector(random_state=42)


@pytest.fixture
def wesad_detector():
    """Fixture providing an initialized WESAD physiological detector."""
    return WESADPhysiologicalDetector()


@pytest.fixture
def memory():
    """Fixture providing a temporary SQLite test database with EHR support."""
    test_db = "test_aegis_temp.db"
    mem = AegisMemory(db_path=test_db)
    yield mem
    mem.close()
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass


@pytest.fixture
def medical_rag_engine():
    """Fixture providing Offline Medical RAG engine."""
    return OfflineMedicalRAG()


@pytest.fixture
def client():
    """Test client for the FastAPI backend."""
    with TestClient(app) as test_client:
        yield test_client


# ==========================================
# 1. ML Core Evaluation Tests
# ==========================================

def test_evaluate_normal_baseline(detector):
    """Verify that evaluate(70, 37.0) returns Normal risk score and is_anomaly=False."""
    result = detector.evaluate(70, 37.0)
    assert result.risk_score == "Normal"
    assert result.is_anomaly is False


def test_evaluate_critical_anomaly_high(detector):
    """Verify that evaluate(130, 39.5) returns High risk score and is_anomaly=True."""
    result = detector.evaluate(130, 39.5)
    assert result.risk_score == "High"
    assert result.is_anomaly is True


def test_evaluate_various_baselines(detector):
    """Verify normal range boundaries."""
    res_low = detector.evaluate(62, 36.6)
    assert res_low.risk_score == "Normal"
    assert res_low.is_anomaly is False

    res_high_norm = detector.evaluate(78, 37.4)
    assert res_high_norm.risk_score == "Normal"
    assert res_high_norm.is_anomaly is False


def test_evaluate_extreme_anomalies(detector):
    """Verify extreme anomaly values."""
    res_extreme = detector.evaluate(160, 40.2)
    assert res_extreme.risk_score == "High"
    assert res_extreme.is_anomaly is True


# ==========================================
# 2. WESAD Multi-Modal Classifier Tests
# ==========================================

def test_wesad_classifier_normal_and_stress(wesad_detector):
    """Verify WESAD 5-feature classification."""
    normal_res = wesad_detector.evaluate(
        heart_rate=72.0,
        rmssd=45.0,
        temperature=36.8,
        temp_slope=0.0,
        eda=1.5
    )
    assert normal_res.risk_level == "OPTIMAL"
    assert normal_res.is_anomaly is False
    assert normal_res.confidence >= 0.5

    stress_res = wesad_detector.evaluate(
        heart_rate=135.0,
        rmssd=15.0,
        temperature=39.5,
        temp_slope=0.15,
        eda=8.5
    )
    assert stress_res.risk_level == "HIGH RISK"
    assert stress_res.is_anomaly is True
    assert stress_res.confidence >= 0.5


# ==========================================
# 3. FastAPI Ingestion & Escalation Tests
# ==========================================

def test_api_root_endpoint(client):
    """Verify health root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_api_ingest_telemetry_normal(client):
    """Verify POST /ingest-telemetry for normal reading."""
    payload = {"heart_rate": 72, "temperature": 36.8}
    response = client.post("/ingest-telemetry", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["risk_score"] == "Normal"
    assert data["is_anomaly"] is False
    assert data["escalated"] is False


@patch("main.dispatch_webhook_escalation")
def test_api_ingest_telemetry_anomaly_triggers_escalation(mock_dispatch, client):
    """Verify POST /ingest-telemetry triggers background webhook when anomaly occurs."""
    payload = {"heart_rate": 135, "temperature": 39.5}
    response = client.post("/ingest-telemetry", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["risk_score"] == "High"
    assert data["is_anomaly"] is True
    assert data["escalated"] is True


def test_webhook_escalation_dispatcher_handles_connection_error():
    """Verify webhook dispatcher handles unreachable destination gracefully."""
    with patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
        asyncio.run(dispatch_webhook_escalation(heart_rate=135.0, temperature=39.5, risk_score="High"))


def test_api_telemetry_history(client):
    """Verify GET /telemetry-history returns historical readings."""
    response = client.get("/telemetry-history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


# ==========================================
# 4. EHR Memory & Offline Medical RAG Tests
# ==========================================

def test_ehr_patient_profile_crud(memory):
    """Verify EHR patient profile initialization and updates."""
    profile = memory.get_patient_profile()
    assert profile["name"] == "Ramcharan"
    assert profile["blood_type"] == "O+"
    assert "ibuprofen" in profile["allergies_list"]

    updated = memory.update_patient_profile(
        active_medications="Vitamin C 500mg daily",
        chronic_conditions="Mild seasonal allergies"
    )
    assert updated["active_medications"] == "Vitamin C 500mg daily"
    assert updated["chronic_conditions"] == "Mild seasonal allergies"


def test_medical_rag_protocol_retrieval(medical_rag_engine):
    """Verify OfflineMedicalRAG retrieves clinical guidelines."""
    # Fever Protocol
    fev = medical_rag_engine.retrieve_protocol("spiking high fever and chills")
    assert fev is not None
    assert fev["protocol_id"] == "CLIN-PROT-FEV-01"
    assert "Paracetamol" in fev["pharmacotherapy"]["first_line"]

    # Depression / Mental Health Protocol
    mental = medical_rag_engine.retrieve_protocol("So my frnd is suffering from depression")
    assert mental is not None
    assert mental["protocol_id"] == "CLIN-PROT-MENTAL-07"
    assert "psychiatrist" in mental["first_line_action"].lower()

    # Eye Strain Protocol
    eye = medical_rag_engine.retrieve_protocol("burning eyes from long screen time")
    assert eye is not None
    assert eye["protocol_id"] == "CLIN-PROT-EYE-03"


def test_third_party_query_detection():
    """Verify third-party friend inquiry detection."""
    assert is_third_party_query("So my frnd is suffering from depression") is True
    assert is_third_party_query("My friend has a headache") is True
    assert is_third_party_query("What can I take for my headache?") is False

    # Multi-turn history detection
    history = [{"role": "user", "content": "My friend is sick"}]
    assert is_third_party_query("any medicines?", history) is True


def test_medical_rag_drug_safety_check(medical_rag_engine):
    """Verify drug allergy contraindication flagging."""
    allergies = ["ibuprofen", "nsaids"]
    
    conflict = medical_rag_engine.evaluate_drug_safety("Should I take some Ibuprofen?", allergies)
    assert conflict["is_contraindicated"] is True
    assert "ibuprofen" in conflict["conflicting_allergens"]
    assert "Paracetamol" in conflict["safe_alternative"]

    safe = medical_rag_engine.evaluate_drug_safety("Should I drink some warm water?", allergies)
    assert safe["is_contraindicated"] is False


def test_api_patient_profile_and_protocols(client):
    """Verify GET /patient-profile and GET /medical-protocols endpoints."""
    res_ehr = client.get("/patient-profile")
    assert res_ehr.status_code == 200
    assert res_ehr.json()["name"] == "Ramcharan"

    res_rag = client.get("/medical-protocols")
    assert res_rag.status_code == 200
    assert len(res_rag.json()) >= 6


# ==========================================
# 5. Pure Ollama Multi-Turn LLM Service Tests
# ==========================================

async def mock_async_chat_stream(*args, **kwargs):
    """Mock async generator yielding Ollama chat stream chunks."""
    chunks = [
        {"message": {"content": "I am very sorry to hear about your friend. "}},
        {"message": {"content": "Depression is a clinical condition requiring professional psychiatric evaluation."}}
    ]
    for chunk in chunks:
        yield chunk


def test_pure_ollama_streaming_inference():
    """Verify stream_baymax_reasoning yields model stream chunks."""
    vitals = {"heart_rate": 75, "temperature": 37.0, "ear": 0.32, "rmssd": 45, "eda": 1.5}
    baseline = {"avg_hr": 72.0, "avg_ear": 0.32}

    with patch("ollama.AsyncClient.chat", side_effect=lambda **kw: mock_async_chat_stream()):
        async def run_test():
            parts = []
            async for chunk in stream_baymax_reasoning("Should I take Ibuprofen for fever?", vitals, baseline):
                parts.append(chunk)
            return "".join(parts)

        result = asyncio.run(run_test())
        assert "sorry to hear about your friend" in result or "clinical condition" in result


def test_api_companion_interact_third_party_depression(client):
    """Verify POST /companion-interact handles third-party depression inquiry."""
    payload = {
        "user_speech": "So my frnd is suffering from depression",
        "heart_rate": 72.0,
        "rmssd": 45.0,
        "temperature": 36.8,
        "temp_slope": 0.0,
        "eda": 1.5,
        "ear": 0.32
    }

    with patch("ollama.AsyncClient.chat", side_effect=lambda **kw: mock_async_chat_stream()):
        response = client.post("/companion-interact", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["matched_protocol"] is not None
        assert data["matched_protocol"]["protocol_id"] == "CLIN-PROT-MENTAL-07"
        assert data["risk_level"] == "THIRD-PARTY ADVISORY"


# ==========================================
# 6. Persistent Memory & Real Vision Tests
# ==========================================

def test_aegis_memory_crud(memory):
    """Verify SQLite CRUD logging and retrieval in AegisMemory."""
    row_id = memory.log_vitals(hr=74.5, ear=0.28, is_fatigued=False, rppg_signal=132.0)
    assert row_id is not None
    assert row_id > 0

    latest = memory.get_latest_vital()
    assert latest is not None
    assert latest["heart_rate"] == 74.5
    assert latest["eye_aspect_ratio"] == 0.28
    assert latest["fatigue_flag"] is False

    memory.add_conversation("user", "Check my fatigue level")
    memory.add_conversation("baymax", "Your eye aspect ratio is nominal.")
    context = memory.get_conversation_context(limit=2)
    assert len(context) == 2


def test_vital_scanner_ear_calculation():
    """Verify Eye Aspect Ratio (EAR) mathematical formula."""
    scanner = VitalScanner()
    
    open_eye = [
        (0.0, 10.0), (5.0, 15.0), (10.0, 15.0),
        (15.0, 10.0), (10.0, 5.0), (5.0, 5.0)
    ]
    ear_open = scanner.calculate_ear(open_eye)
    assert ear_open > 0.30

    closed_eye = [
        (0.0, 10.0), (5.0, 10.2), (10.0, 10.2),
        (15.0, 10.0), (10.0, 9.8), (5.0, 9.8)
    ]
    ear_closed = scanner.calculate_ear(closed_eye)
    assert ear_closed < 0.10


def test_vital_scanner_process_frame():
    """Verify VitalScanner processes image frame cleanly."""
    scanner = VitalScanner()
    test_frame = np.full((480, 640, 3), 120, dtype=np.uint8)
    result = scanner.process_frame(test_frame, draw_overlay=True)

    assert "ear" in result
    assert "is_fatigued" in result
    assert "raw_pulse" in result
    assert result["annotated_frame"].shape == (480, 640, 3)


def test_api_live_vision_metrics(client):
    """Verify GET /live-vision-metrics returns vision metrics."""
    response = client.get("/live-vision-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "heart_rate" in data
    assert "eye_aspect_ratio" in data


def test_api_memory_records(client):
    """Verify GET /memory-records returns rolling stats, vitals log, and patient profile."""
    response = client.get("/memory-records")
    assert response.status_code == 200
    data = response.json()
    assert "rolling_stats" in data
    assert "vitals_log" in data
    assert "patient_profile" in data


def test_api_clear_memory(client):
    """Verify POST /clear-memory resets database."""
    response = client.post("/clear-memory")
    assert response.status_code == 200
    assert response.json()["status"] == "memory_cleared"
