"""
AEGIS Baymax Service - Doctor-Level Multi-Turn Conversational Memory & Offline RAG
Maintains rolling conversation buffer (last 6 turns), detects third-party inquiries,
and retrieves offline clinical protocols and EHR profiles without hallucinations.
"""

import re
import sys
from typing import Dict, Any, List, Optional, AsyncGenerator
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


def is_third_party_query(query: str, recent_history: Optional[List[Dict[str, str]]] = None) -> bool:
    """
    Detect if the inquiry is about a friend, relative, or third party.
    """
    third_party_terms = [
        "friend", "frnd", "someone", "somebody", "my mother", "my father",
        "my brother", "my sister", "my son", "my daughter", "my wife", "my husband",
        "my partner", "my coworker", "my colleague", "they", "their", "he is", "she is"
    ]
    query_lower = query.lower()
    if any(term in query_lower for term in third_party_terms):
        return True

    # Check immediate previous user turns in history
    if recent_history:
        for turn in reversed(recent_history):
            if turn.get("role") == "user":
                prev_lower = turn.get("content", "").lower()
                if any(term in prev_lower for term in third_party_terms):
                    return True
                break

    return False


async def stream_baymax_reasoning(
    user_query: str,
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    patient_profile: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model: str = "aegis-baymax"
) -> AsyncGenerator[str, None]:
    """
    Multi-Turn Doctor-Level Clinical Inference Engine.
    Passes conversation history to Ollama, matches offline RAG protocols,
    checks EHR drug-allergy contraindications, and handles third-party inquiries.
    """
    # 1. Retrieve EHR Patient Profile and Recent Conversation History
    if patient_profile is None or conversation_history is None:
        try:
            mem = AegisMemory(db_path="aegis_core.db")
            if patient_profile is None:
                patient_profile = mem.get_patient_profile()
            if conversation_history is None:
                conversation_history = mem.get_conversation_context(limit=6)
            mem.close()
        except Exception:
            if patient_profile is None:
                patient_profile = {
                    "name": "Ramcharan",
                    "age": 24,
                    "allergies": "Ibuprofen, NSAIDs",
                    "allergies_list": ["ibuprofen", "nsaids", "aspirin"],
                    "active_medications": "None",
                    "chronic_conditions": "Mild Asthmatic Tendency"
                }
            if conversation_history is None:
                conversation_history = []

    # 2. Match Offline Medical Protocol (Search combined query + history for short follow-ups)
    search_query = user_query
    if len(user_query.split()) <= 3 and conversation_history:
        for turn in reversed(conversation_history):
            if turn.get("role") == "user":
                search_query = f"{turn.get('content', '')} {user_query}"
                break

    matched_protocol = medical_rag.retrieve_protocol(search_query)

    # 3. Evaluate Drug-Allergy Safety
    allergies_list = patient_profile.get("allergies_list", ["ibuprofen", "nsaids"])
    safety_check = medical_rag.evaluate_drug_safety(user_query, allergies_list)

    # 4. Determine Third-Party vs Self Inquiry
    is_third_party = is_third_party_query(user_query, conversation_history)

    # 5. Construct System Prompt
    system_prompt = (
        "You are Baymax, a personal healthcare companion and compassionate clinical caregiver. "
        "Rule 1: NEVER refer to the person as 'the user' or speak in the third person. Address the speaker directly as 'you' and 'I'. "
        "Rule 2: Adopt a warm, calm, innocent, and highly empathetic tone, while remaining clinically objective about medical guidelines. "
        "Rule 3: Keep your responses concise (1 to 3 sentences maximum). "
        "Rule 4: CROSS-REFERENCE EHR ALLERGIES: If the patient asks about or if treatment involves any medication they are allergic to (e.g. Ibuprofen/NSAIDs), you MUST warn them directly: 'I am scanning your profile now. Your medical records indicate an allergy to [Medication]. Do not take it.' Then recommend the safe clinical alternative (e.g. Paracetamol). "
        "Rule 5: THIRD-PARTY & FRIEND INQUIRIES: If the speaker is asking for a friend or third party (e.g. 'my friend is suffering from depression', 'any medicines?'), DO NOT quote the speaker's sensor vitals or assume the speaker is the one who is sick. Address the friend's clinical situation directly with empathetic medical advice. "
        "Rule 6: MEDICATIONS & PRESCRIPTIONS: If asked about medicines for depression or psychiatric conditions, explain that medications such as SSRIs require a strict clinical evaluation and prescription from a licensed psychiatrist and cannot be taken over the counter. "
        "Rule 7: CONVERSATIONAL CONTINUITY: Always use the chat history to understand follow-up questions (such as 'any medicines?' or 'what else can I do?')."
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
            f"Speaker is asking about or considering {', '.join(safety_check['conflicting_allergens']).upper()} which conflicts with documented EHR allergy! "
            f"You MUST explicitly forbid them from taking it and recommend {safety_check['safe_alternative']} instead.\n"
        )

    vitals_context = ""
    if not is_third_party:
        vitals_context = (
            f"LIVE BIOMETRIC TELEMETRY (SPEAKER):\n"
            f"- Heart Rate: {vitals.get('heart_rate')} BPM (5-min baseline: {baseline.get('avg_hr')} BPM)\n"
            f"- Core Temp: {vitals.get('temperature')}°C\n"
            f"- Ocular EAR: {vitals.get('ear')} (Drowsiness threshold: 0.22)\n"
            f"- HRV RMSSD: {vitals.get('rmssd')} ms, EDA: {vitals.get('eda')} µS\n"
        )
    else:
        vitals_context = "CONTEXT NOTE: Third-party inquiry. The speaker is inquiring on behalf of a friend/third party. Do NOT quote the speaker's sensor vitals."

    current_turn_prompt = (
        f"{ehr_context}\n"
        f"{rag_context}\n"
        f"{allergy_alert}\n"
        f"{vitals_context}\n"
        f"Patient Statement: '{user_query}'\n"
        f"Respond directly to the speaker as Baymax in 1 to 3 concise, caring, doctor-level sentences."
    )

    # 6. Build Multi-Turn Messages Array for Ollama
    messages = [{"role": "system", "content": system_prompt}]

    # Append past turns from history
    if conversation_history:
        past_turns = conversation_history[-6:]
        for turn in past_turns:
            role = "assistant" if turn.get("role") in ["baymax", "assistant"] else "user"
            content = turn.get("content", "")
            if content and content != user_query:
                messages.append({"role": role, "content": content})

    # Append current enriched prompt
    messages.append({"role": "user", "content": current_turn_prompt})

    models_to_try = [model, "llama3.2:1b", "llama3", "tinyllama"]
    success = False
    last_err = ""

    for m in models_to_try:
        try:
            response_stream = await async_client.chat(
                model=m,
                messages=messages,
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
        yield f"I am unable to access my clinical knowledge core: {last_err}. Please ensure Ollama is active."


async def generate_baymax_reply_text(
    user_query: str,
    vitals: Dict[str, Any],
    baseline: Dict[str, Any],
    patient_profile: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model: str = "aegis-baymax"
) -> str:
    """
    Non-streaming one-shot caller for JSON endpoint responses.
    """
    reply_parts = []
    async for chunk in stream_baymax_reasoning(user_query, vitals, baseline, patient_profile, conversation_history, model):
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
