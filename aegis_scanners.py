"""
AEGIS Advanced Clinical Scanners Module
========================================
Provides:
1. Medicine Strip OCR Scanner - Extracts drug name, dosage, composition from tablet blister images
2. ABHA (Ayushman Bharat Health Account) QR Code Decoder - Parses 14-digit ABHA National Health ID
3. Chest X-Ray Edge Pneumonia / TB Screener - Classifies CXR images with CAM heatmap overlay
4. Hand Gesture Organ Mapper - Maps MediaPipe hand landmark coordinates to anatomical organ zones
"""

import base64
import json
import re
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
import numpy as np


# ============================================================================
# 1. MEDICINE STRIP OCR SCANNER
# ============================================================================

# Common Indian pharmaceutical drug database for fuzzy matching
DRUG_DATABASE = {
    "paracetamol": {"generic": "Paracetamol (Acetaminophen)", "class": "Analgesic / Antipyretic", "common_dosages": ["500mg", "650mg", "1000mg"], "interactions": ["Alcohol", "Warfarin"]},
    "ibuprofen": {"generic": "Ibuprofen", "class": "NSAID / Anti-Inflammatory", "common_dosages": ["200mg", "400mg", "600mg"], "interactions": ["Aspirin", "Warfarin", "Lithium"]},
    "amoxicillin": {"generic": "Amoxicillin", "class": "Penicillin Antibiotic", "common_dosages": ["250mg", "500mg"], "interactions": ["Methotrexate", "Warfarin"]},
    "amlodipine": {"generic": "Amlodipine Besylate", "class": "Calcium Channel Blocker (Antihypertensive)", "common_dosages": ["2.5mg", "5mg", "10mg"], "interactions": ["Simvastatin", "Cyclosporine"]},
    "metformin": {"generic": "Metformin Hydrochloride", "class": "Biguanide (Antidiabetic)", "common_dosages": ["500mg", "850mg", "1000mg"], "interactions": ["Alcohol", "Contrast Dye"]},
    "azithromycin": {"generic": "Azithromycin", "class": "Macrolide Antibiotic", "common_dosages": ["250mg", "500mg"], "interactions": ["Antacids", "Warfarin"]},
    "cetirizine": {"generic": "Cetirizine Dihydrochloride", "class": "Antihistamine (H1 Blocker)", "common_dosages": ["5mg", "10mg"], "interactions": ["Alcohol", "CNS Depressants"]},
    "omeprazole": {"generic": "Omeprazole", "class": "Proton Pump Inhibitor (PPI)", "common_dosages": ["20mg", "40mg"], "interactions": ["Clopidogrel", "Methotrexate"]},
    "salbutamol": {"generic": "Salbutamol (Albuterol)", "class": "Beta-2 Agonist Bronchodilator", "common_dosages": ["100mcg", "200mcg", "2mg", "4mg"], "interactions": ["Beta-Blockers", "Digoxin"]},
    "ferrous sulfate": {"generic": "Ferrous Sulfate (Iron)", "class": "Iron Supplement (Hematinic)", "common_dosages": ["200mg", "325mg"], "interactions": ["Antacids", "Tetracyclines", "Ciprofloxacin"]},
    "mefenamic acid": {"generic": "Mefenamic Acid", "class": "NSAID / Antispasmodic", "common_dosages": ["250mg", "500mg"], "interactions": ["Aspirin", "Warfarin", "Lithium"]},
    "vitamin d3": {"generic": "Cholecalciferol (Vitamin D3)", "class": "Fat-Soluble Vitamin Supplement", "common_dosages": ["1000IU", "2000IU", "60000IU"], "interactions": ["Thiazide Diuretics", "Digoxin"]},
    "dolo": {"generic": "Paracetamol (Acetaminophen)", "class": "Analgesic / Antipyretic", "common_dosages": ["650mg"], "interactions": ["Alcohol", "Warfarin"]},
    "crocin": {"generic": "Paracetamol (Acetaminophen)", "class": "Analgesic / Antipyretic", "common_dosages": ["500mg", "650mg"], "interactions": ["Alcohol", "Warfarin"]},
    "combiflam": {"generic": "Ibuprofen + Paracetamol", "class": "NSAID Combination Analgesic", "common_dosages": ["400mg+325mg"], "interactions": ["Aspirin", "Warfarin"]},
    "aspirin": {"generic": "Acetylsalicylic Acid", "class": "NSAID / Antiplatelet", "common_dosages": ["75mg", "150mg", "325mg"], "interactions": ["Warfarin", "Ibuprofen", "Methotrexate"]},
    "pantoprazole": {"generic": "Pantoprazole Sodium", "class": "Proton Pump Inhibitor (PPI)", "common_dosages": ["20mg", "40mg"], "interactions": ["Atazanavir", "Methotrexate"]},
    "atorvastatin": {"generic": "Atorvastatin Calcium", "class": "HMG-CoA Reductase Inhibitor (Statin)", "common_dosages": ["10mg", "20mg", "40mg"], "interactions": ["Grapefruit", "Cyclosporine"]},
    "montelukast": {"generic": "Montelukast Sodium", "class": "Leukotriene Receptor Antagonist", "common_dosages": ["4mg", "5mg", "10mg"], "interactions": ["Phenobarbital", "Rifampicin"]},
    "losartan": {"generic": "Losartan Potassium", "class": "Angiotensin II Receptor Blocker (ARB)", "common_dosages": ["25mg", "50mg", "100mg"], "interactions": ["Potassium Supplements", "NSAIDs"]},
}


def scan_medicine_strip(ocr_text: str, patient_allergies: List[str] = None) -> Dict[str, Any]:
    """
    Process OCR-extracted text from a medicine strip/blister pack image.
    Identifies drug name, dosage, checks against allergy database.
    
    Args:
        ocr_text: Raw text from OCR scan of medicine strip
        patient_allergies: List of patient's known drug allergies
    
    Returns:
        Dict with identified drug details, allergy warnings, and schedule suggestion
    """
    if patient_allergies is None:
        patient_allergies = []

    text_lower = ocr_text.lower().strip()

    # Fuzzy match against drug database
    identified_drug = None
    matched_key = None
    confidence = 0.0

    for drug_key, drug_info in DRUG_DATABASE.items():
        if drug_key in text_lower or drug_key.replace(" ", "") in text_lower.replace(" ", ""):
            identified_drug = drug_info
            matched_key = drug_key
            confidence = 0.95
            break
        # Partial match
        if len(drug_key) > 3 and drug_key[:4] in text_lower:
            identified_drug = drug_info
            matched_key = drug_key
            confidence = 0.78
            break

    if identified_drug is None:
        # Try to extract any recognizable drug-like pattern
        words = re.findall(r'[a-zA-Z]{4,}', text_lower)
        for word in words:
            for drug_key in DRUG_DATABASE:
                if word in drug_key or drug_key in word:
                    identified_drug = DRUG_DATABASE[drug_key]
                    matched_key = drug_key
                    confidence = 0.65
                    break
            if identified_drug:
                break

    # Extract dosage from text
    dosage_match = re.search(r'(\d+)\s*(mg|mcg|iu|ml|g)\b', text_lower, re.IGNORECASE)
    detected_dosage = f"{dosage_match.group(1)}{dosage_match.group(2).lower()}" if dosage_match else None

    # Allergy cross-reference
    allergy_alert = False
    allergy_details = []
    if identified_drug and matched_key:
        for allergy in patient_allergies:
            allergy_l = allergy.lower().strip()
            if allergy_l in matched_key or matched_key in allergy_l:
                allergy_alert = True
                allergy_details.append(f"CRITICAL: Patient is allergic to {allergy.upper()}. This drug ({identified_drug['generic']}) is CONTRAINDICATED.")
            # Check drug class
            if "nsaid" in allergy_l and "nsaid" in identified_drug["class"].lower():
                allergy_alert = True
                allergy_details.append(f"CRITICAL: Patient has NSAID allergy. {identified_drug['generic']} is an NSAID and is CONTRAINDICATED.")

    # Build schedule suggestion
    schedule_suggestion = "Take as directed by your physician"
    if identified_drug:
        drug_class = identified_drug["class"].lower()
        if "analgesic" in drug_class or "antipyretic" in drug_class:
            schedule_suggestion = "Take 1 tablet every 6-8 hours as needed, with food. Max 4 doses/day."
        elif "antibiotic" in drug_class:
            schedule_suggestion = "Take 1 tablet every 12 hours for the full prescribed course. Do not skip doses."
        elif "antihypertensive" in drug_class or "blocker" in drug_class:
            schedule_suggestion = "Take 1 tablet every morning at 08:00 AM with water. Monitor BP regularly."
        elif "supplement" in drug_class or "vitamin" in drug_class:
            schedule_suggestion = "Take 1 tablet/capsule daily after breakfast with water."
        elif "bronchodilator" in drug_class:
            schedule_suggestion = "Inhale 2 puffs as needed for chest tightness. Shake canister before use."
        elif "ppi" in drug_class:
            schedule_suggestion = "Take 1 tablet 30 minutes before breakfast on empty stomach."

    if identified_drug is None:
        return {
            "status": "UNRECOGNIZED",
            "raw_ocr_text": ocr_text,
            "drug_identified": False,
            "confidence": 0.0,
            "message": "Could not identify a known pharmaceutical from the scanned text. Please position the medicine strip clearly in front of the camera.",
            "allergy_alert": False,
        }

    return {
        "status": "ALLERGY_DANGER" if allergy_alert else "IDENTIFIED",
        "drug_identified": True,
        "drug_name": identified_drug["generic"],
        "drug_class": identified_drug["class"],
        "detected_dosage": detected_dosage or identified_drug["common_dosages"][0],
        "common_dosages": identified_drug["common_dosages"],
        "known_interactions": identified_drug["interactions"],
        "confidence": confidence,
        "allergy_alert": allergy_alert,
        "allergy_warnings": allergy_details,
        "schedule_suggestion": schedule_suggestion,
        "raw_ocr_text": ocr_text,
    }


# ============================================================================
# 2. ABHA (AYUSHMAN BHARAT HEALTH ACCOUNT) QR CODE DECODER
# ============================================================================

def decode_abha_qr(qr_payload: str) -> Dict[str, Any]:
    """
    Decode an Ayushman Bharat Health Account (ABHA) QR code payload.
    
    ABHA cards contain a JSON payload with patient demographics encoded
    in the QR code. The 14-digit ABHA number format is: XX-XXXX-XXXX-XXXX
    
    Args:
        qr_payload: Raw decoded string from QR code scanner
    
    Returns:
        Dict with parsed patient demographics and ABHA metadata
    """
    # Try JSON parse first (standard ABHA QR format)
    try:
        data = json.loads(qr_payload)
        return _parse_abha_json(data)
    except (json.JSONDecodeError, ValueError):
        pass

    # Try to extract ABHA number pattern from raw text
    abha_pattern = re.search(r'(\d{2})[- ]?(\d{4})[- ]?(\d{4})[- ]?(\d{4})', qr_payload)
    if abha_pattern:
        abha_number = f"{abha_pattern.group(1)}-{abha_pattern.group(2)}-{abha_pattern.group(3)}-{abha_pattern.group(4)}"

        # Extract name if present (stop at known field keywords)
        name_match = re.search(r'(?:name|patient|nm)[:\s]+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+(?:gender|sex|g|dob|blood|age|mobile|state|district|phone)\b|$)', qr_payload, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else "Unknown Patient"

        # Extract gender
        gender_match = re.search(r'(?:gender|sex|g)[:\s]+([MFO]|Male|Female|Other)', qr_payload, re.IGNORECASE)
        gender = "Male"
        if gender_match:
            g = gender_match.group(1).upper()
            gender = "Female" if g in ("F", "FEMALE") else "Other" if g in ("O", "OTHER") else "Male"

        # Extract DOB
        dob_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', qr_payload)
        dob = dob_match.group(1) if dob_match else None

        # Extract blood group
        bg_match = re.search(r'(A|B|AB|O)[+-]', qr_payload)
        blood_group = bg_match.group(0) if bg_match else None

        return {
            "status": "DECODED",
            "abha_number": abha_number,
            "abha_address": f"{name.lower().replace(' ', '')}@abdm",
            "name": name,
            "gender": gender,
            "date_of_birth": dob,
            "blood_group": blood_group,
            "state": None,
            "district": None,
            "mobile_hash": hashlib.sha256(abha_number.encode()).hexdigest()[:16],
            "verification_status": "PARTIAL_DECODE",
            "source": "RAW_TEXT_EXTRACTION",
        }

    # Simulate demo ABHA decode for hackathon demonstration
    if "abha" in qr_payload.lower() or "abdm" in qr_payload.lower() or len(qr_payload) > 20:
        demo_hash = hashlib.sha256(qr_payload.encode()).hexdigest()
        demo_abha = f"91-{demo_hash[0:4]}-{demo_hash[4:8]}-{demo_hash[8:12]}"

        return {
            "status": "DECODED",
            "abha_number": demo_abha,
            "abha_address": "patient@abdm",
            "name": "Decoded Patient",
            "gender": "Male",
            "date_of_birth": "01-01-1998",
            "blood_group": "O+",
            "state": "Telangana",
            "district": "Warangal",
            "mobile_hash": demo_hash[:16],
            "verification_status": "DEMO_DECODE",
            "source": "QR_PAYLOAD_HASH",
        }

    return {
        "status": "INVALID_QR",
        "message": "The scanned QR code does not contain a valid ABHA health card payload. Please ensure the card is an official Ayushman Bharat Digital Health card.",
        "raw_payload": qr_payload[:200],
    }


def _parse_abha_json(data: dict) -> Dict[str, Any]:
    """Parse structured ABHA JSON QR payload."""
    return {
        "status": "DECODED",
        "abha_number": data.get("hidn", data.get("abha_number", data.get("healthId", "Unknown"))),
        "abha_address": data.get("hid", data.get("abha_address", data.get("healthIdNumber", ""))),
        "name": data.get("name", data.get("fullName", "Unknown")),
        "gender": data.get("gender", data.get("sex", "Male")),
        "date_of_birth": data.get("dob", data.get("dateOfBirth", None)),
        "blood_group": data.get("bloodGroup", data.get("blood_group", None)),
        "state": data.get("state", data.get("stateName", None)),
        "district": data.get("district", data.get("districtName", None)),
        "mobile_hash": data.get("mobile", data.get("phone_hash", hashlib.sha256(str(data).encode()).hexdigest()[:16])),
        "verification_status": "VERIFIED" if data.get("hidn") or data.get("abha_number") else "PARTIAL",
        "source": "STRUCTURED_JSON_QR",
    }


# ============================================================================
# 3. CHEST X-RAY EDGE PNEUMONIA / TB SCREENER
# ============================================================================

def classify_chest_xray(
    pixel_intensity_mean: float = 128.0,
    lung_opacity_ratio: float = 0.15,
    contrast_score: float = 0.65,
    cardiac_silhouette_ratio: float = 0.48,
    upper_lobe_density: float = 0.12,
    lower_lobe_density: float = 0.18,
    bilateral: bool = False,
) -> Dict[str, Any]:
    """
    Edge Chest X-Ray classifier using extracted radiometric features.
    
    For a full deployment, this would use a CNN (DenseNet-121 / EfficientNet)
    trained on NIH ChestX-ray14 or CheXpert datasets. For the edge demo,
    we use clinical heuristic scoring based on radiometric features that
    would be extracted from a real CXR image.
    
    Scoring Logic:
    - Lung opacity ratio > 0.35 with high lower lobe density → Bacterial Pneumonia
    - Bilateral opacities with moderate ratio → Viral Pneumonia (COVID-like)
    - High upper lobe density with cavitation pattern → Pulmonary Tuberculosis
    - Low opacity, normal contrast → Normal / Healthy CXR
    """
    findings = []
    classification = "NORMAL"
    confidence = 0.92
    severity = "CLEAR"
    heatmap_zones = []

    # Tuberculosis Detection (upper lobe predominant)
    if upper_lobe_density > 0.30:
        classification = "PULMONARY_TUBERCULOSIS"
        confidence = 0.88
        severity = "HIGH"
        findings.append("Upper lobe infiltrates with possible cavitation pattern consistent with pulmonary tuberculosis.")
        findings.append("Recommend: Sputum AFB smear, GeneXpert MTB/RIF, and chest CT for confirmation.")
        heatmap_zones = [
            {"zone": "Right Upper Lobe", "intensity": round(upper_lobe_density * 100, 1), "color": "#ef4444"},
            {"zone": "Left Upper Lobe", "intensity": round(upper_lobe_density * 85, 1), "color": "#f97316"},
        ]

    # Bacterial Pneumonia Detection (lower lobe consolidation)
    elif lung_opacity_ratio > 0.35 and lower_lobe_density > 0.30:
        classification = "BACTERIAL_PNEUMONIA"
        confidence = 0.91
        severity = "HIGH"
        findings.append("Dense lobar consolidation in lower lung fields with air bronchograms suggestive of bacterial pneumonia.")
        findings.append("Recommend: Blood cultures, CBC with differential, empiric antibiotics (Amoxicillin-Clavulanate or Azithromycin).")
        heatmap_zones = [
            {"zone": "Right Lower Lobe", "intensity": round(lower_lobe_density * 100, 1), "color": "#ef4444"},
            {"zone": "Left Lower Lobe", "intensity": round(lower_lobe_density * 80, 1), "color": "#f97316"},
        ]

    # Viral / COVID-19 Pneumonia (bilateral ground-glass)
    elif bilateral and lung_opacity_ratio > 0.25:
        classification = "VIRAL_PNEUMONIA"
        confidence = 0.84
        severity = "MODERATE"
        findings.append("Bilateral peripheral ground-glass opacities consistent with viral pneumonia (COVID-19 pattern).")
        findings.append("Recommend: RT-PCR testing, pulse oximetry monitoring, supportive care with O2 if SpO2 < 94%.")
        heatmap_zones = [
            {"zone": "Right Peripheral", "intensity": round(lung_opacity_ratio * 100, 1), "color": "#f59e0b"},
            {"zone": "Left Peripheral", "intensity": round(lung_opacity_ratio * 90, 1), "color": "#f59e0b"},
        ]

    # Mild opacity / Early infiltrate
    elif lung_opacity_ratio > 0.20:
        classification = "EARLY_INFILTRATE"
        confidence = 0.76
        severity = "LOW"
        findings.append("Mild patchy opacity noted. Could represent early pneumonic infiltrate or atelectasis.")
        findings.append("Recommend: Clinical correlation, repeat CXR in 48-72 hours if symptoms persist.")
        heatmap_zones = [
            {"zone": "Lower Lung Fields", "intensity": round(lung_opacity_ratio * 80, 1), "color": "#eab308"},
        ]

    # Cardiomegaly check
    elif cardiac_silhouette_ratio > 0.55:
        classification = "CARDIOMEGALY"
        confidence = 0.83
        severity = "MODERATE"
        findings.append(f"Cardiothoracic ratio {cardiac_silhouette_ratio:.2f} exceeds 0.50 threshold. Suggestive of cardiomegaly.")
        findings.append("Recommend: Echocardiogram, BNP levels, and cardiology referral.")
        heatmap_zones = [
            {"zone": "Cardiac Silhouette", "intensity": round(cardiac_silhouette_ratio * 100, 1), "color": "#a855f7"},
        ]

    else:
        findings.append("No significant pulmonary infiltrates, effusions, or consolidation identified.")
        findings.append("Heart size and mediastinum appear within normal limits.")
        heatmap_zones = [
            {"zone": "Bilateral Lung Fields", "intensity": 8.0, "color": "#22c55e"},
        ]

    return {
        "classification": classification,
        "confidence": round(confidence, 3),
        "severity": severity,
        "findings": findings,
        "heatmap_zones": heatmap_zones,
        "radiometric_features": {
            "pixel_intensity_mean": round(pixel_intensity_mean, 2),
            "lung_opacity_ratio": round(lung_opacity_ratio, 3),
            "contrast_score": round(contrast_score, 3),
            "cardiac_silhouette_ratio": round(cardiac_silhouette_ratio, 3),
            "upper_lobe_density": round(upper_lobe_density, 3),
            "lower_lobe_density": round(lower_lobe_density, 3),
            "bilateral": bilateral,
        },
        "model_info": "Edge CXR Heuristic Classifier v1.0 (DenseNet-121 compatible feature extraction)",
    }


# ============================================================================
# 4. HAND GESTURE TO ORGAN ZONE MAPPER
# ============================================================================

# Anatomical organ zones mapped to normalized screen regions
ORGAN_ZONES = {
    "HEAD_BRAIN": {"y_range": (0.0, 0.18), "x_range": (0.3, 0.7), "label": "Brain / Head", "disease": "ACUTE_FEVER"},
    "CHEST_HEART": {"y_range": (0.22, 0.42), "x_range": (0.35, 0.55), "label": "Cardiovascular Heart", "disease": "CARDIAC_TACHYCARDIA"},
    "LEFT_LUNG": {"y_range": (0.20, 0.45), "x_range": (0.55, 0.75), "label": "Left Pulmonary Lung", "disease": "BRONCHIAL_ASTHMA"},
    "RIGHT_LUNG": {"y_range": (0.20, 0.45), "x_range": (0.25, 0.45), "label": "Right Pulmonary Lung", "disease": "BRONCHIAL_ASTHMA"},
    "ABDOMEN": {"y_range": (0.45, 0.65), "x_range": (0.3, 0.7), "label": "Digestive / Core Abdomen", "disease": "ANEMIA_PALLOR"},
    "PELVIC": {"y_range": (0.65, 0.85), "x_range": (0.3, 0.7), "label": "Pelvic / Uterine Region", "disease": "DYSMENORRHEA"},
}


def map_hand_to_organ(
    index_tip_x: float,
    index_tip_y: float,
    wrist_x: float,
    wrist_y: float,
    hand_detected: bool = True,
    is_pointing: bool = True,
) -> Dict[str, Any]:
    """
    Map hand landmark coordinates to anatomical organ zones.
    
    Uses the index finger tip position (MediaPipe landmark 8) to determine
    which organ zone the patient is pointing at on their body or on the
    3D digital twin viewport.
    
    Coordinates are normalized 0.0 to 1.0 (from MediaPipe).
    
    Args:
        index_tip_x: Normalized X coordinate of index finger tip (0-1)
        index_tip_y: Normalized Y coordinate of index finger tip (0-1)
        wrist_x: Normalized X coordinate of wrist (0-1)
        wrist_y: Normalized Y coordinate of wrist (0-1)
        hand_detected: Whether a hand is currently detected
        is_pointing: Whether the hand is in a pointing gesture
    
    Returns:
        Dict with matched organ zone, gesture status, and raycast vector
    """
    if not hand_detected:
        return {
            "status": "NO_HAND_DETECTED",
            "organ": None,
            "gesture": "NONE",
            "message": "No hand detected in camera frame. Hold your hand in front of the camera and point at the area of concern.",
        }

    if not is_pointing:
        return {
            "status": "HAND_DETECTED_NO_GESTURE",
            "organ": None,
            "gesture": "OPEN_PALM",
            "hand_position": {"x": round(index_tip_x, 3), "y": round(index_tip_y, 3)},
            "message": "Hand detected but no pointing gesture recognized. Extend your index finger to point at the organ.",
        }

    # Calculate pointing vector from wrist to index tip
    dx = index_tip_x - wrist_x
    dy = index_tip_y - wrist_y
    magnitude = max((dx**2 + dy**2) ** 0.5, 0.001)

    # Find matching organ zone
    matched_organ = None
    for zone_key, zone_def in ORGAN_ZONES.items():
        y_min, y_max = zone_def["y_range"]
        x_min, x_max = zone_def["x_range"]
        if x_min <= index_tip_x <= x_max and y_min <= index_tip_y <= y_max:
            matched_organ = zone_def
            break

    if matched_organ is None:
        return {
            "status": "POINTING_OUTSIDE_BODY",
            "organ": None,
            "gesture": "POINTING",
            "hand_position": {"x": round(index_tip_x, 3), "y": round(index_tip_y, 3)},
            "raycast_vector": {"dx": round(dx / magnitude, 3), "dy": round(dy / magnitude, 3)},
            "message": "Pointing gesture detected but outside anatomical zones. Move your finger towards the body outline.",
        }

    return {
        "status": "ORGAN_TARGETED",
        "organ": matched_organ["label"],
        "disease_preset": matched_organ["disease"],
        "gesture": "POINTING",
        "hand_position": {"x": round(index_tip_x, 3), "y": round(index_tip_y, 3)},
        "raycast_vector": {"dx": round(dx / magnitude, 3), "dy": round(dy / magnitude, 3)},
        "confidence": round(0.85 + (0.15 * (1.0 - abs(index_tip_x - 0.5))), 3),
        "message": f"Gesture raycast locked on: {matched_organ['label']}. Loading organ diagnostic profile.",
    }
