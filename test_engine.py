"""
Unit and Integration Tests for AEGIS Engine, WESAD Multi-Modal Classifier with XAI,
FastAPI Ingestion, Pure Ollama LLM Service, Baymax Voice Companion,
Real-Time Computer Vision with Syncope Fall Detection, Persistent SQLite Memory & EHR Layer,
Offline Medical RAG, and HL7/FHIR Clinical Triage Handover Export.
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
from fhir_exporter import generate_fhir_bundle, generate_html_triage_report
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
# 2. WESAD Classifier & Explainable AI (XAI) Tests
# ==========================================

def test_wesad_classifier_normal_and_stress(wesad_detector):
    """Verify WESAD 5-feature classification and XAI output."""
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
    assert len(normal_res.feature_contributions) == 5

    stress_res = wesad_detector.evaluate(
        heart_rate=135.0,
        rmssd=15.0,
        temperature=39.5,
        temp_slope=0.15,
        eda=8.5
    )
    assert stress_res.risk_level == "HIGH RISK"
    assert stress_res.is_anomaly is True
    assert stress_res.top_driver is not None


def test_xai_attribution_math_properties(wesad_detector):
    """Verify that XAI feature contributions sum to 100%."""
    xai = wesad_detector.calculate_xai_attributions(
        hr=120.0,
        rmssd=20.0,
        temp=39.0,
        temp_slope=0.10,
        eda=6.0
    )
    total_pct = sum(xai["contributions"].values())
    assert 99.0 <= total_pct <= 101.0
    assert xai["top_driver"] in xai["contributions"]


# ==========================================
# 3. Computer Vision & Syncope Fall Detection Tests
# ==========================================

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


def test_vital_scanner_syncope_head_tilt():
    """Verify head tilt roll and syncope collapse detection."""
    scanner = VitalScanner()

    # Normal upright posture
    upright_eyes = [(100, 100, 20, 20), (140, 100, 20, 20)]
    tilt_upright, syncope_upright, status_upright = scanner.calculate_head_tilt_and_syncope(
        eyes=upright_eyes,
        face_box=(80, 80, 100, 100),
        frame_shape=(480, 640)
    )
    assert tilt_upright < 10.0
    assert syncope_upright is False
    assert status_upright == "ERECT_NOMINAL"

    # Acute syncope collapse tilt (> 35 deg)
    tilted_eyes = [(100, 80, 20, 20), (140, 130, 20, 20)]
    tilt_severe, syncope_severe, status_severe = scanner.calculate_head_tilt_and_syncope(
        eyes=tilted_eyes,
        face_box=(80, 80, 100, 100),
        frame_shape=(480, 640)
    )
    assert tilt_severe > 35.0
    assert syncope_severe is True
    assert status_severe == "SYNCOPE_COLLAPSE_DETECTED"


def test_vital_scanner_process_frame():
    """Verify VitalScanner processes image frame cleanly."""
    scanner = VitalScanner()
    test_frame = np.full((480, 640, 3), 120, dtype=np.uint8)
    result = scanner.process_frame(test_frame, draw_overlay=True)

    assert "ear" in result
    assert "is_fatigued" in result
    assert "head_tilt_deg" in result
    assert "syncope_detected" in result
    assert "posture_status" in result


# ==========================================
# 4. HL7 / FHIR Clinical Handover Exporter Tests
# ==========================================

def test_fhir_bundle_generation():
    """Verify HL7 FHIR v4.0.1 Bundle JSON generation."""
    patient_mock = {
        "patient_uid": "PAT-RAM-2026",
        "name": "Ramcharan",
        "gender": "Male",
        "blood_type": "O+",
        "allergies": "Ibuprofen, NSAIDs"
    }
    vitals_mock = {
        "heart_rate": 105.0,
        "temperature": 39.2,
        "rmssd": 25.0,
        "eda": 4.5,
        "ear": 0.28,
        "posture_status": "ERECT_NOMINAL"
    }
    proto_mock = {
        "protocol_id": "CLIN-PROT-FEV-01",
        "title": "Acute Febrile Response & Hyperthermia Protocol",
        "first_line_action": "Cool ambient hydration",
        "pharmacotherapy": {"first_line": "Paracetamol 500mg"}
    }

    bundle = generate_fhir_bundle(
        patient_profile=patient_mock,
        vitals=vitals_mock,
        baseline={"avg_hr": 72.0},
        matched_protocol=proto_mock
    )

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "document"
    assert len(bundle["entry"]) >= 4

    resource_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    assert "Patient" in resource_types
    assert "AllergyIntolerance" in resource_types
    assert "Observation" in resource_types
    assert "CarePlan" in resource_types


def test_html_triage_report_generation():
    """Verify printable Emergency Triage Handover HTML generation."""
    patient_mock = {
        "patient_uid": "PAT-RAM-2026",
        "name": "Ramcharan",
        "age": 24,
        "gender": "Male",
        "blood_type": "O+",
        "allergies": "Ibuprofen, NSAIDs"
    }
    vitals_mock = {"heart_rate": 105, "temperature": 39.2, "rmssd": 25, "eda": 4.5, "ear": 0.28}
    html = generate_html_triage_report(patient_profile=patient_mock, vitals=vitals_mock, baseline={"avg_hr": 72.0})

    assert "AEGIS MEDICAL WORKSTATION // EMERGENCY TRIAGE HANDOVER" in html
    assert "Ramcharan" in html
    assert "Ibuprofen" in html


def test_api_fhir_and_triage_endpoints(client):
    """Verify GET /clinical-handover/fhir and /clinical-handover/triage-report endpoints."""
    res_fhir = client.get("/clinical-handover/fhir")
    assert res_fhir.status_code == 200
    assert res_fhir.json()["resourceType"] == "Bundle"

    res_html = client.get("/clinical-handover/triage-report")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]


# ==========================================
# 5. EHR Memory, Offline RAG & Multi-Turn Tests
# ==========================================

def test_ehr_patient_profile_crud(memory):
    """Verify EHR patient profile initialization and updates."""
    profile = memory.get_patient_profile()
    assert profile["name"] == "Ramcharan"
    assert profile["blood_type"] == "O+"
    assert "ibuprofen" in profile["allergies_list"]


def test_medical_rag_protocol_retrieval(medical_rag_engine):
    """Verify OfflineMedicalRAG retrieves clinical guidelines."""
    fev = medical_rag_engine.retrieve_protocol("spiking high fever and chills")
    assert fev is not None
    assert fev["protocol_id"] == "CLIN-PROT-FEV-01"

    mental = medical_rag_engine.retrieve_protocol("So my frnd is suffering from depression")
    assert mental is not None
    assert mental["protocol_id"] == "CLIN-PROT-MENTAL-07"

    adhd = medical_rag_engine.retrieve_protocol("adhd good or bad")
    assert adhd is not None
    assert adhd["protocol_id"] == "CLIN-PROT-NEURO-08"


def test_third_party_query_detection():
    """Verify third-party friend inquiry detection."""
    assert is_third_party_query("So my frnd is suffering from depression") is True
    assert is_third_party_query("What can I take for my headache?") is False


def test_medical_rag_drug_safety_check(medical_rag_engine):
    """Verify drug allergy contraindication flagging."""
    allergies = ["ibuprofen", "nsaids"]
    conflict = medical_rag_engine.evaluate_drug_safety("Should I take some Ibuprofen?", allergies)
    assert conflict["is_contraindicated"] is True
    assert "Paracetamol" in conflict["safe_alternative"]


# ==========================================
# 6. FastAPI Ingestion & Companion Flow Tests
# ==========================================

def test_api_root_endpoint(client):
    """Verify health root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["fhir_interoperability"] == "HL7 FHIR v4.0.1 Enabled"


def test_api_ingest_telemetry_normal(client):
    """Verify POST /ingest-telemetry for normal reading."""
    payload = {"heart_rate": 72, "temperature": 36.8}
    response = client.post("/ingest-telemetry", json=payload)
    assert response.status_code == 200
    assert response.json()["risk_score"] == "Normal"


@patch("main.dispatch_webhook_escalation")
def test_api_companion_interact_with_syncope(mock_dispatch, client):
    """Verify POST /companion-interact handles syncope collapse."""
    payload = {
        "user_speech": "I have collapsed and feel faint.",
        "heart_rate": 125.0,
        "rmssd": 18.0,
        "temperature": 38.8,
        "temp_slope": 0.10,
        "eda": 6.5,
        "ear": 0.15,
        "head_tilt_deg": 44.0,
        "syncope_detected": True,
        "posture_status": "SYNCOPE_COLLAPSE_DETECTED"
    }

    with patch("ollama.AsyncClient.chat"):
        response = client.post("/companion-interact", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["syncope_detected"] is True
        assert data["posture_status"] == "SYNCOPE_COLLAPSE_DETECTED"
        assert len(data["feature_contributions"]) == 5
        assert data["escalated"] is True


# ==========================================
# 7. Next-Level Point-of-Care Diagnostics & Satellite SOS Tests
# ==========================================

def test_anemia_pallor_estimation(client):
    """Verify optical conjunctival colorimetry anemia screening."""
    payload = {"erythema_index": 2.8, "r_channel_mean": 150.0}
    response = client.post("/diagnostics/anemia", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "estimated_hemoglobin_g_dl" in data
    assert data["estimated_hemoglobin_g_dl"] >= 12.0
    assert data["status"] == "OPTIMAL_HEMOGLOBIN"


def test_cough_acoustic_analysis(client):
    """Verify acoustic cough frequency spectrogram analyzer."""
    payload = {"spectral_flux": 0.75, "peak_frequency_hz": 1550.0}
    response = client.post("/diagnostics/cough", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["acoustic_pattern"] == "BRONCHIAL_WHEEZE_ASTHMA"
    assert data["severity"] == "HIGH"


def test_qsofa_sepsis_cds_evaluation(client):
    """Verify qSOFA early sepsis trajectory prediction."""
    payload = {
        "heart_rate": 120.0,
        "temperature": 39.5,
        "temp_slope": 0.15,
        "syncope_detected": True,
        "respiratory_rate": 26.0,
        "systolic_bp": 85.0
    }
    response = client.post("/diagnostics/qsofa", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["qsofa_score"] == 3
    assert data["shock_probability"] > 0.70
    assert data["triage_category"] == "HIGH_SEPSIS_RISK"


def test_satellite_sos_micro_packet_generator(client):
    """Verify 140-byte compact satellite SOS telemetry generator."""
    payload = {"patient_uid": "PAT-RAM-2026", "gps_coords": "17.9689 N, 79.5941 E"}
    response = client.post("/diagnostics/satellite-sos", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["byte_size"] <= 140
    assert data["satellite_compatible"] is True
    assert data["micro_packet"].startswith("AEGIS!")


# ==========================================
# 8. Advanced Clinical Scanner Tests
# ==========================================

def test_medicine_ocr_scanner_identifies_paracetamol(client):
    """Verify medicine strip OCR identifies Paracetamol and detects dosage."""
    payload = {"ocr_text": "PARACETAMOL 500mg Tablets IP"}
    response = client.post("/scanner/medicine-ocr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["drug_identified"] is True
    assert "Paracetamol" in data["drug_name"]
    assert data["detected_dosage"] == "500mg"
    assert data["allergy_alert"] is False


def test_medicine_ocr_scanner_flags_ibuprofen_allergy(client):
    """Verify medicine OCR flags NSAID allergy for Ibuprofen strip on allergic patient."""
    payload = {"ocr_text": "IBUPROFEN 400mg Film Coated Tablets"}
    response = client.post("/scanner/medicine-ocr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["drug_identified"] is True
    assert data["allergy_alert"] is True
    assert data["status"] == "ALLERGY_DANGER"
    assert len(data["allergy_warnings"]) > 0


def test_abha_qr_decoder_parses_abha_number(client):
    """Verify ABHA QR decoder extracts 14-digit health ID."""
    payload = {"qr_payload": "91-1234-5678-9012 name: Ramcharan gender: M dob: 15-03-2002 O+"}
    response = client.post("/scanner/abha-qr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DECODED"
    assert data["abha_number"] == "91-1234-5678-9012"
    assert data["name"] == "Ramcharan"
    assert data["gender"] == "Male"
    assert data["blood_group"] == "O+"


def test_abha_qr_decoder_handles_json_payload(client):
    """Verify ABHA QR decoder handles structured JSON ABHA payload."""
    import json
    abha_json = json.dumps({"hidn": "91-9876-5432-1098", "name": "Giri", "gender": "Female", "dob": "10-08-2004", "bloodGroup": "A+"})
    payload = {"qr_payload": abha_json}
    response = client.post("/scanner/abha-qr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DECODED"
    assert data["abha_number"] == "91-9876-5432-1098"
    assert data["name"] == "Giri"
    assert data["gender"] == "Female"


def test_chest_xray_normal_classification(client):
    """Verify normal chest X-ray classification."""
    payload = {"lung_opacity_ratio": 0.10, "upper_lobe_density": 0.08, "lower_lobe_density": 0.12, "cardiac_silhouette_ratio": 0.45}
    response = client.post("/scanner/chest-xray", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "NORMAL"
    assert data["severity"] == "CLEAR"


def test_chest_xray_pneumonia_classification(client):
    """Verify bacterial pneumonia detection with high lower lobe opacity."""
    payload = {"lung_opacity_ratio": 0.42, "upper_lobe_density": 0.10, "lower_lobe_density": 0.45, "cardiac_silhouette_ratio": 0.48}
    response = client.post("/scanner/chest-xray", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "BACTERIAL_PNEUMONIA"
    assert data["severity"] == "HIGH"
    assert len(data["findings"]) > 0
    assert len(data["heatmap_zones"]) > 0


def test_chest_xray_tuberculosis_classification(client):
    """Verify pulmonary TB detection with high upper lobe density."""
    payload = {"lung_opacity_ratio": 0.30, "upper_lobe_density": 0.45, "lower_lobe_density": 0.12, "cardiac_silhouette_ratio": 0.46}
    response = client.post("/scanner/chest-xray", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "PULMONARY_TUBERCULOSIS"
    assert data["severity"] == "HIGH"


def test_hand_gesture_organ_targeting(client):
    """Verify hand gesture raycast maps to correct organ zone."""
    payload = {"index_tip_x": 0.45, "index_tip_y": 0.32, "wrist_x": 0.45, "wrist_y": 0.7, "hand_detected": True, "is_pointing": True}
    response = client.post("/scanner/hand-gesture", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ORGAN_TARGETED"
    assert data["organ"] == "Cardiovascular Heart"
    assert data["disease_preset"] == "CARDIAC_TACHYCARDIA"


def test_hand_gesture_no_hand_detected(client):
    """Verify graceful handling when no hand is detected."""
    payload = {"index_tip_x": 0.5, "index_tip_y": 0.5, "wrist_x": 0.5, "wrist_y": 0.7, "hand_detected": False, "is_pointing": False}
    response = client.post("/scanner/hand-gesture", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NO_HAND_DETECTED"

