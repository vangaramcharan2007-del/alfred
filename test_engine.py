"""
Unit and Integration Tests for AEGIS Engine, FastAPI Ingestion, and Ollama LLM Service.
Tests physiological anomaly detection logic, API escalation workflows, and streaming advice.
"""

import asyncio
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from aegis_engine import AnomalyDetector, EvaluationResult
from main import app, dispatch_webhook_escalation
from baymax_service import generate_explanation


@pytest.fixture
def detector():
    """Fixture providing an initialized and trained AnomalyDetector instance."""
    return AnomalyDetector(random_state=42)


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
    
    # Assert risk_score is Normal
    assert result.risk_score == "Normal"
    # Assert is_anomaly is False
    assert result.is_anomaly is False
    
    # Also verify unpacking compatibility
    risk_score, is_anomaly = result[:2]
    assert risk_score == "Normal"
    assert is_anomaly is False


def test_evaluate_critical_anomaly_high(detector):
    """Verify that evaluate(130, 39.5) returns High risk score and is_anomaly=True."""
    result = detector.evaluate(130, 39.5)
    
    # Assert risk_score is High
    assert result.risk_score == "High"
    # Assert is_anomaly is True
    assert result.is_anomaly is True

    # Also verify unpacking compatibility
    risk_score, is_anomaly = result[:2]
    assert risk_score == "High"
    assert is_anomaly is True


def test_evaluate_various_baselines(detector):
    """Verify normal range boundaries."""
    # Test lower normal bound
    res_low = detector.evaluate(62, 36.6)
    assert res_low.risk_score == "Normal"
    assert res_low.is_anomaly is False

    # Test upper normal bound
    res_high_norm = detector.evaluate(78, 37.4)
    assert res_high_norm.risk_score == "Normal"
    assert res_high_norm.is_anomaly is False


def test_evaluate_extreme_anomalies(detector):
    """Verify extreme anomaly values."""
    # Extreme tachycardia + hyperthermia
    res_extreme = detector.evaluate(160, 40.2)
    assert res_extreme.risk_score == "High"
    assert res_extreme.is_anomaly is True

    # Extreme bradycardia / hypothermia
    res_brady = detector.evaluate(35, 34.0)
    assert res_extreme.risk_score == "High"


# ==========================================
# 2. FastAPI Ingestion & Escalation Tests
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
    assert data["heart_rate"] == 72
    assert data["temperature"] == 36.8


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
        asyncio.run(dispatch_webhook_escalation(heart_rate=135, temperature=39.5, risk_score="High"))


def test_api_telemetry_history(client):
    """Verify GET /telemetry-history returns historical readings."""
    response = client.get("/telemetry-history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "heart_rate" in data[0]
    assert "temperature" in data[0]



# ==========================================
# 3. Phase 2: Ollama LLM /explain-risk Tests
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
        assert "hydrate" in streamed_content


def test_api_explain_risk_offline_fallback(client):
    """Verify POST /explain-risk gracefully falls back when Ollama daemon is offline."""
    payload = {"heart_rate": 135, "temperature": 39.5, "risk_score": "High"}

    with patch("ollama.AsyncClient.chat", side_effect=Exception("Ollama connection refused")):
        response = client.post("/explain-risk", json=payload)

        assert response.status_code == 200
        streamed_content = response.text
        assert "Critical physiological elevation detected" in streamed_content
        assert "rest immediately" in streamed_content


def test_api_explain_risk_normal_telemetry(client):
    """Verify POST /explain-risk handles normal telemetry correctly."""
    payload = {"heart_rate": 72, "temperature": 36.8}

    with patch("ollama.AsyncClient.chat", side_effect=Exception("Ollama connection refused")):
        response = client.post("/explain-risk", json=payload)

        assert response.status_code == 200
        assert "Vitals appear stable" in response.text
