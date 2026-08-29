"""
AEGIS Comprehensive Test Suite for SIH 2026.
Covers: Engine, Scanners, Diagnostics, Resilience, Privacy, Mesh, MultiAgent, Audio, Memory, SIH Evaluator.
"""
import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════
# 1. aegis_engine.py
# ═══════════════════════════════════════════════════════════════════════

class TestAnomalyDetector:
    def test_normal_vitals(self):
        from aegis_engine import AnomalyDetector
        det = AnomalyDetector(); det.train_baseline()
        r = det.evaluate(hr=72, temp=36.8)
        assert r.risk_score == "Normal" and r.is_anomaly is False

    def test_extreme_vitals(self):
        from aegis_engine import AnomalyDetector
        det = AnomalyDetector(); det.train_baseline()
        r = det.evaluate(hr=180, temp=41.0)
        assert r.risk_score == "High" and r.is_anomaly is True

    def test_to_dict(self):
        from aegis_engine import EvaluationResult
        assert "risk_score" in EvaluationResult("Normal", False, 0.5).to_dict()


class TestWESADDetector:
    def test_normal_is_optimal(self):
        from aegis_engine import WESADPhysiologicalDetector
        r = WESADPhysiologicalDetector().evaluate(72, 45, 36.8, 0.0, 1.5)
        assert r.risk_level == "OPTIMAL" and r.is_anomaly is False

    def test_extreme_is_high_risk(self):
        from aegis_engine import WESADPhysiologicalDetector
        r = WESADPhysiologicalDetector().evaluate(160, 8, 40.5, 0.8, 18.0)
        assert "HIGH" in r.risk_level.upper() and r.is_anomaly is True

    def test_xai_contributions_sum_near_100(self):
        from aegis_engine import WESADPhysiologicalDetector
        attr = WESADPhysiologicalDetector().calculate_xai_attributions(120, 15, 39, 0.5, 10)
        total = sum(attr["contributions"].values())
        assert 98 <= total <= 102
        assert "top_driver" in attr

    def test_to_dict(self):
        from aegis_engine import WESADPhysiologicalDetector
        d = WESADPhysiologicalDetector().evaluate(72, 45, 36.8, 0.0, 1.5).to_dict()
        assert "risk_level" in d and "feature_contributions" in d


# ═══════════════════════════════════════════════════════════════════════
# 2. aegis_resilience.py
# ═══════════════════════════════════════════════════════════════════════

class TestResilience:
    def test_normal(self):
        from aegis_resilience import EnvironmentalReading, assess_environment
        r = assess_environment(EnvironmentalReading(28.0, 50.0, 45, False))
        assert r.level == "NORMAL" and r.emergency_mode is False

    def test_extreme_heat(self):
        from aegis_resilience import EnvironmentalReading, assess_environment
        r = assess_environment(EnvironmentalReading(43.0, 70.0, 50, False))
        assert r.level in ("ELEVATED", "HIGH") and r.heat_index_c > 41

    def test_severe_aqi(self):
        from aegis_resilience import EnvironmentalReading, assess_environment
        r = assess_environment(EnvironmentalReading(30.0, 40.0, 330, False))
        assert any("AIR" in h.upper() for h in r.hazards)

    def test_flood(self):
        from aegis_resilience import EnvironmentalReading, assess_environment
        r = assess_environment(EnvironmentalReading(30.0, 50.0, 50, True))
        assert any("FLOOD" in h.upper() for h in r.hazards)

    def test_combined_disaster(self):
        from aegis_resilience import EnvironmentalReading, assess_environment
        r = assess_environment(EnvironmentalReading(43.0, 70.0, 330, True))
        assert r.level == "HIGH" and r.emergency_mode is True and len(r.hazards) >= 2

    def test_to_dict(self):
        from aegis_resilience import EnvironmentalReading, assess_environment
        assert "level" in assess_environment(EnvironmentalReading(28, 50, 45, False)).to_dict()


# ═══════════════════════════════════════════════════════════════════════
# 3. aegis_privacy.py
# ═══════════════════════════════════════════════════════════════════════

class TestPrivacy:
    def _make_protector(self):
        f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        return f.name

    def test_roundtrip(self):
        from aegis_privacy import LocalDataProtector
        p = self._make_protector()
        lp = LocalDataProtector(p)
        enc = lp.encrypt("secret data")
        assert enc.startswith("enc:v1:") and lp.decrypt(enc) == "secret data"

    def test_none(self):
        from aegis_privacy import LocalDataProtector
        lp = LocalDataProtector(self._make_protector())
        assert lp.encrypt(None) is None and lp.decrypt(None) is None

    def test_idempotent(self):
        from aegis_privacy import LocalDataProtector
        lp = LocalDataProtector(self._make_protector())
        enc = lp.encrypt("data"); enc2 = lp.encrypt(enc)
        assert lp.decrypt(enc2) == "data"


# ═══════════════════════════════════════════════════════════════════════
# 4. aegis_scanners.py
# ═══════════════════════════════════════════════════════════════════════

class TestScanners:
    def test_paracetamol(self):
        from aegis_scanners import scan_medicine_strip
        r = scan_medicine_strip("Paracetamol 650mg")
        assert r["status"] == "IDENTIFIED"

    def test_allergy_flag(self):
        from aegis_scanners import scan_medicine_strip
        r = scan_medicine_strip("Ibuprofen 400mg", patient_allergies=["Ibuprofen"])
        assert "allergy" in json.dumps(r).lower() or "contraind" in json.dumps(r).lower()

    def test_unknown_drug(self):
        from aegis_scanners import scan_medicine_strip
        assert scan_medicine_strip("XyzDrug123") is not None

    def test_abha_decode(self):
        from aegis_scanners import decode_abha_qr
        payload = json.dumps({"hidn": "91-1234-5678-9012", "name": "Test", "gender": "M", "dob": "1990-01-01"})
        r = decode_abha_qr(payload)
        assert r["status"] == "DECODED"

    def test_xray_normal(self):
        from aegis_scanners import classify_chest_xray
        r = classify_chest_xray(128, 0.08, 0.7, 0.42, 0.08, 0.10, False)
        assert r is not None

    def test_xray_abnormal(self):
        from aegis_scanners import classify_chest_xray
        r = classify_chest_xray(180, 0.55, 0.3, 0.58, 0.45, 0.50, True)
        assert r is not None

    def test_organ_raycast(self):
        from aegis_scanners import map_hand_to_organ
        r = map_hand_to_organ(0.5, 0.35, 0.5, 0.7, True, True)
        assert r["status"] == "ORGAN_TARGETED"

    def test_no_hand(self):
        from aegis_scanners import map_hand_to_organ
        r = map_hand_to_organ(0.5, 0.5, 0.5, 0.7, False, False)
        assert r["status"] != "ORGAN_TARGETED"


# ═══════════════════════════════════════════════════════════════════════
# 5. aegis_diagnostics.py
# ═══════════════════════════════════════════════════════════════════════

class TestDiagnostics:
    def test_anemia_normal(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().estimate_anemia_from_pallor(0.7, 160.0)
        assert r["estimated_hemoglobin_g_dl"] >= 11.0

    def test_anemia_severe(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().estimate_anemia_from_pallor(0.15, 80.0)
        assert r["estimated_hemoglobin_g_dl"] < 10.0

    def test_cough_analysis(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().analyze_cough_acoustics(0.9, 800.0)
        assert "acoustic_pattern" in r

    def test_clear_breathing(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().analyze_cough_acoustics(0.1, 200.0)
        assert "CLEAR" in r["acoustic_pattern"].upper() or "BENIGN" in r["acoustic_pattern"].upper()

    def test_qsofa_normal(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().evaluate_qsofa_sepsis_trajectory(72, 36.8, 0.0, False, 16, 120)
        assert r["qsofa_score"] <= 1

    def test_qsofa_critical(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().evaluate_qsofa_sepsis_trajectory(135, 40.2, 0.7, True, 30, 75)
        assert r["qsofa_score"] >= 2

    def test_sos_packet(self):
        from aegis_diagnostics import MultimodalDiagnostics
        r = MultimodalDiagnostics().generate_satellite_sos_packet("PAT-RAM-2026", "O+", 135, 40.1, 3, 0.85)
        assert "micro_packet" in r
        assert r["satellite_compatible"] is True


# ═══════════════════════════════════════════════════════════════════════
# 6. aegis_mesh_sync.py
# ═══════════════════════════════════════════════════════════════════════

class TestMesh:
    def test_peers(self):
        from aegis_mesh_sync import AegisMeshManager
        s = AegisMeshManager().get_mesh_state()
        assert s.connected_peers_count >= 3

    def test_broadcast(self):
        from aegis_mesh_sync import AegisMeshManager
        r = AegisMeshManager().broadcast_sync("PATIENT_ADMISSION", {"uid": "TEST"})
        assert r["status"] == "BROADCAST_REPLICATED"
        assert r["peers_reached"] >= 1

    def test_checksum(self):
        from aegis_mesh_sync import AegisMeshManager
        r = AegisMeshManager().broadcast_sync("VITALS", {"hr": 72})
        assert len(r["checksum"]) >= 8


# ═══════════════════════════════════════════════════════════════════════
# 7. aegis_multiagent.py
# ═══════════════════════════════════════════════════════════════════════

class TestMultiAgent:
    V = {"heart_rate": 135, "rmssd": 12, "temperature": 39.8, "temp_slope": 0.6,
         "eda": 14.0, "syncope_detected": True, "ear": 0.18}
    E = {"patient_uid": "PAT-RAM-2026", "name": "Ramesh", "age": 58, "gender": "Male",
         "blood_type": "O+", "allergies": "Ibuprofen, Aspirin",
         "chronic_conditions": "Hypertension", "active_medications": "Amlodipine 5mg"}

    def test_cardiology(self):
        from aegis_multiagent import CardiologyAgent
        r = CardiologyAgent().evaluate(self.V, self.E)
        assert r.urgency_tier in ("RED", "YELLOW", "GREEN") and len(r.findings) > 0

    def test_pharmacology_allergy(self):
        from aegis_multiagent import PharmacologyAgent
        r = PharmacologyAgent().evaluate("Ibuprofen 400mg", self.E, self.V)
        assert "allergy" in " ".join(r.findings).lower() or r.urgency_tier == "RED"

    def test_critical_care(self):
        from aegis_multiagent import CriticalCareTriageAgent
        r = CriticalCareTriageAgent().evaluate(self.V, self.E)
        assert r.urgency_tier in ("RED", "YELLOW")

    def test_board_consensus(self):
        from aegis_multiagent import ClinicalBoardSynthesizer
        c = ClinicalBoardSynthesizer().convene_board("Patient collapsed", self.V, self.E)
        assert c.triage_tier in ("RED", "YELLOW", "GREEN")
        assert len(c.specialist_assessments) == 3


# ═══════════════════════════════════════════════════════════════════════
# 8. aegis_memory.py
# ═══════════════════════════════════════════════════════════════════════

class TestMemory:
    def test_vital_insert_retrieve(self):
        from aegis_memory import AegisMemory
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            m = AegisMemory(f.name)
            m.insert_vital(72.0, 0.32, False, 0.5)
            assert m.get_latest_vital()["heart_rate"] == 72.0
            m.close()

    def test_patient_crud(self):
        from aegis_memory import AegisMemory
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            m = AegisMemory(f.name)
            r = m.add_new_patient(name="Test", age=30, gender="F", blood_type="A+", allergies="Pen")
            assert "patient_uid" in r
            p = m.get_patient_profile(r["patient_uid"])
            assert p["name"] == "Test"
            m.close()

    def test_encrypted_conversation(self):
        from aegis_memory import AegisMemory
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            m = AegisMemory(f.name)
            m.add_conversation("user", "chest pain")
            ctx = m.get_conversation_context(5)
            assert len(ctx) >= 1 and "chest pain" in ctx[-1]["content"]
            m.close()

    def test_fhir_queue(self):
        from aegis_memory import AegisMemory
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            m = AegisMemory(f.name)
            patients = m.list_all_patients()
            uid = patients[0]["patient_uid"] if patients else "PAT-TEST"
            bid = m.queue_fhir_bundle(uid, {"resourceType": "Bundle"})
            assert isinstance(bid, str) and "BUNDLE" in bid
            assert m.get_sync_queue_status()["pending_offline_count"] >= 1
            m.close()


# ═══════════════════════════════════════════════════════════════════════
# 9. sih_evaluator.py
# ═══════════════════════════════════════════════════════════════════════

class TestSIHEvaluator:
    def test_calibration_flow(self):
        from sih_evaluator import PersonalBaselineCalibrator
        c = PersonalBaselineCalibrator()
        assert c.start_60s_calibration()["status"] == "CALIBRATION_INITIATED"
        assert c.complete_calibration(72, 36.8, 45, 1.5)["status"] == "CALIBRATION_LOCKED"

    def test_deviation_normal(self):
        from sih_evaluator import PersonalBaselineCalibrator
        c = PersonalBaselineCalibrator()
        c.complete_calibration(72, 36.8, 45, 1.5)
        r = c.evaluate_deviation(74, 36.9, 43, 1.6, 28, 50, 0)
        assert r["total_risk_score"] < 5.0

    def test_deviation_extreme(self):
        from sih_evaluator import PersonalBaselineCalibrator
        c = PersonalBaselineCalibrator()
        c.complete_calibration(72, 36.8, 45, 1.5)
        r = c.evaluate_deviation(140, 39.5, 10, 16, 44, 350, 80)
        assert r["total_risk_score"] > 5.0

    def test_demo_stages(self):
        from sih_evaluator import PersonalBaselineCalibrator
        c = PersonalBaselineCalibrator()
        for i in range(1, 5):
            assert c.generate_sih_demo_stage(i) is not None


# ═══════════════════════════════════════════════════════════════════════
# 10. aegis_gov_api.py
# ═══════════════════════════════════════════════════════════════════════

class TestGovAPI:
    def test_abha_validation(self):
        from aegis_gov_api import verify_abha_number
        r = verify_abha_number("91-1234-5678-9012")
        assert r.status == "success"

    def test_abha_invalid(self):
        from aegis_gov_api import verify_abha_number
        r = verify_abha_number("123")
        assert r.verified is False

    def test_ndma_alerts(self):
        from aegis_gov_api import fetch_ndma_alerts
        r = fetch_ndma_alerts("telangana")
        assert r.total_active >= 1  # Cached alerts

    def test_imd_weather(self):
        from aegis_gov_api import fetch_imd_weather
        r = fetch_imd_weather("hyderabad")
        assert r.temperature_c > 0

    def test_situation_report(self):
        from aegis_gov_api import get_government_situation_report
        r = get_government_situation_report("hyderabad", "telangana")
        assert "weather" in r and "disaster_alerts" in r


# ═══════════════════════════════════════════════════════════════════════
# 11. Full Patient Workflow Integration
# ═══════════════════════════════════════════════════════════════════════

class TestFullWorkflow:
    def test_end_to_end(self):
        from aegis_memory import AegisMemory
        from aegis_engine import WESADPhysiologicalDetector
        from aegis_diagnostics import MultimodalDiagnostics
        from aegis_mesh_sync import AegisMeshManager
        from aegis_resilience import EnvironmentalReading, assess_environment

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            mem = AegisMemory(f.name)
            reg = mem.add_new_patient(name="Sita Devi", age=45, gender="F", blood_type="B+", allergies="NSAIDs")
            uid = reg["patient_uid"]
            mem.insert_vital(130, 0.18, True, 0.6)

            det = WESADPhysiologicalDetector()
            assert det.evaluate(130, 12, 39.5, 0.6, 14.0).is_anomaly is True

            env = assess_environment(EnvironmentalReading(43, 70, 310, True))
            assert env.emergency_mode is True

            diag = MultimodalDiagnostics()
            sos = diag.generate_satellite_sos_packet(uid, "B+", 130, 39.5, 2, 0.75)
            assert sos["satellite_compatible"] is True

            bid = mem.queue_fhir_bundle(uid, {"resourceType": "Bundle", "type": "document", "entry": []})
            assert "BUNDLE" in bid

            mesh = AegisMeshManager()
            assert mesh.broadcast_sync("EMERGENCY_SOS", {"uid": uid})["status"] == "BROADCAST_REPLICATED"
            mem.close()
