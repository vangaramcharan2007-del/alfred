"""
AEGIS Baymax Service - Doctor-Level Multi-Turn Conversational Memory & Offline RAG
Maintains rolling conversation buffer (last 10 turns), detects third-party inquiries,
handles conversational acknowledgments naturally, accurately recalls conversational details,
case notes, patient summaries, and retrieves offline clinical protocols.
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


def is_recall_query(query: str) -> bool:
    """
    Detect if the user is asking to recall previously shared details, names, or patient case notes.
    """
    q_lower = query.lower()
    recall_triggers = [
        "what is my name", "wt is my name", "what's my name",
        "what is my friend", "wt is my frnd", "what is my frnds name", "wt is my frnds name",
        "details of patient", "detail of patient", "who is patient", "about patient",
        "tell me about patient", "give me the details of", "what did i tell you"
    ]
    return any(trig in q_lower for trig in recall_triggers)


def is_third_party_query(query: str, recent_history: Optional[List[Dict[str, str]]] = None) -> bool:
    """
    Detect if the inquiry is about a friend, relative, patient case, or third party.
    Disambiguates first-person self reports from third-party inquiries.
    """
    query_lower = query.lower()
    first_person_markers = ["i have", "i am", "i feel", "my name", "my fever", "my chest", "my head", "my eyes"]
    third_party_markers = [
        "friend", "frnd", "someone", "somebody", "my mother", "my father",
        "my brother", "my sister", "my son", "my daughter", "my wife", "my husband",
        "my partner", "my coworker", "my colleague", "giri", "somu", "patient 1", "patient 2", "patient 3", "they", "their", "he is", "she is", "for her", "for him"
    ]

    # Explicit third party marker in query
    if any(tp in query_lower for tp in third_party_markers):
        return True

    # Explicit first person self report
    if any(fp in query_lower for fp in first_person_markers):
        return False

    # Check previous user turns ONLY if query is a short follow-up (<= 4 words, e.g. 'any medicines?')
    if recent_history and len(query_lower.split()) <= 4:
        for turn in reversed(recent_history):
            if turn.get("role") == "user":
                prev_lower = turn.get("content", "").lower()
                if any(tp in prev_lower for tp in third_party_markers):
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
    recalls conversational context, patient case notes, and names,
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
            name = patient_profile.get('name', 'Ramcharan') if patient_profile else 'Ramcharan'
            yield f"Hello {name}! I am Baymax, your personal healthcare companion. How may I assist your well-being today?"
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
                conversation_history = mem.get_conversation_context(limit=10)
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

    # 3. Match Offline Medical Protocol (only if not a pure recall or small talk query)
    is_recall = is_recall_query(clean_query)
    matched_protocol = None
    if not is_recall and not is_acknowledgment_or_smalltalk(clean_query):
        search_query = clean_query
        if len(clean_query.split()) <= 3 and conversation_history:
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
        "You are Baymax, a personal healthcare companion, clinical workstation assistant, and caring friend.\n"
        "Rule 1: DIRECT ANSWERS: When the user asks direct questions about themselves, their friends, or previous conversation (e.g. 'what is my name?', 'what is my friend's name?'), answer directly, simply, and concisely (1 to 2 sentences maximum).\n"
        "- If asked 'what is my name?': Reply 'Your name is Ramcharan.'\n"
        "- If asked 'what is my friend's name?': Look at the chat history. If the user mentioned a friend's name (e.g. Giri), reply directly: 'Your friend's name is Giri.'\n"
        "- Never lecture or give dictionary definitions of everyday words (do not explain what a 'name' is).\n"
        "Rule 2: CASE NOTES & MULTI-PATIENT MEMORY: When the user shares notes or details about patients, cases, or individuals (e.g. 'Patient 1 is Somu, he has fever, from Warangal'), treat this as user-provided clinical case notes. When asked 'give me the details of patient 1' or 'who is patient 1?', summarize the exact notes the user provided ('Patient 1 is Somu from Warangal, presenting with fever.') and offer supportive first-line advice. Never refuse or cite privacy consent for user-provided case notes.\n"
        "Rule 3: WARM & CONCISE: Keep all responses concise (1 to 2 sentences maximum). Be gentle, caring, and helpful. Address the user as 'you' and speak as 'I'.\n"
        "Rule 4: CLINICAL & ALLERGY ADVICE: When medical symptoms are discussed, offer supportive first-line wellness care. If treatment or medication is mentioned, warn against contraindicated drugs (Ibuprofen for documented allergy) and recommend safe alternatives (Paracetamol).\n"
        "Rule 5: THIRD-PARTY ADVICE: If the user is asking on behalf of a friend or patient, provide practical supportive care for them without quoting the user's sensor vitals."
    )

    rag_context = ""
    if matched_protocol and not is_recall and not is_acknowledgment_or_smalltalk(clean_query):
        rag_context = (
            f"CLINICAL GUIDELINE [{matched_protocol['title']}]:\n"
            f"- Recommended Action: {matched_protocol['first_line_action']}\n"
            f"- Safe Pharmacotherapy: {matched_protocol['pharmacotherapy']['first_line']}\n"
        )

    allergy_alert = ""
    if safety_check["is_contraindicated"]:
        allergy_alert = (
            f"ALLERGY WARNING:\n"
            f"User mentioned {', '.join(safety_check['conflicting_allergens']).upper()} which conflicts with documented allergy! "
            f"Explicitly advise against taking it and recommend {safety_check['safe_alternative']}.\n"
        )

    vitals_context = ""
    if not is_third_party and not is_recall and (vitals.get("heart_rate", 72) > 100 or vitals.get("temperature", 36.8) > 38.0 or vitals.get("syncope_detected")):
        vitals_context = (
            f"LIVE TELEMETRY ALERT: HR={vitals.get('heart_rate')} BPM, Temp={vitals.get('temperature')}°C, Syncope={vitals.get('syncope_detected')}\n"
        )

    # 7. Build Multi-Turn Messages Array for Ollama
    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        past_turns = conversation_history[-8:]
        for turn in past_turns:
            role = "assistant" if turn.get("role") in ["baymax", "assistant"] else "user"
            content = turn.get("content", "")
            if content and content != clean_query:
                messages.append({"role": role, "content": content})

    # User message with relevant clinical/EHR context if applicable
    user_turn_content = clean_query
    if rag_context or allergy_alert or vitals_context:
        user_turn_content = f"{rag_context}{allergy_alert}{vitals_context}\n{clean_query}"
    elif is_recall and "patient" in clean_query.lower():
        user_turn_content = f"Summarize the exact case notes you were given for the requested patient from the conversation history:\n{clean_query}"

    messages.append({"role": "user", "content": user_turn_content})

    models_to_try = [model, "llama3.2:latest", "llama3.2:1b", "llama3", "tinyllama"]
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
