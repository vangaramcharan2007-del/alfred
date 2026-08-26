"""Tests for AEGIS's local-first resilience and privacy additions."""

import sqlite3

from aegis_memory import AegisMemory
from aegis_resilience import EnvironmentalReading, assess_environment
from main import app
from fastapi.testclient import TestClient


def test_offline_environmental_assessment_combines_heat_air_and_flood_risk():
    assessment = assess_environment(
        EnvironmentalReading(
            ambient_temperature_c=43.0,
            humidity_percent=70.0,
            aqi=340,
            flood_warning=True,
        )
    )
    assert assessment.level == "HIGH"
    assert assessment.emergency_mode is True
    assert {"EXTREME_HEAT_STRESS", "SEVERE_AIR_QUALITY", "FLOOD_DISRUPTION"}.issubset(assessment.hazards)


def test_sensitive_profile_and_conversation_fields_are_encrypted_at_rest(tmp_path):
    database = tmp_path / "aegis.db"
    memory = AegisMemory(str(database))
    patient = memory.add_new_patient(name="Asha Rao", allergies="Penicillin", emergency_contact="9999999999")
    memory.add_conversation("user", "My medical note is private")
    memory.close()

    raw_connection = sqlite3.connect(database)
    raw_name = raw_connection.execute("SELECT name FROM patient_profile WHERE patient_uid = ?", (patient["patient_uid"],)).fetchone()[0]
    raw_message = raw_connection.execute("SELECT content FROM memory_context ORDER BY id DESC LIMIT 1").fetchone()[0]
    raw_connection.close()
    assert raw_name.startswith("enc:v1:")
    assert raw_message.startswith("enc:v1:")


def test_telemetry_returns_a_local_environmental_alert_without_remote_sharing():
    with TestClient(app) as client:
        response = client.post(
            "/ingest-telemetry",
            json={
                "heart_rate": 75,
                "temperature": 36.8,
                "environment": {"ambient_temperature_c": 43, "humidity_percent": 70, "aqi": 330, "flood_warning": False},
            },
        )
    assert response.status_code == 200
    result = response.json()
    assert result["risk_score"] == "High"
    assert result["environmental_assessment"]["level"] == "HIGH"
    assert result["clinical_notice"].startswith("Wellness decision support")
