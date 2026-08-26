"""
AEGIS Multi-Agent Clinical Specialist Board Engine
===================================================
Simulates a collegiate, multi-specialist medical board:
1. Cardiology Specialist Agent (Dr. Aria Thorne, MD - Cardiology)
2. Pharmacology & Drug Safety Agent (Dr. Kavi Patel, PharmD - Clinical Pharmacology)
3. Emergency Critical Care Triage Agent (Dr. Marcus Vance, MD - Trauma & Intensive Care)
4. Clinical Board Synthesizer (Consensus Care Plan & Directive Formulation)
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SpecialistAssessment(BaseModel):
    specialist_id: str
    name: str
    role: str
    avatar_color: str
    confidence: float
    urgency_tier: str  # RED, YELLOW, GREEN
    findings: List[str]
    differential_diagnoses: List[str]
    immediate_recommendations: List[str]
    concerns_or_objections: List[str]


class ClinicalBoardConsensus(BaseModel):
    case_summary: str
    triage_tier: str  # RED (Immediate Resuscitation), YELLOW (Urgent), GREEN (Non-urgent)
    primary_consensus_diagnosis: str
    specialist_assessments: List[SpecialistAssessment]
    debate_transcript: List[Dict[str, str]]
    unified_care_plan: Dict[str, Any]
    escalation_required: bool
    generated_at: str


class CardiologyAgent:
    """Specialist in Hemodynamics, Arrhythmias, HRV, and Autonomic Failure."""

    def evaluate(self, vitals: Dict[str, Any], ehr_profile: Dict[str, Any]) -> SpecialistAssessment:
        hr = vitals.get("heart_rate", 72)
        rmssd = vitals.get("rmssd", 45.0)
        syncope = vitals.get("syncope_detected", False)
        posture = vitals.get("posture_status", "ERECT_NOMINAL")

        findings = []
        differentials = []
        recommendations = []
        objections = []
        urgency = "GREEN"
        confidence = 0.94

        if syncope:
            urgency = "RED"
            findings.append("Acute Syncope / Orthostatic Hemodynamic Collapse detected via 3-axis facial orientation.")
            differentials.extend(["Vasovagal Syncope", "Orthostatic Hypotension", "Arrhythmogenic Pre-Syncope"])
            recommendations.extend([
                "Maintain horizontal supine position with 30° leg elevation to restore cerebral perfusion.",
                "Continuous 12-lead ECG monitoring and non-invasive blood pressure (NIBP) tracking.",
                "Administer 500mL IV Normal Saline bolus if hypovolemic.",
            ])
            objections.append("Patient must NOT be mobilized until heart rate stabilizes and orthostatic vitals normalize.")
        elif hr > 115:
            urgency = "YELLOW"
            findings.append(f"Sinus Tachycardia ({hr} BPM) with diminished HRV RMSSD ({rmssd:.1f}ms) indicating sympathetic hyperactivation.")
            differentials.extend(["Systemic Inflammatory Response / Early Sepsis", "Dehydration", "Hyperpyrexia-induced Tachycardia"])
            recommendations.extend([
                "Evaluate for source of infection or hypermetabolic stress.",
                "Initiate oral or IV hydration.",
                "Monitor for progression into tachyarrhythmia.",
            ])
        elif hr < 50:
            urgency = "YELLOW"
            findings.append(f"Significant Sinus Bradycardia ({hr} BPM) with elevated vagal tone.")
            differentials.extend(["Sinus Node Dysfunction", "Medication-induced Bradycardia", "Vagal Hyper-reactivity"])
            recommendations.extend([
                "Review active medications for beta-blockers or calcium channel blockers.",
                "Prepare Atropine 0.5mg IV if symptomatic hypoperfusion develops.",
            ])
        else:
            findings.append(f"Normal Cardiac Rhythm. Heart Rate is nominal at {hr} BPM; HRV RMSSD is healthy ({rmssd:.1f}ms).")
            differentials.append("Cardiac Homeostasis")
            recommendations.append("Continue routine cardiac monitoring.")

        return SpecialistAssessment(
            specialist_id="cardiology",
            name="Dr. Aria Thorne, MD",
            role="Cardiology & Hemodynamics Specialist",
            avatar_color="#ef4444",
            confidence=confidence,
            urgency_tier=urgency,
            findings=findings,
            differential_diagnoses=differentials,
            immediate_recommendations=recommendations,
            concerns_or_objections=objections,
        )


class PharmacologyAgent:
    """Specialist in Drug-Drug Interactions, Allergies, Pharmacokinetics, and Contraindications."""

    def evaluate(self, query_or_drugs: str, ehr_profile: Dict[str, Any], vitals: Dict[str, Any]) -> SpecialistAssessment:
        allergies_list = [a.lower().strip() for a in ehr_profile.get("allergies_list", ["ibuprofen", "nsaids"])]
        active_meds = ehr_profile.get("active_medications", "")
        chronic = ehr_profile.get("chronic_conditions", "")
        q_lower = query_or_drugs.lower()

        findings = []
        differentials = []
        recommendations = []
        objections = []
        urgency = "GREEN"
        confidence = 0.96

        # Check Ibuprofen / NSAID Allergy
        if any(a in q_lower or a in ["ibuprofen", "nsaids"] for a in allergies_list) and ("ibuprofen" in q_lower or "nsaid" in q_lower or "pain" in q_lower or "fever" in q_lower):
            urgency = "RED"
            findings.append(f"CRITICAL ALLERGY CONTRAINDICATION: Documented severe IgE-mediated allergy to {', '.join(allergies_list).upper()}.")
            differentials.extend(["Drug-Induced Anaphylaxis Risk", "Bronchospasm / Asthma Exacerbation"])
            recommendations.extend([
                "STRICTLY FORBID all NSAIDs (Ibuprofen, Naproxen, Aspirin, Diclofenac).",
                "Approve Paracetamol (Acetaminophen) 500mg - 1000mg PO every 6 hours (Max 4000mg/24h) for antipyresis and analgesia.",
            ])
            objections.append("NSAID administration carries an immediate 88% risk of anaphylactoid reaction in this patient.")
        elif "asthma" in chronic.lower() and "beta" in q_lower:
            urgency = "YELLOW"
            findings.append("Drug-Disease Interaction: Non-selective beta blockers contraindicated with documented Asthma.")
            recommendations.append("Use cardio-selective agents (Metoprolol/Atenolol) with caution or alternative rate-control.")
        else:
            findings.append(f"Pharmacological review nominal. Documented allergies respected: {', '.join(allergies_list).upper()}.")
            recommendations.append("First-line antipyretic: Paracetamol 500mg oral suspension/tablet.")

        return SpecialistAssessment(
            specialist_id="pharmacology",
            name="Dr. Kavi Patel, PharmD",
            role="Clinical Pharmacology & Toxicology Specialist",
            avatar_color="#8b5cf6",
            confidence=confidence,
            urgency_tier=urgency,
            findings=findings,
            differential_diagnoses=differentials,
            immediate_recommendations=recommendations,
            concerns_or_objections=objections,
        )


class CriticalCareTriageAgent:
    """Specialist in Trauma, Sepsis, Resuscitation, and Clinical Triage."""

    def evaluate(self, vitals: Dict[str, Any], ehr_profile: Dict[str, Any]) -> SpecialistAssessment:
        hr = vitals.get("heart_rate", 72)
        temp = vitals.get("temperature", 36.8)
        syncope = vitals.get("syncope_detected", False)
        resp_rate = vitals.get("respiratory_rate", 16)
        spo2 = vitals.get("spo2", 98)

        findings = []
        differentials = []
        recommendations = []
        objections = []
        urgency = "GREEN"
        confidence = 0.95

        # Compute Quick SOFA (qSOFA) Score
        qsofa = 0
        if resp_rate >= 22:
            qsofa += 1
            findings.append(f"Tachypnea: Respiratory Rate {resp_rate}/min (>= 22/min) [+1 qSOFA]")
        if syncope:
            qsofa += 1
            findings.append("Altered Mentation / Syncope Drop [+1 qSOFA]")
        if temp > 38.5 or hr > 120:
            findings.append(f"Systemic Inflammatory Vitals: Core Temp {temp:.1f}°C, HR {hr} BPM.")

        if syncope or qsofa >= 2:
            urgency = "RED"
            findings.append(f"CRITICAL TRIAGE LEVEL 1 (RED): Resuscitation tier activated (qSOFA: {qsofa}).")
            differentials.extend(["Septic Shock / Sepsis-3", "Neurocardiogenic Syncope", "Severe Hypoxemic / Metabolic Crisis"])
            recommendations.extend([
                "Activate Critical Care Rapid Response Team (RRT).",
                "Secure airway, establish high-flow oxygen, insert large-bore IV access.",
                "Draw blood cultures, serum lactate, and full arterial blood gas (ABG) panel.",
            ])
            objections.append("Do not discharge or delay monitoring; immediate ICU / HDU bed allocation required.")
        elif temp > 38.0 or hr > 105:
            urgency = "YELLOW"
            findings.append(f"URGENT TRIAGE LEVEL 2 (YELLOW): Febrile inflammatory state requiring medical observation.")
            differentials.extend(["Infectious Etiology (Bacterial/Viral)", "Acute Dehydration"])
            recommendations.extend([
                "Perform physical examination, urinalysis, and chest radiography.",
                "Hydration and antipyretic administration.",
            ])
        else:
            findings.append(f"TRIAGE LEVEL 3 (GREEN): Patient vitals are within standard ambulatory physiological range.")
            recommendations.append("Standard ward care and scheduled vital re-checks every 4 hours.")

        return SpecialistAssessment(
            specialist_id="critical_care",
            name="Dr. Marcus Vance, MD",
            role="Emergency & Critical Care Triage Specialist",
            avatar_color="#06b6d4",
            confidence=confidence,
            urgency_tier=urgency,
            findings=findings,
            differential_diagnoses=differentials,
            immediate_recommendations=recommendations,
            concerns_or_objections=objections,
        )


class ClinicalBoardSynthesizer:
    """Orchestrates multi-agent collegiate deliberation and synthesizes consensus care plan."""

    def __init__(self):
        self.cardiology = CardiologyAgent()
        self.pharmacology = PharmacologyAgent()
        self.critical_care = CriticalCareTriageAgent()

    def convene_board(
        self,
        query: str,
        vitals: Dict[str, Any],
        ehr_profile: Dict[str, Any]
    ) -> ClinicalBoardConsensus:
        # 1. Independent Assessments
        cardio_assess = self.cardiology.evaluate(vitals, ehr_profile)
        pharm_assess = self.pharmacology.evaluate(query, ehr_profile, vitals)
        triage_assess = self.critical_care.evaluate(vitals, ehr_profile)

        specialist_list = [cardio_assess, pharm_assess, triage_assess]

        # 2. Determine Highest Urgency Tier
        urgency_order = {"RED": 3, "YELLOW": 2, "GREEN": 1}
        max_urgency = max(specialist_list, key=lambda a: urgency_order.get(a.urgency_tier, 1)).urgency_tier

        # 3. Formulate Collegiate Debate Transcript
        patient_name = ehr_profile.get("name", "Patient")
        debate_transcript = [
            {
                "speaker": "Dr. Aria Thorne (Cardiology)",
                "avatar": "🫀",
                "color": "#ef4444",
                "statement": (
                    f"Reviewing {patient_name}'s hemodynamic profile: Heart Rate is {vitals.get('heart_rate', 72)} BPM "
                    f"with RMSSD {vitals.get('rmssd', 45.0):.1f}ms. "
                    f"{'Syncope collapse detected!' if vitals.get('syncope_detected') else 'Rhythm is stable.'} "
                    f"My immediate recommendation is {cardio_assess.immediate_recommendations[0]}."
                )
            },
            {
                "speaker": "Dr. Kavi Patel (Pharmacology)",
                "avatar": "💊",
                "color": "#8b5cf6",
                "statement": (
                    f"From a pharmacotherapy standpoint, I have audited {patient_name}'s allergy ledger. "
                    f"{'WARNING: Severe allergy to ' + ', '.join(ehr_profile.get('allergies_list', ['Ibuprofen'])).upper() + ' prohibits NSAIDs! We must strictly use Paracetamol.' if pharm_assess.urgency_tier == 'RED' else 'Medication profile is clear for first-line antipyretics.'}"
                )
            },
            {
                "speaker": "Dr. Marcus Vance (Critical Care)",
                "avatar": "🚨",
                "color": "#06b6d4",
                "statement": (
                    f"Triage calculation assigns {patient_name} to Tier {max_urgency}. "
                    f"{'Resuscitation protocols are armed. Escalating to ICU Rapid Response.' if max_urgency == 'RED' else 'Patient can be safely managed under primary ward observation with regular monitoring.'}"
                )
            },
        ]

        # 4. Formulate Unified Consensus Care Plan
        all_recs = []
        for a in specialist_list:
            all_recs.extend(a.immediate_recommendations)

        care_plan = {
            "patient_uid": ehr_profile.get("patient_uid", "p-001"),
            "patient_name": patient_name,
            "triage_color": max_urgency,
            "resuscitation_required": max_urgency == "RED",
            "positioning": "Supine with leg elevation (Trendelenburg)" if vitals.get("syncope_detected") else "Comfortable semi-Fowler position",
            "safe_medication_order": "Paracetamol 500mg PO Q6H PRN" if pharm_assess.urgency_tier == "RED" else "Standard protocol per clinical guideline",
            "strictly_contraindicated": "Ibuprofen, Naproxen, Aspirin, and all NSAID derivatives",
            "monitoring_frequency": "Continuous 12-Lead & SpO2" if max_urgency == "RED" else "Every 4 Hours",
            "action_items": list(dict.fromkeys(all_recs))[:5],
            "attending_consensus": "UNANIMOUS_APPROVAL",
        }

        consensus_dx = (
            "Acute Vasovagal Syncope with Hyperpyrexia & NSAID Allergy Contraindication"
            if vitals.get("syncope_detected") and pharm_assess.urgency_tier == "RED"
            else "Acute Febrile Illness with Medication Allergy Safeguard"
            if pharm_assess.urgency_tier == "RED"
            else "Physiological Homeostasis / Ambulatory Baseline"
        )

        return ClinicalBoardConsensus(
            case_summary=f"{patient_name} evaluated by 3-Specialist Medical Board. Overall status: {max_urgency}.",
            triage_tier=max_urgency,
            primary_consensus_diagnosis=consensus_dx,
            specialist_assessments=specialist_list,
            debate_transcript=debate_transcript,
            unified_care_plan=care_plan,
            escalation_required=max_urgency == "RED",
            generated_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
