"""
AEGIS FHIR & Clinical Triage Handover Exporter
Generates HL7 / FHIR v4.0.1 compliant JSON Bundles and Hospital-Grade Printable Emergency Triage Handover Reports.
Adheres to HL7 FHIR US-Core and International Patient Summary (IPS) interoperability standards.
"""

from datetime import datetime, timezone
import json
from typing import Dict, Any, List, Optional


def generate_fhir_bundle(
    patient_profile: Dict[str, Any],
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    matched_protocol: Optional[Dict[str, Any]] = None,
    recent_history: Optional[List[Dict[str, Any]]] = None,
    xai_attributions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate an HL7/FHIR v4.0.1 compliant Document Bundle for hospital EHR interoperability.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    patient_id = patient_profile.get("patient_uid", "PAT-RAM-2026")
    patient_name = patient_profile.get("name", "Ramcharan")
    allergies = patient_profile.get("allergies", "Ibuprofen, NSAIDs")

    entries = []

    # 1. Resource: Patient
    entries.append({
        "fullUrl": f"urn:uuid:patient-{patient_id}",
        "resource": {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
            },
            "identifier": [
                {
                    "system": "http://hospital.aegis.health/patient-ids",
                    "value": patient_id
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "text": patient_name,
                    "family": patient_name.split()[-1] if len(patient_name.split()) > 1 else patient_name,
                    "given": patient_name.split()[:-1] if len(patient_name.split()) > 1 else [patient_name]
                }
            ],
            "gender": patient_profile.get("gender", "male").lower(),
            "birthDate": "2002-01-15",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-bloodType",
                    "valueString": patient_profile.get("blood_type", "O+")
                }
            ]
        }
    })

    # 2. Resource: AllergyIntolerance (Documented Contraindication)
    for allergy in [a.strip() for a in allergies.split(",") if a.strip()]:
        entries.append({
            "fullUrl": f"urn:uuid:allergy-{allergy.lower()}",
            "resource": {
                "resourceType": "AllergyIntolerance",
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                        "display": "Active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }]
                },
                "type": "allergy",
                "category": ["medication"],
                "criticality": "high",
                "code": {
                    "text": allergy
                },
                "patient": {
                    "reference": f"urn:uuid:patient-{patient_id}",
                    "display": patient_name
                },
                "recordedDate": now_iso
            }
        })

    # 3. Resource: Observation - Heart Rate
    entries.append({
        "fullUrl": "urn:uuid:obs-heart-rate",
        "resource": {
            "resourceType": "Observation",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8867-4",
                    "display": "Heart rate"
                }],
                "text": "Heart Rate"
            },
            "subject": {"reference": f"urn:uuid:patient-{patient_id}"},
            "effectiveDateTime": now_iso,
            "valueQuantity": {
                "value": float(vitals.get("heartRate", vitals.get("heart_rate", 72))),
                "unit": "beats/minute",
                "system": "http://unitsofmeasure.org",
                "code": "/min"
            },
            "interpretation": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": "H" if float(vitals.get("heartRate", vitals.get("heart_rate", 72))) > 100 else "N",
                    "display": "High" if float(vitals.get("heartRate", vitals.get("heart_rate", 72))) > 100 else "Normal"
                }]
            }]
        }
    })

    # 4. Resource: Observation - Body Temperature
    entries.append({
        "fullUrl": "urn:uuid:obs-temperature",
        "resource": {
            "resourceType": "Observation",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8310-5",
                    "display": "Body temperature"
                }]
            },
            "subject": {"reference": f"urn:uuid:patient-{patient_id}"},
            "effectiveDateTime": now_iso,
            "valueQuantity": {
                "value": float(vitals.get("temperature", 36.8)),
                "unit": "Cel",
                "system": "http://unitsofmeasure.org",
                "code": "Cel"
            }
        }
    })

    # 5. Resource: Condition / Active Anomaly
    if matched_protocol:
        entries.append({
            "fullUrl": f"urn:uuid:condition-{matched_protocol.get('protocol_id', 'CLIN-01')}",
            "resource": {
                "resourceType": "Condition",
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "provisional"
                    }]
                },
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis"
                    }]
                }],
                "code": {
                    "text": matched_protocol.get("title", "Acute Physiological Anomaly")
                },
                "subject": {"reference": f"urn:uuid:patient-{patient_id}"},
                "recordedDate": now_iso
            }
        })

    # 6. Resource: CarePlan / Safe First-Line Pharmacotherapy
    if matched_protocol:
        entries.append({
            "fullUrl": f"urn:uuid:careplan-{matched_protocol.get('protocol_id', 'CLIN-01')}",
            "resource": {
                "resourceType": "CarePlan",
                "status": "active",
                "intent": "proposal",
                "title": f"Triage Care Plan: {matched_protocol.get('title')}",
                "description": f"First Line: {matched_protocol.get('first_line_action')}. Pharmacotherapy: {matched_protocol.get('pharmacotherapy', {}).get('first_line', 'Supportive hydration.')}",
                "subject": {"reference": f"urn:uuid:patient-{patient_id}"},
                "period": {"start": now_iso}
            }
        })

    return {
        "resourceType": "Bundle",
        "id": f"aegis-triage-{int(datetime.now(timezone.utc).timestamp())}",
        "meta": {
            "lastUpdated": now_iso,
            "profile": ["http://hl7.org/fhir/StructureDefinition/Bundle"]
        },
        "type": "document",
        "timestamp": now_iso,
        "total": len(entries),
        "entry": entries
    }


def generate_html_triage_report(
    patient_profile: Dict[str, Any],
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    matched_protocol: Optional[Dict[str, Any]] = None,
    xai_attributions: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate an official, printable Clinical Emergency Triage & Handover HTML Document.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    hr = vitals.get("heartRate", vitals.get("heart_rate", 72))
    temp = vitals.get("temperature", 36.8)
    rmssd = vitals.get("rmssd", 45.0)
    eda = vitals.get("eda", 1.5)
    ear = vitals.get("ear", 0.32)
    posture = vitals.get("posture_status", "ERECT_NOMINAL")

    xai_bars_html = ""
    if xai_attributions and "contributions" in xai_attributions:
        for name, pct in xai_attributions["contributions"].items():
            color = "#f43f5e" if pct > 30 else "#06b6d4" if pct > 20 else "#10b981"
            xai_bars_html += f"""
            <div style="margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 2px;">
                    <span>{name}</span>
                    <strong>{pct}%</strong>
                </div>
                <div style="background: #e2e8f0; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: {color}; width: {pct}%; height: 100%;"></div>
                </div>
            </div>
            """

    proto_html = ""
    if matched_protocol:
        proto_html = f"""
        <div style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 12px; margin-top: 10px; border-radius: 4px;">
            <div style="font-size: 13px; font-weight: bold; color: #0369a1;">ACTIVE RAG PROTOCOL: {matched_protocol.get('protocol_id')} - {matched_protocol.get('title')}</div>
            <div style="font-size: 12px; margin-top: 4px;"><strong>Recommended First-Line:</strong> {matched_protocol.get('first_line_action')}</div>
            <div style="font-size: 12px; margin-top: 4px;"><strong>Safe Pharmacotherapy:</strong> {matched_protocol.get('pharmacotherapy', {}).get('first_line', 'N/A')}</div>
            <div style="font-size: 12px; margin-top: 4px; color: #b91c1c;"><strong>Contraindication:</strong> {matched_protocol.get('pharmacotherapy', {}).get('contraindication_rationale', 'N/A')}</div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AEGIS Emergency Clinical Handover Document</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #0f172a; margin: 30px; line-height: 1.5; }}
            .header {{ border-bottom: 2px solid #0284c7; padding-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }}
            .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
            .badge-danger {{ background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }}
            .badge-info {{ background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }}
            .card {{ border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; background: #ffffff; }}
            .vitals-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
            .vitals-table th, .vitals-table td {{ border: 1px solid #e2e8f0; padding: 6px 10px; font-size: 12px; text-align: left; }}
            .vitals-table th {{ background: #f1f5f9; }}
            .sig-block {{ margin-top: 30px; border-top: 1px dashed #94a3b8; padding-top: 16px; display: flex; justify-content: space-between; font-size: 12px; color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1 style="margin: 0; font-size: 20px; color: #0369a1;">AEGIS MEDICAL WORKSTATION // EMERGENCY TRIAGE HANDOVER</h1>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">HL7 FHIR v4.0.1 Document Standard • Generated: {now_str}</div>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-info">TRIAGE PRIORITY: ACUTE</span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #334155;">1. PATIENT DEMOGRAPHICS (EHR)</h3>
                <div style="font-size: 12px;"><strong>Name:</strong> {patient_profile.get('name', 'Ramcharan')} ({patient_profile.get('age', 24)}y, {patient_profile.get('gender', 'Male')})</div>
                <div style="font-size: 12px;"><strong>Patient UID:</strong> {patient_profile.get('patient_uid', 'PAT-RAM-2026')}</div>
                <div style="font-size: 12px;"><strong>Blood Type:</strong> {patient_profile.get('blood_type', 'O+')}</div>
                <div style="font-size: 12px; margin-top: 6px;">
                    <strong>DOCUMENTED ALLERGIES:</strong><br>
                    <span class="badge badge-danger" style="margin-top: 3px;">⚠️ {patient_profile.get('allergies', 'Ibuprofen, NSAIDs')}</span>
                </div>
                <div style="font-size: 12px; margin-top: 6px;"><strong>Active Medications:</strong> {patient_profile.get('active_medications', 'None')}</div>
                <div style="font-size: 12px;"><strong>Chronic Conditions:</strong> {patient_profile.get('chronic_conditions', 'Mild Asthmatic Tendency')}</div>
            </div>

            <div class="card">
                <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #334155;">2. REAL-TIME PHYSIOLOGICAL BIOMETRICS</h3>
                <table class="vitals-table">
                    <tr><th>Biomarker</th><th>Measured Value</th><th>Clinical Status</th></tr>
                    <tr><td>Heart Rate (BPM)</td><td><strong>{hr} BPM</strong></td><td>{ 'Tachycardia (Elevated)' if hr > 100 else 'Resting Normal' }</td></tr>
                    <tr><td>Core Body Temperature</td><td><strong>{temp:.1f} °C</strong></td><td>{ 'Hyperthermia (Fever)' if temp > 38.0 else 'Normothermic' }</td></tr>
                    <tr><td>Autonomic HRV (RMSSD)</td><td><strong>{rmssd} ms</strong></td><td>{ 'Autonomic Strain (Low)' if rmssd < 25 else 'Nominal Balance' }</td></tr>
                    <tr><td>EDA Skin Conductance</td><td><strong>{eda:.1f} µS</strong></td><td>Sympathetic Arousal</td></tr>
                    <tr><td>Ocular Aspect Ratio (EAR)</td><td><strong>{ear:.3f}</strong></td><td>{ 'Somnolence / Fatigue' if ear < 0.22 else 'Vigilant' }</td></tr>
                    <tr><td>Postural Alignment</td><td><strong>{posture}</strong></td><td>{ '⚠️ SYNCOPE / DROP' if 'SYNCOPE' in posture else 'Erect Posture' }</td></tr>
                </table>
            </div>
        </div>

        <div class="card" style="margin-top: 16px;">
            <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #334155;">3. EXPLAINABLE AI (XAI) BIOMARKER DECOMPOSITION</h3>
            <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Mathematical contribution weights calculated by WESAD Random Forest Risk Engine:</div>
            {xai_bars_html if xai_bars_html else '<div style="font-size: 12px; color: #64748b;">No active anomaly deviation.</div>'}
        </div>

        <div class="card" style="margin-top: 16px;">
            <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #334155;">4. CLINICAL DECISION SUPPORT & SAFE PHARMACOTHERAPY</h3>
            {proto_html if proto_html else '<div style="font-size: 12px; color: #64748b;">Resting observation nominal.</div>'}
        </div>

        <div class="sig-block">
            <div><strong>Attending System:</strong> AEGIS Autonomous Companion v3.6.0</div>
            <div><strong>Attending Physician Signature:</strong> ___________________________</div>
            <div><strong>Hospital Disposition:</strong> Triage / Observation Unit</div>
        </div>
    </body>
    </html>
    """
    return html
