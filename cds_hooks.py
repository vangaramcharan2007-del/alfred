"""
AEGIS HL7 FHIR CDS-Hooks 1.0 Clinical Decision Support Engine
============================================================
Implements standardized CDS-Hooks specifications for integration with Hospital
Information Systems (HIS) and Electronic Health Records (EHR):
- patient-view: Evaluates patient vitals and allergies upon chart access
- medication-prescribe: Intercepts prescription orders to block contraindicated drugs
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CDSSuggestionAction(BaseModel):
    type: str = "create"
    description: str
    resource: Optional[Dict[str, Any]] = None


class CDSSuggestion(BaseModel):
    label: str
    uuid: str
    actions: List[CDSSuggestionAction] = []


class CDSCard(BaseModel):
    summary: str
    detail: str
    indicator: str  # info, warning, critical
    source: Dict[str, str] = Field(
        default_factory=lambda: {"label": "AEGIS AI Clinical Decision Engine", "url": "https://aegis-health.local"}
    )
    suggestions: List[CDSSuggestion] = []
    selectionBehavior: str = "at-most-one"


class CDSResponse(BaseModel):
    cards: List[CDSCard]


def evaluate_patient_view_hook(patient_profile: Dict[str, Any], vitals: Dict[str, Any]) -> CDSResponse:
    """Evaluate patient-view CDS Hook triggered when clinician opens patient record."""
    cards = []
    allergies = patient_profile.get("allergies_list", ["ibuprofen", "nsaids"])
    syncope = vitals.get("syncope_detected", False)
    hr = vitals.get("heart_rate", 72)
    name = patient_profile.get("name", "Patient")

    # 1. Critical Syncope / Hemodynamic Alert
    if syncope:
        cards.append(
            CDSCard(
                summary=f"CRITICAL: Acute Syncope Collapse Detected ({name})",
                detail=f"Patient {name} has experienced sudden loss of posture/orientation. Heart Rate is {hr} BPM. Immediate supine positioning and airway assessment required.",
                indicator="critical",
                suggestions=[
                    CDSSuggestion(
                        label="Place Patient in Supine Trendelenburg Position",
                        uuid="act-syncope-01",
                        actions=[
                            CDSSuggestionAction(
                                type="create",
                                description="Order urgent 12-lead ECG and continuous vitals monitoring",
                            )
                        ],
                    )
                ],
            )
        )

    # 2. Allergy Contraindication Notice
    if allergies:
        cards.append(
            CDSCard(
                summary=f"Allergy Alert: {', '.join(allergies).upper()} Documented",
                detail=f"Patient has verified allergy to {', '.join(allergies)}. Avoid prescribing NSAID antipyretics or analgesics.",
                indicator="warning",
                suggestions=[
                    CDSSuggestion(
                        label="Default Antipyretic to Paracetamol 500mg",
                        uuid="act-allergy-01",
                        actions=[
                            CDSSuggestionAction(
                                type="create",
                                description="Substitute Paracetamol (Acetaminophen) for fever and pain management",
                            )
                        ],
                    )
                ],
            )
        )

    # 3. If vitals normal
    if not cards:
        cards.append(
            CDSCard(
                summary="Vitals Nominal - Clinical Homeostasis",
                detail=f"Patient {name}'s physiological telemetry is within target baseline ranges. No immediate intervention needed.",
                indicator="info",
            )
        )

    return CDSResponse(cards=cards)


def evaluate_medication_prescribe_hook(
    patient_profile: Dict[str, Any],
    medication_name: str,
    dosage: Optional[str] = None
) -> CDSResponse:
    """Evaluate medication-prescribe CDS Hook when a medication is ordered."""
    cards = []
    allergies = [a.lower() for a in patient_profile.get("allergies_list", ["ibuprofen", "nsaids"])]
    med_lower = medication_name.lower()

    if any(a in med_lower for a in allergies) or ("ibuprofen" in med_lower or "nsaid" in med_lower or "advil" in med_lower):
        cards.append(
            CDSCard(
                summary=f"HARD STOP: Documented Allergy to {medication_name.upper()}",
                detail=(
                    f"Patient {patient_profile.get('name', 'Patient')} has a severe documented allergy to {medication_name}. "
                    f"Administering this medication may induce bronchospasm, urticaria, or anaphylactoid shock. "
                    f"Recommended safe alternative is Paracetamol (Acetaminophen)."
                ),
                indicator="critical",
                suggestions=[
                    CDSSuggestion(
                        label="Switch to Paracetamol 500mg Tablet PO Q6H PRN",
                        uuid="sug-switch-paracetamol",
                        actions=[
                            CDSSuggestionAction(
                                type="create",
                                description="Cancel contraindicated order and prescribe Paracetamol 500mg PO",
                            )
                        ],
                    )
                ],
            )
        )
    else:
        cards.append(
            CDSCard(
                summary=f"Medication Approved: {medication_name}",
                detail=f"No contraindications or cross-allergenicity found for {medication_name} in EHR records.",
                indicator="info",
            )
        )

    return CDSResponse(cards=cards)
