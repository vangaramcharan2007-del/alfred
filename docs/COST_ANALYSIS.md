# AEGIS — Deployment Cost Analysis & Scaling Architecture

## Per-PHC (Primary Health Centre) Deployment Cost

### Hardware (One-Time)

| Component | Specification | Cost (₹) |
|-----------|--------------|----------|
| Laptop / Tablet | Lenovo IdeaPad Slim 3 (i3, 8GB, 256GB SSD) | ₹28,000 |
| DHT22 Temp/Humidity Sensor + ESP32 | Environmental monitoring | ₹450 |
| USB Pulse Oximeter (CMS50D) | SpO2 + Heart Rate | ₹1,200 |
| USB Webcam (Logitech C270) | rPPG + Vision diagnostics | ₹1,800 |
| **Total Hardware** | | **₹31,450** |

### Software (Annual)

| Component | Cost (₹/year) |
|-----------|---------------|
| AEGIS Software License | ₹0 (Open Source) |
| Cloud Hosting (optional backup sync) | ₹0 — ₹2,400 (Render free tier / ₹200/mo) |
| Bhashini API | ₹0 (Government free tier) |
| Domain + SSL | ₹500 |
| **Total Software/year** | **₹0 — ₹2,900** |

### Comparison vs Existing Solutions

| Solution | Setup Cost | Annual Cost | Offline? | Indian Languages? |
|----------|-----------|-------------|----------|-------------------|
| **AEGIS** | ₹31,450 | ₹0-2,900 | ✅ Yes | ✅ 5 languages |
| Commercial EHR (Practo/HealthPlix) | ₹50,000+ | ₹60,000+ | ❌ No | ❌ English only |
| Paper records (status quo) | ₹0 | ₹5,000 (printing) | ✅ Yes | ✅ But no analytics |

## Scaling Architecture

```
District PHC (Offline Edge)                State Hospital (Regional Hub)
┌─────────────────────────┐               ┌──────────────────────┐
│ AEGIS Tablet/Laptop     │──── LoRa ────▶│ AEGIS District Hub   │
│ • SQLite + AES-128      │   Mesh Sync   │ • PostgreSQL          │
│ • WESAD ML Engine       │               │ • FHIR Gateway        │
│ • Webcam rPPG           │               │ • NDMA Alert Relay    │
│ • Bhashini TTS/ASR      │               └──────────┬───────────┘
└─────────────────────────┘                          │
                                                     │ ABDM/FHIR Sync
                                                     ▼
                                          ┌──────────────────────┐
                                          │ National ABDM Gateway │
                                          │ • Health Records      │
                                          │ • ABHA Verification   │
                                          │ • DigiLocker          │
                                          └──────────────────────┘
```

## Scaling Numbers

| Scale | PHCs | Est. Total Cost | Timeline |
|-------|------|-----------------|----------|
| Pilot (1 District) | 25 | ₹7.86 Lakhs | 3 months |
| State Rollout (Telangana) | 1,800 | ₹5.66 Crores | 12 months |
| National (all states) | 30,000 | ₹94.35 Crores | 24 months |

> **Key Advantage:** ₹94 Crores for 30,000 PHCs = ₹31,450 per PHC. 
> Compared to commercial EHR systems costing ₹1.1 Lakh+ per site, 
> AEGIS saves the government **₹236 Crores annually**.
