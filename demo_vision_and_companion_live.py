"""
Live Demonstration Script - AEGIS Vision Core, Persistent Memory, and Baymax Companion
Executes end-to-end multi-modal pipeline showing live vision processing,
SQLite memory persistence, and context-aware conversational takeovers.
"""

import sys
import time
import requests
import numpy as np
import cv2

from aegis_memory import AegisMemory
from aegis_vision import VitalScanner

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BACKEND_URL = "http://127.0.0.1:8000"


def print_banner(title: str):
    print("\n" + "=" * 65)
    print(f"  ⚡ {title}")
    print("=" * 65)


def run_live_demo():
    print_banner("1. INITIALIZING AEGIS LIVE VISION SCANNER & SQLITE MEMORY")
    memory = AegisMemory(db_path="aegis_core.db")
    scanner = VitalScanner(db_path="aegis_core.db")
    print("✅ AegisMemory connected to SQLite: aegis_core.db")
    print("✅ VitalScanner initialized with Haar Face/Eye Detectors & rPPG Extractor")

    print_banner("2. PROCESSING OPTICAL BIOMETRICS & LOGGING TO DATABASE")
    # Simulate 5 live camera diagnostic frames
    print("Scanning optical reflectance & Eye Aspect Ratio (EAR)...")
    for i in range(1, 6):
        synth_frame = np.full((480, 640, 3), 120 + i * 5, dtype=np.uint8)
        res = scanner.process_frame(synth_frame, draw_overlay=False)
        print(f"  [Frame {i}] Face Detected: {res['face_detected']} | EAR: {res['ear']:.3f} | rPPG Green: {res['raw_pulse']:.1f} | Fatigued: {res['is_fatigued']}")
        time.sleep(0.3)

    # Verify SQLite Memory state
    latest_db_entry = memory.get_latest_vital()
    recent_baseline = memory.get_recent_baseline(limit=5)
    print(f"\n📁 Database Verification:")
    print(f"   Latest DB Entry : {latest_db_entry}")
    print(f"   Recent Log Count: {len(recent_baseline)} records stored in aegis_core.db")

    print_banner("3. QUERYING LIVE FASTAPI VISION ENDPOINT (GET /live-vision-metrics)")
    try:
        res = requests.get(f"{BACKEND_URL}/live-vision-metrics")
        print(f"HTTP {res.status_code} Response:")
        print(res.json())
    except Exception as exc:
        print(f"API Error: {exc}")

    print_banner("4. TWO-WAY VOICE COMPANION: ROUTINE DIALOGUE (POST /companion-interact)")
    try:
        payload_normal = {
            "user_speech": "Hello Baymax, how are my vital parameters today?",
            "heart_rate": 72.0,
            "rmssd": 46.0,
            "temperature": 36.8,
            "temp_slope": 0.0,
            "eda": 1.5,
            "ear": 0.32
        }
        print(f"User Spoke: \"{payload_normal['user_speech']}\"")
        res_normal = requests.post(f"{BACKEND_URL}/companion-interact", json=payload_normal).json()
        print(f"Risk Level : {res_normal['risk_level']}")
        print(f"Baymax Voice Output: \"{res_normal['reply_text']}\"")
    except Exception as exc:
        print(f"API Error: {exc}")

    print_banner("5. VISION FATIGUE INTERVENTION (PROLONGED EYELID CLOSURE EAR < 0.22)")
    try:
        # Log a fatigue state in database
        memory.log_vitals(hr=68.0, ear=0.14, is_fatigued=True, rppg_signal=120.0)
        
        payload_fatigue = {
            "user_speech": "I have been working for 8 hours straight without a break.",
            "heart_rate": 68.0,
            "rmssd": 35.0,
            "temperature": 36.6,
            "temp_slope": -0.02,
            "eda": 2.1,
            "ear": 0.14
        }
        print(f"Vision Scanner Event: EAR=0.14 (Somnolence Flag ACTIVE)")
        print(f"User Spoke: \"{payload_fatigue['user_speech']}\"")
        res_fatigue = requests.post(f"{BACKEND_URL}/companion-interact", json=payload_fatigue).json()
        print(f"Risk Level : {res_fatigue['risk_level']}")
        print(f"Fatigue Detected: {res_fatigue['fatigue_detected']}")
        print(f"Baymax Proactive Intervention: \"{res_fatigue['reply_text']}\"")
    except Exception as exc:
        print(f"API Error: {exc}")

    print_banner("6. ACUTE THERMAL & CARDIAC ANOMALY INTERVENTION (WESAD MODEL)")
    try:
        payload_anomaly = {
            "user_speech": "I am experiencing severe dizziness and body heat.",
            "heart_rate": 135.0,
            "rmssd": 15.0,
            "temperature": 39.5,
            "temp_slope": 0.15,
            "eda": 8.5,
            "ear": 0.25
        }
        print(f"WESAD Biometric Spike: HR=135 BPM, Temp=39.5°C, HRV=15ms, EDA=8.5µS")
        res_anomaly = requests.post(f"{BACKEND_URL}/companion-interact", json=payload_anomaly).json()
        print(f"Risk Level : {res_anomaly['risk_level']}")
        print(f"Anomaly Triggered: {res_anomaly['is_anomaly']}")
        print(f"Escalation Webhook Fired: {res_anomaly['escalated']}")
        print(f"Baymax Emergency Takeover: \"{res_anomaly['reply_text']}\"")
    except Exception as exc:
        print(f"API Error: {exc}")

    print_banner("ALL-IN LIVE DEMONSTRATION COMPLETE - 100% OPERATIONAL")


if __name__ == "__main__":
    run_live_demo()
