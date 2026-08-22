"""
Unit and Integration Tests for AEGIS Engine, WESAD Multi-Modal Classifier,
FastAPI Ingestion, Ollama LLM Service, and Baymax Voice Companion.
"""

import asyncio
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from aegis_engine import (
    AnomalyDetector,
    EvaluationResult,
    WESADPhysiologicalDetector,
    WESADEvaluationResult
)
from main import app, dispatch_webhook_escalation
from baymax_service import generate_explanation


@pytest.fixture
def detector():
    """Fixture providing an initialized and trained AnomalyDetector instance."""
    return AnomalyDetector(random_state=42)


@pytest.fixture
def wesad_detector():
    """Fixture providing an initialized WESAD physiological detector."""
    return WESADPhysiologicalDetector()


@pytest.fixture
def client():
    """Test client for the FastAPI backend."""
    with TestClient(app) as test_client:
        yield test_client


# ==========================================
# 1. ML Core Evaluation Tests (Task 1 & 4)
# ==========================================

def test_evaluate_normal_baseline(detector):
    """Verify that evaluate(70, 37.0) returns Normal risk score and is_anomaly=False."""
    result = detector.evaluate(70, 37.0)
    assert result.risk_score == "Normal"
    assert result.is_anomaly is False
    
    risk_score, is_anomaly = result[:2]
    assert risk_score == "Normal"
    assert is_anomaly is False


def test_evaluate_critical_anomaly_high(detector):
    """Verify that evaluate(130, 39.5) returns High risk score and is_anomaly=True."""
    result = detector.evaluate(130, 39.5)
    assert result.risk_score == "High"
    assert result.is_anomaly is True

    risk_score, is_anomaly = result[:2]
    assert risk_score == "High"
    assert is_anomaly is True


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
    # 1. Healthy Resting: HR=72, RMSSD=45ms, Temp=36.8°C, Slope=0.0, EDA=1.5
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

    # 2. Severe Stress / Heat Stroke: HR=135, RMSSD=15ms, Temp=39.5°C, Slope=0.15, EDA=8.5
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
# 4. Ollama LLM /explain-risk Tests
# ==========================================

async def mock_async_chat_stream(*args, **kwargs):
    """Mock async generator yielding Ollama chat stream chunks."""
    chunks = [
        {"message": {"content": "Critical physiological elevation detected. "}},
        {"message": {"content": "Please rest immediately in a cool area and hydrate."}}
    ]
    for chunk in chunks:
        yield chunk


def test_api_explain_risk_with_mocked_ollama(client):
    """Verify POST /explain-risk returns HTTP 200 and streams Ollama advice."""
    payload = {"heart_rate": 135, "temperature": 39.5}

    with patch("ollama.AsyncClient.chat", side_effect=lambda **kw: mock_async_chat_stream()):
        response = client.post("/explain-risk", json=payload)

        assert response.status_code == 200
        streamed_content = response.text
        assert "Critical physiological elevation detected" in streamed_content


def test_api_explain_risk_offline_fallback(client):
    """Verify POST /explain-risk gracefully falls back when Ollama daemon is offline."""
    payload = {"heart_rate": 135, "temperature": 39.5, "risk_score": "High"}

    with patch("ollama.AsyncClient.chat", side_effect=Exception("Ollama connection refused")):
        response = client.post("/explain-risk", json=payload)

        assert response.status_code == 200
        assert "Critical physiological elevation detected" in response.text


# ==========================================
# 5. Baymax Companion Voice Interaction Tests
# ==========================================

def test_api_companion_interact_normal_speech(client):
    """Verify POST /companion-interact handles routine user speech."""
    payload = {
        "user_speech": "How are my vitals doing today Baymax?",
        "heart_rate": 72.0,
        "rmssd": 48.0,
        "temperature": 36.8,
        "temp_slope": 0.0,
        "eda": 1.4
    }

    response = client.post("/companion-interact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is False
    assert data["risk_level"] == "OPTIMAL"
    assert len(data["reply_text"]) > 0


@patch("main.dispatch_webhook_escalation")
def test_api_companion_interact_anomaly_takeover(mock_dispatch, client):
    """Verify POST /companion-interact detects acute anomaly and triggers escalation."""
    payload = {
        "user_speech": "I feel extremely dizzy and overheated.",
        "heart_rate": 135.0,
        "rmssd": 15.0,
        "temperature": 39.5,
        "temp_slope": 0.15,
        "eda": 8.5
    }

    response = client.post("/companion-interact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is True
    assert data["risk_level"] == "HIGH RISK"
    assert data["escalated"] is True
    assert "cooldown protocol" in data["reply_text"].lower() or "thermal" in data["reply_text"].lower() or "acute" in data["reply_text"].lower()
