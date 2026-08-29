<p align="center">
  <img src="https://img.shields.io/badge/SIH-2026-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDEgMjFoMjJMMTIgMnoiLz48L3N2Zz4=" alt="SIH 2026" />
  <img src="https://img.shields.io/badge/Problem-SIH26181-orange?style=for-the-badge" alt="SIH26181" />
  <img src="https://img.shields.io/badge/Tests-52%20Passed-brightgreen?style=for-the-badge" alt="Tests" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Offline-First-red?style=for-the-badge" alt="Offline First" />
  <img src="https://img.shields.io/badge/Languages-5%20Indian-green?style=for-the-badge" alt="5 Languages" />
</p>

# 🛡️ AEGIS — Offline-First Rural Health Companion & Clinical Triage Workstation

> **SIH 2026 Problem Statement: SIH26181**  
> Extreme Heat & Environmental Biometric Risk Engine with Sovereign Data Privacy

AEGIS is an **offline-first, AI-powered clinical workstation** designed for India's 30,000+ Primary Health Centres (PHCs), disaster zones, and rural field hospitals. It operates with **zero internet dependency**, **on-device AES-128 encryption**, and supports **5 Indian languages** (Telugu, Hindi, Tamil, Kannada, English).

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    AEGIS Clinical Command Deck                     │
│            Next.js 14 + Three.js 3D Anatomical Twin + PWA          │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ REST / WebSocket / MJPEG
┌──────────────────────────────▼─────────────────────────────────────┐
│                     FastAPI Backend (Python)                        │
│  ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌───────────────────┐  │
│  │ WESAD ML │ │ Clinical  │ │ Multi-Agent│ │ Environmental     │  │
│  │ Engine   │ │ Scanners  │ │ Medical    │ │ Tri-Risk Matrix   │  │
│  │(IsoForest│ │(OCR,X-Ray │ │ Board (3   │ │(Heat+AQI+Flood)   │  │
│  │+RandForst│ │ABHA,Organ)│ │ Specialists│ │NOAA Heat Index    │  │
│  └──────────┘ └───────────┘ └────────────┘ └───────────────────┘  │
│  ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌───────────────────┐  │
│  │ Webcam   │ │ Bhashini  │ │ P2P Mesh   │ │ Gov APIs          │  │
│  │ rPPG +   │ │ + gTTS    │ │ CRDT Sync  │ │ ABDM/NDMA/IMD     │  │
│  │ Syncope  │ │ 5 Langs   │ │ LoRa/WiFi  │ │ + Offline Cache   │  │
│  └──────────┘ └───────────┘ └────────────┘ └───────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ SQLite (WAL) + AES-128-CBC Encryption + FHIR v4.0.1 Export  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🔥 Core Problem: Heat & Environmental Risk
- **60-second Personal Baseline Calibration** — Z-score deviations vs static population norms
- **Environmental Tri-Risk Matrix** — NOAA Heat Index + AQI + Flood inundation
- **XAI Shapley Attributions** — % contribution of each biomarker to risk score

### 🏥 Clinical Capabilities
- **Medicine Strip OCR** with allergy contraindication checking (20+ Indian drugs)
- **ABHA QR Decoder** — Ayushman Bharat Health Account 14-digit national ID
- **Edge Chest X-Ray Screener** — TB, Pneumonia, COVID, Cardiomegaly classification
- **Hand Gesture Organ Raycast** — MediaPipe landmark → anatomical twin targeting
- **Multi-Agent Medical Board** — 3 AI specialists (Cardiology, Pharmacology, Critical Care)
- **qSOFA Sepsis Trajectory Estimator** with shock probability
- **Optical Anemia Detector** — conjunctival pallor → Hb estimation
- **Cough Acoustic Classifier** — asthma, productive cough, croup detection

### 🔒 Privacy & Offline-First
- **Zero-cloud architecture** — all ML inference runs on-device
- **AES-128-CBC + HMAC-SHA256** encryption for all patient records
- **FHIR v4.0.1 Store-and-Forward** — sync when connectivity returns
- **140-byte Satellite SOS Packets** — Iridium/Starlink/LoRa compatible

### 🌐 Government Integration
- **ABDM Sandbox** — ABHA number verification
- **NDMA SACHET** — real-time disaster alerts
- **IMD Weather** — heatwave and meteorological data
- **Bhashini (MeitY)** — Indian language ASR/TTS with offline fallback

### 📡 Disaster Resilience
- **P2P Mesh Sync** — CRDT + Vector Clock versioning across tablets
- **4 peer nodes** — Triage, Ward, Ambulance, Basecamp
- **Zero-internet ad-hoc WiFi mesh** for field operations

### 🗣️ Accessibility
- **5 Indian Languages** — Telugu, Hindi, Tamil, Kannada, English
- **Voice-first interface** — TTS & STT for illiterate community health workers
- **PWA** — installable on tablets, works offline

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
docker compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Gateway:  http://localhost:80
```

### Option 2: Local Development
```bash
# Backend
python -m pip install -e ".[dev]"
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd aegis-ui && npm install && npm run dev
```

### Option 3: SIH Judge Demo Mode
```bash
# Run the 4-stage SIH26181 demonstration
python demo_aegis_resilience.py
```

---

## 🧪 Testing

```bash
# Run full test suite (52 tests)
pytest tests/test_aegis_sih.py -v

# With coverage report
pytest tests/test_aegis_sih.py -v --cov=. --cov-report=term-missing
```

**Test Coverage:** 52 tests across 11 modules — Engine, Resilience, Privacy, Scanners, Diagnostics, Mesh, MultiAgent, Memory, SIH Evaluator, Gov APIs, Full Workflow Integration.

---

## 💰 Deployment Cost

| Scale | PHCs | Cost per PHC | Total |
|-------|------|-------------|-------|
| Pilot (1 District) | 25 | ₹31,450 | ₹7.86 Lakhs |
| State (Telangana) | 1,800 | ₹31,450 | ₹5.66 Crores |
| National | 30,000 | ₹31,450 | ₹94.35 Crores |

> **70% cheaper** than commercial EHR systems. See [docs/COST_ANALYSIS.md](docs/COST_ANALYSIS.md) for details.

---

## 📂 Project Structure

```
├── main.py                  # FastAPI backend (1186 lines, 65+ endpoints)
├── aegis_engine.py          # WESAD ML + IsolationForest anomaly detection
├── aegis_scanners.py        # Medicine OCR, ABHA QR, X-Ray, Organ Raycast
├── aegis_diagnostics.py     # Anemia, Cough, qSOFA, Satellite SOS
├── aegis_multiagent.py      # 3-specialist Clinical Board consensus
├── aegis_vision.py          # Webcam rPPG, EAR fatigue, syncope detection
├── aegis_audio.py           # Multi-lingual TTS/STT (5 Indian languages)
├── aegis_memory.py          # SQLite EHR + encrypted clinical records
├── aegis_privacy.py         # AES-128-CBC Fernet encryption-at-rest
├── aegis_resilience.py      # Environmental tri-risk assessment
├── aegis_mesh_sync.py       # P2P CRDT mesh synchronization
├── aegis_gov_api.py         # ABDM, NDMA, IMD, Bhashini integration
├── sih_evaluator.py         # SIH26181 baseline calibration & demo stages
├── fhir_exporter.py         # HL7 FHIR v4.0.1 document bundle generator
├── medical_rag.py           # Offline Medical RAG knowledge base
├── baymax_service.py        # Ollama LLM clinical intelligence
├── cds_hooks.py             # CDS Hooks 1.0 clinical decision support
├── aegis-ui/                # Next.js 14 + Three.js frontend (PWA)
├── tests/                   # 52 automated tests
├── docs/                    # Cost analysis, scaling architecture
├── Dockerfile               # Backend container
├── aegis-ui/Dockerfile      # Frontend container
├── docker-compose.yml       # 1-command deployment
└── nginx.conf               # Reverse proxy configuration
```

---

## 👥 Team

Built for **Smart India Hackathon 2026** by Team AEGIS.

---

## 📜 License

Open Source — Built for India's public health infrastructure.
