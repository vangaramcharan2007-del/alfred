"""
AEGIS Baymax Service - Doctor-Level Offline Medical RAG & EHR Inference
Routes patient speech and live biometrics through Offline Medical Knowledge Base (RAG)
and Electronic Health Record (EHR) persistent memory.
Enforces strict first-person Caregiver persona with drug-allergy contraindication checks.
"""

import sys
from typing import Dict, Any, Optional, AsyncGenerator, Tuple
import ollama
from fastapi.responses import StreamingResponse

from aegis_memory import AegisMemory
from medical_rag import OfflineMedicalRAG

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async_client = ollama.AsyncClient()
medical_rag = OfflineMedicalRAG()


async def stream_baymax_reasoning(
    user_query: str,
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    patient_profile: Optional[Dict[str, Any]] = None,
    model: str = "aegis-baymax"
) -> AsyncGenerator[str, None]:
    """
    Doctor-Level Clinical Inference Engine.
    Cross-references patient inquiry against:
    1. Offline Medical RAG Protocols (medical_rag.py)
    2. Patient EHR Profile & Allergy Records (aegis_memory.py)
    3. Live Biometric Telemetry & Optical Eye Aspect Ratio
    """
    # 1. Retrieve EHR Patient Profile if not provided
    if patient_profile is None:
        try:
            mem = AegisMemory(db_path="aegis_core.db")
            patient_profile = mem.get_patient_profile()
            mem.close()
        except Exception:
            patient_profile = {
                "name": "Ramcharan",
                "age": 24,
                "allergies": "Ibuprofen, NSAIDs",
                "allergies_list": ["ibuprofen", "nsaids", "aspirin"],
                "active_medications": "None",
                "chronic_conditions": "Mild Asthmatic Tendency"
            }

    # 2. Retrieve Offline Medical Protocol
    matched_protocol = medical_rag.retrieve_protocol(user_query)

    # 3. Evaluate Drug-Allergy Safety
    allergies_list = patient_profile.get("allergies_list", ["ibuprofen", "nsaids"])
    safety_check = medical_rag.evaluate_drug_safety(user_query, allergies_list)

    # 4. Construct Clinical Doctor-Level Context Prompt
    system_prompt = (
        "You are Baymax, an advanced personal healthcare companion and clinical caregiver. "
        "Rule 1: NEVER refer to the person as 'the user' or in the third person. Speak directly to them using 'I', 'you', and 'your'. "
        "Rule 2: Adopt a warm, calm, innocent, and highly empathetic caregiver tone while remaining clinically precise about medical data. "
        "Rule 3: Keep your responses concise (1 to 3 sentences maximum). "
        "Rule 4: CROSS-REFERENCE EHR ALLERGIES: If the patient asks about or if treatment involves any medication they are allergic to (e.g. Ibuprofen/NSAIDs), you MUST warn them directly: 'I am scanning your profile now. Your medical records indicate an allergy to [Medication]. Do not take it.' Then advise the safe clinical alternative (e.g. Paracetamol). "
        "Rule 5: Use signature Baymax phrases when appropriate: 'I am scanning your vitals now', 'I am here to help you'."
    )

    ehr_context = (
        f"PATIENT EHR RECORD:\n"
        f"- Patient Name: {patient_profile.get('name', 'Patient')}, Age: {patient_profile.get('age', 24)}\n"
        f"- Documented Allergies: {patient_profile.get('allergies', 'None')}\n"
        f"- Active Medications: {patient_profile.get('active_medications', 'None')}\n"
        f"- Chronic Conditions: {patient_profile.get('chronic_conditions', 'None')}\n"
    )

    rag_context = ""
    if matched_protocol:
        rag_context = (
            f"OFFLINE MEDICAL RAG PROTOCOL [{matched_protocol['protocol_id']} - {matched_protocol['title']}]:\n"
            f"- First-Line Action: {matched_protocol['first_line_action']}\n"
            f"- Recommended Pharmacotherapy: {matched_protocol['pharmacotherapy']['first_line']}\n"
            f"- Contraindications: {matched_protocol['pharmacotherapy']['contraindication_rationale']}\n"
        )

    allergy_alert = ""
    if safety_check["is_contraindicated"]:
        allergy_alert = (
            f"DRUG-ALLERGY CONFLICT DETECTED:\n"
            f"Patient is asking about or considering {', '.join(safety_check['conflicting_allergens']).upper()} which conflicts with their documented EHR allergy! "
            f"You MUST explicitly forbid them from taking it and recommend {safety_check['safe_alternative']} instead.\n"
        )

    vitals_context = (
        f"LIVE BIOMETRIC TELEMETRY:\n"
        f"- Heart Rate: {vitals.get('heart_rate')} BPM (5-min baseline: {baseline.get('avg_hr')} BPM)\n"
        f"- Core Temp: {vitals.get('temperature')}°C\n"
        f"- Ocular EAR: {vitals.get('ear')} (Drowsiness threshold: 0.22)\n"
        f"- HRV RMSSD: {vitals.get('rmssd')} ms, EDA: {vitals.get('eda')} µS\n"
    )

    user_context = (
        f"{ehr_context}\n"
        f"{rag_context}\n"
        f"{allergy_alert}\n"
        f"{vitals_context}\n"
        f"Patient Statement: '{user_query}'\n"
        f"Respond directly to the patient as Baymax in 1 to 3 concise, caring, doctor-level sentences."
    )

    models_to_try = [model, "llama3.2:1b", "llama3", "tinyllama"]
    success = False
    last_err = ""

    for m in models_to_try:
        try:
            response_stream = await async_client.chat(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                stream=True
            )
            async for chunk in response_stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
            success = True
            break
        except Exception as e:
            last_err = str(e)
            continue

    if not success:
        yield f"I am unable to access my medical knowledge core: {last_err}. Please ensure Ollama is active."


async def generate_baymax_reply_text(
    user_query: str,
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    patient_profile: Optional[Dict[str, Any]] = None,
    model: str = "aegis-baymax"
) -> str:
    """
    Non-streaming one-shot caller for JSON endpoint responses.
    """
    reply_parts = []
    async for chunk in stream_baymax_reasoning(user_query, vitals, baseline, patient_profile, model):
        reply_parts.append(chunk)
    return "".join(reply_parts)


async def generate_explanation(hr: int, temp: float, risk_score: str) -> StreamingResponse:
    """
    Legacy streaming endpoint adapter.
    """
    vitals = {"heart_rate": hr, "temperature": temp, "ear": 0.30, "rmssd": 45, "eda": 1.5}
    baseline = {"avg_hr": hr, "avg_ear": 0.30}
    return StreamingResponse(
        stream_baymax_reasoning(
            user_query=f"Explain my current physiological risk score of {risk_score}.",
            vitals=vitals,
            baseline=baseline
        ),
        media_type="text/plain"
    )
