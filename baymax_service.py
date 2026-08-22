"""
AEGIS Baymax Service - Doctor-Level Multi-Turn Conversational Memory & Offline RAG
Maintains rolling conversation buffer (last 6 turns), detects third-party inquiries,
handles conversational acknowledgments naturally, and retrieves offline clinical protocols.
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


def is_acknowledgment_or_smalltalk(query: str) -> bool:
    """
    Detect short conversational acknowledgments and greetings that do not require medical search.
    """
    clean = re.sub(r"[^a-zA-Z\s]", "", query.lower()).strip()
    ack_words = {
        "ok", "k", "okay", "alright", "all right", "got it", "understood",
        "thanks", "thank you", "thx", "cool", "great", "fine", "yes", "no",
        "sure", "nice", "hello", "hi", "hey", "bye", "goodbye", "good night", "see you"
    }
    return clean in ack_words or (len(clean.split()) == 1 and clean in ack_words)


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
    Handles small talk gracefully, passes conversation history to Ollama,
    matches offline RAG protocols, and checks EHR drug-allergy contraindications.
    """
    clean_query = user_query.strip()
    
    # 1. Handle Simple Acknowledgments / Small Talk Fast-Path
    if is_acknowledgment_or_smalltalk(clean_query):
        clean_lower = clean_query.lower()
        if clean_lower in ["ok", "k", "okay", "got it", "understood", "alright"]:
            yield "I am here whenever you need me. Please let me know if you would like me to check your vitals or assist with any other questions."
            return
        elif clean_lower in ["thanks", "thank you", "thx"]:
            yield "You are welcome. I am satisfied with your care. Take good care of yourself!"
            return
        elif clean_lower in ["hello", "hi", "hey"]:
            yield f"Hello {patient_profile.get('name', '') if patient_profile else ''}! I am Baymax, your personal healthcare companion. How may I assist your well-being today?"
            return
        elif clean_lower in ["bye", "goodbye", "good night", "see you"]:
            yield "I will remain on standby to monitor your health. Rest well and stay safe!"
            return

    # 2. Retrieve EHR Patient Profile and Recent Conversation History
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

    # 3. Match Offline Medical Protocol
    search_query = clean_query
    if len(clean_query.split()) <= 3 and conversation_history and not is_acknowledgment_or_smalltalk(clean_query):
        for turn in reversed(conversation_history):
            if turn.get("role") == "user":
                search_query = f"{turn.get('content', '')} {clean_query}"
                break

    matched_protocol = medical_rag.retrieve_protocol(search_query)

    # 4. Evaluate Drug-Allergy Safety
    allergies_list = patient_profile.get("allergies_list", ["ibuprofen", "nsaids"])
    safety_check = medical_rag.evaluate_drug_safety(clean_query, allergies_list)

    # 5. Determine Third-Party vs Self Inquiry
    is_third_party = is_third_party_query(clean_query, conversation_history)

    # 6. Construct System Prompt
    system_prompt = (
        "You are Baymax, an empathetic, caring, and knowledgeable personal healthcare companion. "
        "Rule 1: Speak directly to the person ('I' and 'you'). Never speak in the third person or say 'the user'. "
        "Rule 2: Adopt a warm, calm, supportive, and scientifically accurate tone. "
        "Rule 3: Answer questions about health concepts, psychological traits, or medical conditions (such as ADHD, fatigue, fever, dehydration) informatively and helpfully using established science. "
        "Rule 4: CROSS-REFERENCE EHR ALLERGIES: If the patient asks about or if treatment involves any medication they are allergic to (e.g. Ibuprofen/NSAIDs), you MUST warn them directly: 'I am scanning your profile now. Your medical records indicate an allergy to [Medication]. Do not take it.' Then recommend the safe clinical alternative (e.g. Paracetamol). "
        "Rule 5: THIRD-PARTY & FRIEND INQUIRIES: If the speaker is asking for a friend or third party (e.g. 'my friend is suffering from depression'), DO NOT quote the speaker's sensor vitals. Address the friend's clinical situation directly. "
        "Rule 6: Keep responses concise (1 to 3 sentences maximum)."
    )

    ehr_context = (
        f"PATIENT PROFILE:\n"
        f"- Name: {patient_profile.get('name', 'Patient')}, Age: {patient_profile.get('age', 24)}\n"
        f"- Allergies: {patient_profile.get('allergies', 'None')}\n"
    )

    rag_context = ""
    if matched_protocol:
        rag_context = (
            f"VERIFIED CLINICAL KNOWLEDGE [{matched_protocol['title']}]:\n"
            f"- Information & First-Line Action: {matched_protocol['first_line_action']}\n"
            f"- Clinical Management: {matched_protocol['pharmacotherapy']['first_line']}\n"
        )

    allergy_alert = ""
    if safety_check["is_contraindicated"]:
        allergy_alert = (
            f"DRUG-ALLERGY CONFLICT:\n"
            f"Speaker asks about {', '.join(safety_check['conflicting_allergens']).upper()} which conflicts with documented allergy! "
            f"Explicitly advise against taking it and recommend {safety_check['safe_alternative']}.\n"
        )

    vitals_context = ""
    if not is_third_party:
        vitals_context = (
            f"SPEAKER VITALS: HR={vitals.get('heart_rate')} BPM, Temp={vitals.get('temperature')}°C, EAR={vitals.get('ear')}\n"
        )
    else:
        vitals_context = "CONTEXT: Inquiring about a third party. Do NOT quote speaker's vitals.\n"

    # Neutral educational framing for clinical queries
    educational_prompt = clean_query
    if "good or bad" in clean_query.lower():
        educational_prompt = f"What is the medical perspective on {clean_query.lower().replace('good or bad', '').strip()}? (Explain its characteristics, strengths, and challenges)."

    current_turn_prompt = (
        f"{ehr_context}"
        f"{rag_context}"
        f"{allergy_alert}"
        f"{vitals_context}"
        f"Topic to explain: '{educational_prompt}'\n"
        f"As Baymax, provide a warm, encouraging, scientifically accurate explanation in 1 to 2 sentences:"
    )

    # 7. Build Multi-Turn Messages Array for Ollama
    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        past_turns = conversation_history[-4:]
        for turn in past_turns:
            role = "assistant" if turn.get("role") in ["baymax", "assistant"] else "user"
            content = turn.get("content", "")
            if content and content != clean_query:
                messages.append({"role": role, "content": content})

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
