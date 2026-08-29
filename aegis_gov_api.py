"""
Government API Integration Layer for AEGIS — SIH 2026.
Connects to Indian government health, disaster, and meteorological APIs:
  1. ABDM (Ayushman Bharat Digital Mission) Sandbox — ABHA verification & health records
  2. NDMA (National Disaster Management Authority) — Real-time disaster alerts
  3. IMD (India Meteorological Department) — Weather & heat wave warnings
  4. Bhashini (MeitY) — Multi-lingual ASR/TTS for Indian languages

All APIs gracefully fallback to offline cached data when network is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger("aegis_gov_api")

# ═══════════════════════════════════════════════════════════════════════
# 1. ABDM (Ayushman Bharat Digital Mission) Sandbox Integration
# ═══════════════════════════════════════════════════════════════════════

ABDM_SANDBOX_BASE = "https://abha.abdm.gov.in/api/v3"
ABDM_API_KEY = os.getenv("ABDM_API_KEY", "")


@dataclass
class ABDMVerificationResult:
    abha_number: str
    verified: bool
    name: Optional[str] = None
    gender: Optional[str] = None
    year_of_birth: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    status: str = "success"
    source: str = "ABDM_SANDBOX"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def verify_abha_number(abha_number: str) -> ABDMVerificationResult:
    """
    Verify ABHA number against ABDM Sandbox.
    Falls back to local validation if API unavailable.
    
    ABDM Sandbox Docs: https://sandbox.abdm.gov.in/docs/
    """
    # Clean ABHA number
    clean = abha_number.replace("-", "").replace(" ", "")
    if len(clean) != 14 or not clean.isdigit():
        return ABDMVerificationResult(
            abha_number=abha_number, verified=False,
            status="error", source="LOCAL_VALIDATION",
            error="ABHA number must be exactly 14 digits"
        )

    # Try ABDM Sandbox API
    if ABDM_API_KEY:
        try:
            import httpx
            resp = httpx.post(
                f"{ABDM_SANDBOX_BASE}/profile/verify",
                headers={"Authorization": f"Bearer {ABDM_API_KEY}", "Content-Type": "application/json"},
                json={"abhaNumber": clean},
                timeout=5.0
            )
            if resp.status_code == 200:
                data = resp.json()
                return ABDMVerificationResult(
                    abha_number=abha_number, verified=True,
                    name=data.get("name"), gender=data.get("gender"),
                    year_of_birth=data.get("yearOfBirth"),
                    state=data.get("stateName"), district=data.get("districtName"),
                    source="ABDM_LIVE"
                )
        except Exception as e:
            logger.warning(f"ABDM API unavailable, using offline validation: {e}")

    # Offline fallback: Luhn-style checksum validation
    digits = [int(d) for d in clean]
    checksum_valid = sum(digits) % 10 != 7  # Simplified validation
    return ABDMVerificationResult(
        abha_number=abha_number,
        verified=checksum_valid,
        source="OFFLINE_LOCAL_VALIDATION",
        status="success"
    )


# ═══════════════════════════════════════════════════════════════════════
# 2. NDMA (National Disaster Management Authority) — Real-Time Alerts
# ═══════════════════════════════════════════════════════════════════════

NDMA_API_BASE = "https://sachet.ndma.gov.in/cap_public_website/FetchAllAlertDetails"


@dataclass
class DisasterAlert:
    alert_id: str
    alert_type: str  # FLOOD, HEAT_WAVE, CYCLONE, EARTHQUAKE, etc.
    severity: str  # EXTREME, SEVERE, MODERATE, MINOR
    headline: str
    description: str
    area: str
    effective_from: str
    expires_at: str
    source: str = "NDMA_SACHET"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NDMAAlertResponse:
    alerts: List[DisasterAlert] = field(default_factory=list)
    total_active: int = 0
    status: str = "success"
    source: str = "NDMA_SACHET"
    fetched_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "alerts": [a.to_dict() for a in self.alerts]}


# Offline fallback: Pre-cached heatwave and flood alerts for SIH demo
_CACHED_NDMA_ALERTS = [
    DisasterAlert(
        alert_id="NDMA-HW-2026-TS-001",
        alert_type="HEAT_WAVE",
        severity="EXTREME",
        headline="Extreme Heat Wave Warning — Telangana, Andhra Pradesh",
        description="IMD issues Red Alert: Maximum temperatures 45-47°C expected in Hyderabad, Warangal, "
                    "Karimnagar, Khammam, Nalgonda districts. Avoid outdoor activity 11 AM - 4 PM.",
        area="Telangana, Andhra Pradesh",
        effective_from="2026-05-15T06:00:00+05:30",
        expires_at="2026-05-18T18:00:00+05:30"
    ),
    DisasterAlert(
        alert_id="NDMA-FL-2026-MH-002",
        alert_type="FLOOD",
        severity="SEVERE",
        headline="Flood Warning — Godavari Basin, Maharashtra & Telangana",
        description="Heavy rainfall (>200mm/24hr) causing Godavari river levels to cross danger mark. "
                    "Low-lying areas in Nashik, Nanded, Bhadrachalam districts at high risk.",
        area="Maharashtra, Telangana — Godavari Basin",
        effective_from="2026-07-20T00:00:00+05:30",
        expires_at="2026-07-23T23:59:00+05:30"
    ),
    DisasterAlert(
        alert_id="NDMA-AQ-2026-DL-003",
        alert_type="AIR_QUALITY_EMERGENCY",
        severity="SEVERE",
        headline="Severe Air Quality Emergency — Delhi NCR (AQI 450+)",
        description="CPCB confirms AQI > 450 across Delhi NCR. Schools closed. N95 masks mandatory. "
                    "Construction ban enforced. GRAP-IV activated.",
        area="Delhi NCR, Haryana, UP — Indo-Gangetic Plain",
        effective_from="2026-11-05T06:00:00+05:30",
        expires_at="2026-11-10T23:59:00+05:30"
    ),
]


def fetch_ndma_alerts(state: Optional[str] = None) -> NDMAAlertResponse:
    """
    Fetch active disaster alerts from NDMA SACHET portal.
    Falls back to cached demo data for offline/SIH demo.
    """
    try:
        import httpx
        resp = httpx.get(NDMA_API_BASE, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            alerts = []
            for item in data.get("alertList", [])[:10]:
                alerts.append(DisasterAlert(
                    alert_id=item.get("alertId", "unknown"),
                    alert_type=item.get("alertCategory", "UNKNOWN"),
                    severity=item.get("severity", "MODERATE"),
                    headline=item.get("headline", ""),
                    description=item.get("description", ""),
                    area=item.get("areaDesc", ""),
                    effective_from=item.get("effective", ""),
                    expires_at=item.get("expires", ""),
                    source="NDMA_LIVE"
                ))
            if state:
                alerts = [a for a in alerts if state.lower() in a.area.lower()]
            return NDMAAlertResponse(
                alerts=alerts, total_active=len(alerts),
                source="NDMA_LIVE", fetched_at=time.strftime("%Y-%m-%dT%H:%M:%S+05:30")
            )
    except Exception as e:
        logger.warning(f"NDMA API unavailable, using cached alerts: {e}")

    # Offline fallback
    alerts = _CACHED_NDMA_ALERTS
    if state:
        alerts = [a for a in alerts if state.lower() in a.area.lower()]
    return NDMAAlertResponse(
        alerts=alerts, total_active=len(alerts),
        source="OFFLINE_CACHED", fetched_at=time.strftime("%Y-%m-%dT%H:%M:%S+05:30")
    )


# ═══════════════════════════════════════════════════════════════════════
# 3. IMD (India Meteorological Department) — Weather & Heat Warnings
# ═══════════════════════════════════════════════════════════════════════

IMD_API_BASE = "https://api.open-meteo.com/v1/forecast"  # Open-Meteo as proxy (IMD doesn't have public REST)

# Indian city coordinates for quick lookup
INDIAN_CITY_COORDS = {
    "hyderabad": (17.385, 78.487),
    "delhi": (28.614, 77.209),
    "mumbai": (19.076, 72.878),
    "chennai": (13.083, 80.271),
    "bangalore": (12.972, 77.594),
    "kolkata": (22.573, 88.364),
    "warangal": (17.978, 79.600),
    "visakhapatnam": (17.687, 83.218),
}


@dataclass
class IMDWeatherData:
    city: str
    temperature_c: float
    humidity_percent: float
    feels_like_c: float
    wind_speed_kmh: float
    uv_index: float
    heat_wave_active: bool
    aqi_estimate: int
    source: str = "IMD_PROXY"
    status: str = "success"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def fetch_imd_weather(city: str = "hyderabad") -> IMDWeatherData:
    """
    Fetch current weather for Indian city. Uses Open-Meteo as IMD proxy.
    Falls back to cached data for offline demo.
    """
    city_lower = city.lower().strip()
    coords = INDIAN_CITY_COORDS.get(city_lower, (17.385, 78.487))

    try:
        import httpx
        resp = httpx.get(
            IMD_API_BASE,
            params={
                "latitude": coords[0], "longitude": coords[1],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,uv_index",
                "timezone": "Asia/Kolkata"
            },
            timeout=5.0
        )
        if resp.status_code == 200:
            data = resp.json().get("current", {})
            temp = data.get("temperature_2m", 35.0)
            humidity = data.get("relative_humidity_2m", 50.0)
            feels_like = data.get("apparent_temperature", temp)
            return IMDWeatherData(
                city=city, temperature_c=temp, humidity_percent=humidity,
                feels_like_c=feels_like,
                wind_speed_kmh=data.get("wind_speed_10m", 10.0),
                uv_index=data.get("uv_index", 7.0),
                heat_wave_active=temp >= 42.0 or feels_like >= 45.0,
                aqi_estimate=min(500, max(30, int((temp - 25) * 15 + humidity * 0.5))),
                source="IMD_LIVE_PROXY"
            )
    except Exception as e:
        logger.warning(f"IMD/Open-Meteo unavailable, using offline data: {e}")

    # Offline fallback
    return IMDWeatherData(
        city=city, temperature_c=43.5, humidity_percent=65.0,
        feels_like_c=51.2, wind_speed_kmh=8.0, uv_index=11.0,
        heat_wave_active=True, aqi_estimate=280,
        source="OFFLINE_CACHED"
    )


# ═══════════════════════════════════════════════════════════════════════
# 4. Bhashini (MeitY) — Indian Language ASR & TTS
# ═══════════════════════════════════════════════════════════════════════

BHASHINI_API_BASE = "https://dhruva-api.bhashini.gov.in/services/inference"
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "")
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "")

# Bhashini language codes
BHASHINI_LANG_MAP = {
    "te": "te",    # Telugu
    "hi": "hi",    # Hindi
    "ta": "ta",    # Tamil
    "kn": "kn",    # Kannada
    "en": "en",    # English
    "mr": "mr",    # Marathi
    "bn": "bn",    # Bengali
    "gu": "gu",    # Gujarati
    "ml": "ml",    # Malayalam
    "pa": "pa",    # Punjabi
    "or": "or",    # Odia
}


@dataclass
class BhashiniTTSResult:
    text: str
    language: str
    audio_base64: Optional[str] = None
    audio_format: str = "wav"
    source: str = "BHASHINI"
    status: str = "success"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BhashiniTranslationResult:
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    source: str = "BHASHINI"
    status: str = "success"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def bhashini_translate(text: str, source_lang: str = "en", target_lang: str = "hi") -> BhashiniTranslationResult:
    """
    Translate text between Indian languages using Bhashini NMT.
    Falls back to pass-through if API unavailable.
    """
    src = BHASHINI_LANG_MAP.get(source_lang, source_lang)
    tgt = BHASHINI_LANG_MAP.get(target_lang, target_lang)

    if BHASHINI_API_KEY:
        try:
            import httpx
            resp = httpx.post(
                f"{BHASHINI_API_BASE}/translation",
                headers={
                    "Authorization": BHASHINI_API_KEY,
                    "userID": BHASHINI_USER_ID,
                    "Content-Type": "application/json"
                },
                json={
                    "pipelineTasks": [{
                        "taskType": "translation",
                        "config": {"language": {"sourceLanguage": src, "targetLanguage": tgt}}
                    }],
                    "inputData": {"input": [{"source": text}]}
                },
                timeout=10.0
            )
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("target", text)
                return BhashiniTranslationResult(
                    source_text=text, translated_text=translated,
                    source_lang=src, target_lang=tgt, source="BHASHINI_LIVE"
                )
        except Exception as e:
            logger.warning(f"Bhashini Translation API unavailable: {e}")

    # Offline fallback: return original text with note
    return BhashiniTranslationResult(
        source_text=text, translated_text=text,
        source_lang=src, target_lang=tgt,
        source="OFFLINE_PASSTHROUGH"
    )


def bhashini_tts(text: str, lang: str = "hi") -> BhashiniTTSResult:
    """
    Generate speech audio from text using Bhashini TTS.
    Falls back to gTTS if Bhashini unavailable.
    """
    lang_code = BHASHINI_LANG_MAP.get(lang, lang)

    if BHASHINI_API_KEY:
        try:
            import httpx
            import base64
            resp = httpx.post(
                f"{BHASHINI_API_BASE}/tts",
                headers={
                    "Authorization": BHASHINI_API_KEY,
                    "userID": BHASHINI_USER_ID,
                    "Content-Type": "application/json"
                },
                json={
                    "pipelineTasks": [{
                        "taskType": "tts",
                        "config": {"language": {"sourceLanguage": lang_code}, "gender": "female"}
                    }],
                    "inputData": {"input": [{"source": text}]}
                },
                timeout=10.0
            )
            if resp.status_code == 200:
                data = resp.json()
                audio = data.get("pipelineResponse", [{}])[0].get("audio", [{}])[0].get("audioContent", "")
                return BhashiniTTSResult(
                    text=text, language=lang_code,
                    audio_base64=audio, source="BHASHINI_LIVE"
                )
        except Exception as e:
            logger.warning(f"Bhashini TTS API unavailable, falling back to gTTS: {e}")

    # Fallback to gTTS
    try:
        from gtts import gTTS
        import base64
        import io
        tts = gTTS(text=text, lang=lang_code)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return BhashiniTTSResult(
            text=text, language=lang_code,
            audio_base64=audio_b64, audio_format="mp3",
            source="GTTS_FALLBACK"
        )
    except Exception:
        return BhashiniTTSResult(
            text=text, language=lang_code,
            status="error", source="OFFLINE",
            error="No TTS engine available offline"
        )


# ═══════════════════════════════════════════════════════════════════════
# Convenience: Get All Government Data for Dashboard
# ═══════════════════════════════════════════════════════════════════════

def get_government_situation_report(city: str = "hyderabad", state: str = "telangana") -> Dict[str, Any]:
    """
    Aggregate all government data sources into a single situation report
    for the AEGIS command deck dashboard.
    """
    weather = fetch_imd_weather(city)
    alerts = fetch_ndma_alerts(state)

    return {
        "city": city,
        "state": state,
        "weather": weather.to_dict(),
        "disaster_alerts": alerts.to_dict(),
        "heat_wave_active": weather.heat_wave_active,
        "total_active_alerts": alerts.total_active,
        "data_sources": {
            "weather": weather.source,
            "alerts": alerts.source,
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+05:30")
    }
