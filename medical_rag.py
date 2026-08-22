"""
AEGIS Medical RAG Core - Offline Clinical Knowledge Base & Protocol Retrieval
Inspired by BioMistral / Medical-RAG-LLM and EHRGym architectures.
Provides deterministic, offline retrieval of clinical practice guidelines,
pharmacotherapy alternatives, and drug-allergy contraindication cross-referencing.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


CLINICAL_PROTOCOLS: List[Dict[str, Any]] = [
    {
        "protocol_id": "CLIN-PROT-FEV-01",
        "title": "Acute Febrile Response & Hyperthermia Protocol",
        "category": "Thermal Regulation / Infectious Response",
        "keywords": ["fever", "temperature", "febrile", "hot", "spiking", "pyrexia", "ibuprofen", "paracetamol", "tylenol", "shivering", "chills", "feverish"],
        "summary": "Clinical protocol for managing acute core temperature elevation (> 37.8°C) and metabolic thermal strain.",
        "first_line_action": "Rest in a cool, ventilated environment; hydration with room-temperature fluids (500 mL/hr); application of tepid/cool compresses to forehead, axillae, and posterior neck.",
        "pharmacotherapy": {
            "first_line": "Paracetamol (Acetaminophen) 500mg - 1000mg orally every 4 to 6 hours (maximum 4000mg in 24 hours).",
            "second_line": "Cold hydration therapy and passive ambient cooling.",
            "contraindicated_drugs": ["ibuprofen", "nsaids", "aspirin", "naproxen"],
            "contraindication_rationale": "NSAIDs/Ibuprofen are contraindicated in patients with documented NSAID hypersensitivity, asthma/bronchospasm risk, active GI ulcers, or acute renal impairment. Paracetamol is the safe therapeutic alternative."
        },
        "escalation_criteria": "Core temperature >= 39.5°C, persistent fever > 72 hours, neck stiffness, confusion, or lack of response to antipyretics."
    },
    {
        "protocol_id": "CLIN-PROT-HEAT-02",
        "title": "Heat Exhaustion & Environmental Heat Strain Protocol",
        "category": "Environmental & Thermal Emergencies",
        "keywords": ["heat", "exhaustion", "sunstroke", "heatstroke", "overheating", "sweating", "heat stress", "thermal"],
        "summary": "Clinical management of acute heat exhaustion caused by exertion or high ambient temperature.",
        "first_line_action": "Immediate cessation of all physical exertion; move to an air-conditioned or shaded area; loosen restrictive clothing; elevate legs slightly.",
        "pharmacotherapy": {
            "first_line": "Oral Rehydration Salts (ORS) or balanced electrolyte beverages containing sodium (20-30 mEq/L) and potassium (2-5 mEq/L).",
            "second_line": "Misting skin with water combined with continuous fanning.",
            "contraindicated_drugs": ["caffeine", "stimulants", "alcohol", "diuretics"],
            "contraindication_rationale": "Diuretics and stimulants worsen intravascular volume depletion and impair thermoregulation."
        },
        "escalation_criteria": "Altered mental status, cessation of sweating with hot dry skin, seizures, or vomiting preventing oral rehydration (signs of Heat Stroke)."
    },
    {
        "protocol_id": "CLIN-PROT-EYE-03",
        "title": "Digital Eye Strain (CVS) & Somnolence Recovery Protocol",
        "category": "Occupational & Ophthalmic Fatigue",
        "keywords": ["eye", "eyes", "burning", "vision", "screen", "strain", "tired", "sleepy", "fatigue", "drowsy", "somnolence", "blink", "drowsiness"],
        "summary": "Management of Computer Vision Syndrome (CVS), tear film evaporation, and ocular motor fatigue.",
        "first_line_action": "Enforce the 20-20-20 Rule (every 20 minutes, focus on an object 20 feet away for 20 seconds); perform deliberate complete blinks for 10 seconds; reduce display glare.",
        "pharmacotherapy": {
            "first_line": "Preservative-free lubricating artificial tear drops (carboxymethylcellulose 0.5% or polyethylene glycol 0.4%).",
            "second_line": "Warm eyelid compress for 5 minutes to restore meibomian lipid layer.",
            "contraindicated_drugs": ["vasoconstrictor eye drops (tetrahydrozoline)"],
            "contraindication_rationale": "Prolonged use of vasoconstrictor drops causes rebound hyperemia and exacerbates ocular surface dryness."
        },
        "escalation_criteria": "If Ocular Eye Aspect Ratio (EAR) falls below 0.22 indicating microsleep or somnolence, mandate a 20-30 minute sleep rest cycle."
    },
    {
        "protocol_id": "CLIN-PROT-DEHYD-04",
        "title": "Dehydration & Autonomic Volume Depletion Protocol",
        "category": "Fluid Balance & Nephrology",
        "keywords": ["water", "dehydration", "thirsty", "dry mouth", "dizzy", "headache", "fluid", "hydration"],
        "summary": "Protocol for restoring intravascular fluid volume and cellular hydration equilibrium.",
        "first_line_action": "Gradual oral fluid intake: 500 mL over 30 minutes, followed by 250 mL every 15 minutes until symptoms resolve.",
        "pharmacotherapy": {
            "first_line": "Hypotonic to isotonic oral rehydration solutions with glucose-electrolyte cotransport matrix.",
            "second_line": "Coconut water or diluted fruit juices with a pinch of salt.",
            "contraindicated_drugs": ["pure hypertonic sugary drinks", "energy drinks"],
            "contraindication_rationale": "High-osmolarity drinks draw fluid into the intestinal lumen, exacerbating systemic dehydration."
        },
        "escalation_criteria": "Postural hypotension, dark oliguria (< 500 mL/day), sunken eyes, or prolonged capillary refill time (> 3 seconds)."
    },
    {
        "protocol_id": "CLIN-PROT-CARD-05",
        "title": "Acute Tachycardia & Autonomic Stress Protocol",
        "category": "Cardiovascular & Autonomic Regulation",
        "keywords": ["heart", "tachycardia", "palpitations", "racing heart", "rapid pulse", "chest", "anxiety", "bpm", "cardiac"],
        "summary": "Management of sinus tachycardia triggered by stress, caffeine, or physiological over-arousal.",
        "first_line_action": "Seated rest in semi-Fowler position; diaphragmatic breathing (4-second inhale, 7-second hold, 8-second exhale); cold water face immersion (mammalian diving reflex).",
        "pharmacotherapy": {
            "first_line": "Vagal nerve stimulation maneuvers and oral hydration.",
            "second_line": "Electrolyte supplementation (magnesium glycinate / potassium).",
            "contraindicated_drugs": ["sympathomimetics", "pseudoephedrine", "energy drinks"],
            "contraindication_rationale": "Adrenergic stimulants exacerbate cardiac workload and increase arrhythmia propensity."
        },
        "escalation_criteria": "Resting Heart Rate > 140 BPM, crushing chest pressure radiating to arm or jaw, syncope, or severe dyspnea."
    },
    {
        "protocol_id": "CLIN-PROT-BURN-06",
        "title": "Minor Thermal Injury & Superficial Burn Protocol",
        "category": "Dermatology & Trauma",
        "keywords": ["burn", "scald", "blister", "hot water", "fire", "burned", "skin burn"],
        "summary": "First-aid clinical guidelines for 1st-degree and minor 2nd-degree thermal skin burns.",
        "first_line_action": "Immediately irrigate burn with cool, running tap water for 10 to 20 minutes (do not use ice); gently remove non-adherent rings or clothing.",
        "pharmacotherapy": {
            "first_line": "Topical pure Aloe Vera gel or silver sulfadiazine / hydrogel dressing; oral Paracetamol for pain.",
            "second_line": "Sterile non-stick gauze wrap.",
            "contraindicated_drugs": ["ice cubes", "butter", "oil", "toothpaste"],
            "contraindication_rationale": "Direct ice application causes vasoconstrictive tissue ischemia and frostbite; butter/oils trap heat and introduce bacterial infection vectors."
        },
        "escalation_criteria": "Burn area > 3 inches in diameter, burns on face, hands, joints, or genitalia, or circumferential burns."
    }
]


class OfflineMedicalRAG:
    """
    Offline Medical Knowledge Retrieval Engine.
    Performs token-overlap and keyword relevance scoring across verified clinical protocols.
    Performs drug-allergy safety contraindication cross-referencing.
    """

    def __init__(self, protocols: Optional[List[Dict[str, Any]]] = None):
        self.protocols = protocols or CLINICAL_PROTOCOLS

    def retrieve_protocol(self, query_text: str, threshold: float = 0.15) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most relevant clinical protocol for a patient inquiry.
        """
        query_clean = re.sub(r"[^a-zA-Z0-9\s]", "", query_text.lower())
        query_tokens = set(query_clean.split())
        if not query_tokens:
            return None

        best_score = 0.0
        best_protocol = None

        for proto in self.protocols:
            score = 0.0
            keywords = [k.lower() for k in proto["keywords"]]
            
            # 1. Exact keyword match
            for kw in keywords:
                if kw in query_clean:
                    score += 2.0
                elif any(q in kw for q in query_tokens):
                    score += 0.8

            # 2. Title & summary overlap
            title_tokens = set(re.sub(r"[^a-zA-Z0-9\s]", "", proto["title"].lower()).split())
            overlap = query_tokens.intersection(title_tokens)
            score += len(overlap) * 1.5

            if score > best_score and score >= threshold:
                best_score = score
                best_protocol = proto

        if best_protocol:
            return {
                "protocol_id": best_protocol["protocol_id"],
                "title": best_protocol["title"],
                "category": best_protocol["category"],
                "first_line_action": best_protocol["first_line_action"],
                "pharmacotherapy": best_protocol["pharmacotherapy"],
                "escalation_criteria": best_protocol["escalation_criteria"],
                "relevance_score": round(best_score, 2)
            }
        return None

    def evaluate_drug_safety(
        self,
        query_text: str,
        patient_allergies: List[str]
    ) -> Dict[str, Any]:
        """
        Cross-reference the query and retrieved protocol against the patient's EHR allergies.
        Detects if patient is asking about or considering a contraindicated medication.
        """
        query_lower = query_text.lower()
        allergies_clean = [a.strip().lower() for a in patient_allergies if a.strip()]

        flagged_allergens = []
        for allergy in allergies_clean:
            if allergy in query_lower:
                flagged_allergens.append(allergy)

        is_contraindicated = len(flagged_allergens) > 0
        safe_alternative = "Paracetamol (Acetaminophen)" if any(a in ["ibuprofen", "nsaids", "aspirin"] for a in flagged_allergens) else "non-pharmacological cooling and hydration"

        return {
            "is_contraindicated": is_contraindicated,
            "conflicting_allergens": flagged_allergens,
            "safe_alternative": safe_alternative,
            "clinical_warning": (
                f"STRICT CONTRAINDICATION: Patient has documented allergy to {', '.join(flagged_allergens).upper()}. "
                f"Do NOT take this medication. Safe clinical alternative: {safe_alternative}."
            ) if is_contraindicated else "No immediate drug-allergy conflict detected."
        }

    def list_all_protocols(self) -> List[Dict[str, Any]]:
        """Return full index of available offline protocols."""
        return [
            {
                "protocol_id": p["protocol_id"],
                "title": p["title"],
                "category": p["category"],
                "keywords": p["keywords"]
            }
            for p in self.protocols
        ]
