"""
Triage Engine — Symptom to specialty classification with urgency scoring.

Maps patient symptoms to appropriate medical specialties and urgency levels.
Uses a combination of keyword matching and medical knowledge rules.
"""

from typing import Dict, List, Tuple
import re

# Symptom to specialty mapping with weights
SYMPTOM_SPECIALTY_MAP: Dict[str, Dict[str, float]] = {
    # Cardiac symptoms
    "chest pain": {"cardiology": 0.9, "emergency": 0.8, "surgery": 0.3},
    "heart attack": {"cardiology": 0.95, "emergency": 0.95},
    "palpitations": {"cardiology": 0.7, "emergency": 0.4},
    "shortness of breath": {"cardiology": 0.6, "emergency": 0.7, "pulmonology": 0.5},
    
    # Orthopedic symptoms
    "broken bone": {"orthopedics": 0.95, "trauma": 0.8, "surgery": 0.6},
    "fracture": {"orthopedics": 0.95, "trauma": 0.8, "surgery": 0.6},
    "joint pain": {"orthopedics": 0.8, "rheumatology": 0.6},
    "back pain": {"orthopedics": 0.7, "neurology": 0.4},
    "sprain": {"orthopedics": 0.7, "emergency": 0.3},
    
    # Eye symptoms
    "eye pain": {"ophthalmology": 0.9, "emergency": 0.4},
    "vision loss": {"ophthalmology": 0.9, "emergency": 0.7},
    "red eye": {"ophthalmology": 0.8},
    "cataract": {"ophthalmology": 0.95},
    
    # Dental symptoms
    "toothache": {"dental": 0.95},
    "dental pain": {"dental": 0.95},
    "gum disease": {"dental": 0.9},
    
    # Maternity symptoms
    "pregnancy": {"maternity": 0.95},
    "labor": {"maternity": 0.95, "surgery": 0.3},
    "contractions": {"maternity": 0.9},
    "morning sickness": {"maternity": 0.7},
    
    # Pediatric symptoms
    "child fever": {"pediatrics": 0.9, "emergency": 0.4},
    "child cough": {"pediatrics": 0.8},
    "child vomiting": {"pediatrics": 0.7, "emergency": 0.5},
    
    # Oncology symptoms
    "lump": {"oncology": 0.6, "surgery": 0.5},
    "unexplained weight loss": {"oncology": 0.5, "endocrinology": 0.4},
    "chemotherapy": {"oncology": 0.95},
    "radiation therapy": {"oncology": 0.95},
    
    # Renal symptoms
    "kidney pain": {"dialysis": 0.7, "nephrology": 0.8, "emergency": 0.5},
    "dialysis": {"dialysis": 0.95},
    "urinary problems": {"nephrology": 0.6, "urology": 0.7},
    
    # Emergency symptoms
    "severe bleeding": {"emergency": 0.95, "surgery": 0.7},
    "unconscious": {"emergency": 0.95, "neurology": 0.6},
    "seizure": {"emergency": 0.8, "neurology": 0.7},
    "stroke": {"emergency": 0.95, "neurology": 0.9},
    
    # General symptoms
    "fever": {"general": 0.6, "infectious": 0.5},
    "headache": {"neurology": 0.5, "general": 0.4},
    "abdominal pain": {"gastroenterology": 0.7, "surgery": 0.4, "emergency": 0.5},
    "diarrhea": {"gastroenterology": 0.7, "infectious": 0.5},
    "vomiting": {"gastroenterology": 0.6, "emergency": 0.4},
    
    # Respiratory symptoms
    "cough": {"pulmonology": 0.7, "infectious": 0.4},
    "asthma": {"pulmonology": 0.9},
    "breathing difficulty": {"pulmonology": 0.7, "emergency": 0.6},
    
    # Neurological symptoms
    "numbness": {"neurology": 0.7},
    "tingling": {"neurology": 0.6},
    "memory loss": {"neurology": 0.6, "psychiatry": 0.4},
    "confusion": {"neurology": 0.7, "emergency": 0.6},
    
    # Skin symptoms
    "rash": {"dermatology": 0.7, "allergy": 0.5},
    "skin infection": {"dermatology": 0.7, "infectious": 0.5},
    "burn": {"emergency": 0.8, "surgery": 0.6, "dermatology": 0.3},
}

# Urgency levels with criteria
URGENCY_LEVELS = {
    "EMERGENT": {
        "description": "Immediate life-threatening condition",
        "timeframe": "Immediate (0-15 minutes)",
        "criteria": [
            "chest pain", "heart attack", "stroke", "severe bleeding",
            "unconscious", "seizure", "breathing difficulty"
        ],
        "score": 5
    },
    "URGENT": {
        "description": "Serious condition requiring prompt attention",
        "timeframe": "Within 1 hour",
        "criteria": [
            "broken bone", "fracture", "severe pain", "high fever",
            "abdominal pain", "vomiting", "diarrhea"
        ],
        "score": 4
    },
    "SEMI_URGENT": {
        "description": "Condition needing medical attention within hours",
        "timeframe": "Within 4-6 hours",
        "criteria": [
            "joint pain", "back pain", "sprain", "eye pain",
            "dental pain", "rash", "infection"
        ],
        "score": 3
    },
    "NON_URGENT": {
        "description": "Non-urgent condition, can wait for appointment",
        "timeframe": "Within 24-48 hours",
        "criteria": [
            "headache", "mild fever", "cough", "cold",
            "follow-up", "check-up"
        ],
        "score": 2
    },
    "ROUTINE": {
        "description": "Routine care, preventive services",
        "timeframe": "Within 1 week",
        "criteria": [
            "pregnancy", "preventive", "screening", "vaccination"
        ],
        "score": 1
    }
}

# Red flags requiring immediate emergency care
RED_FLAGS = [
    "chest pain", "heart attack", "stroke", "severe bleeding",
    "unconscious", "seizure", "breathing difficulty", "anaphylaxis",
    "poisoning", "severe burn", "head injury", "spine injury"
]


def extract_symptoms(text: str) -> List[str]:
    """Extract symptoms from free text with Hindi/Hinglish support."""
    text_lower = text.lower()
    
    # Map common Hindi/Hinglish keywords to English terms
    hindi_mappings = {
        # Cardiology
        "seene me dard": "chest pain",
        "seene mai dard": "chest pain",
        "chhati me dard": "chest pain",
        "dil me dard": "chest pain",
        "dhadkan": "palpitations",
        "saans phulna": "shortness of breath",
        "saans lene me": "shortness of breath",
        
        # Orthopedics
        "haddi": "broken bone",
        "toot": "broken bone",
        "tut": "broken bone",
        "kamar dard": "back pain",
        "kamar me dard": "back pain",
        "jodon me dard": "joint pain",
        "ghutne me dard": "joint pain",
        
        # Eye
        "aankh": "eye pain",
        "dhundhla": "vision loss",
        "motiyabind": "cataract",
        
        # Dental
        "daant": "toothache",
        "teeth": "toothache",
        "masude": "gum disease",
        
        # Maternity
        "pregnancy": "pregnancy",
        "delivery": "labor",
        "bachha hone": "labor",
        
        # Pediatrics
        "bachhe": "child fever",
        "bacche": "child fever",
        
        # Oncology
        "cancer": "chemotherapy",
        "ganth": "lump",
        "gaanth": "lump",
        
        # Renal
        "kidney": "kidney pain",
        "peshab": "urinary problems",
        
        # Emergency
        "khoon beh raha": "severe bleeding",
        "behos": "unconscious",
        "daura": "seizure",
        
        # General
        "bukhar": "fever",
        "sir dard": "headache",
        "pet me dard": "abdominal pain",
        "pet dard": "abdominal pain",
        "ulti": "vomiting",
        "khansi": "cough",
    }
    
    for hi, eng in hindi_mappings.items():
        if hi in text_lower:
            text_lower += f" {eng}"

    found_symptoms = []
    
    # Check for multi-word symptoms first
    for symptom in sorted(SYMPTOM_SPECIALTY_MAP.keys(), key=len, reverse=True):
        if symptom in text_lower:
            found_symptoms.append(symptom)
    
    # Also check for common variations and synonyms
    synonyms = {
        "heart": ["cardiac", "heart"],
        "bone": ["fracture", "broken"],
        "eye": ["visual", "vision"],
        "tooth": ["dental", "teeth"],
        "stomach": ["abdominal", "belly"],
        "breathing": ["respiratory", "dyspnea"],
    }
    
    for base, syns in synonyms.items():
        for syn in syns:
            if syn in text_lower and base not in found_symptoms:
                found_symptoms.append(base)
    
    return list(set(found_symptoms))


def classify_symptoms(symptoms: List[str]) -> Dict[str, float]:
    """Classify symptoms to specialties with confidence scores."""
    specialty_scores: Dict[str, float] = {}
    
    for symptom in symptoms:
        if symptom in SYMPTOM_SPECIALTY_MAP:
            for specialty, weight in SYMPTOM_SPECIALTY_MAP[symptom].items():
                if specialty not in specialty_scores:
                    specialty_scores[specialty] = 0.0
                specialty_scores[specialty] = max(specialty_scores[specialty], weight)
    
    # Normalize scores to 0-1 range
    if specialty_scores:
        max_score = max(specialty_scores.values())
        if max_score > 0:
            specialty_scores = {k: v / max_score for k, v in specialty_scores.items()}
    
    return specialty_scores


def assess_urgency(symptoms: List[str], text: str = "") -> Tuple[str, int, str]:
    """Assess urgency level based on symptoms."""
    text_lower = text.lower() if text else ""
    
    # Check for red flags first
    for flag in RED_FLAGS:
        if flag in text_lower or flag in symptoms:
            return "EMERGENT", URGENCY_LEVELS["EMERGENT"]["score"], URGENCY_LEVELS["EMERGENT"]["description"]
    
    # Check urgency levels in order
    for level_name, level_info in URGENCY_LEVELS.items():
        for criterion in level_info["criteria"]:
            if criterion in text_lower or criterion in symptoms:
                return level_name, level_info["score"], level_info["description"]
    
    # Default to non-urgent if no matches
    return "NON_URGENT", URGENCY_LEVELS["NON_URGENT"]["score"], URGENCY_LEVELS["NON_URGENT"]["description"]


def triage(text: str, patient_age: int = None, patient_gender: str = None) -> dict:
    """
    Perform triage on patient symptoms.
    
    Args:
        text: Patient description of symptoms
        patient_age: Optional patient age
        patient_gender: Optional patient gender
    
    Returns:
        Triage result with specialties, urgency, and recommendations
    """
    # Extract symptoms from text
    symptoms = extract_symptoms(text)
    
    # Classify to specialties
    specialty_scores = classify_symptoms(symptoms)
    
    # Assess urgency
    urgency_level, urgency_score, urgency_description = assess_urgency(symptoms, text)
    
    # Sort specialties by score
    sorted_specialties = sorted(specialty_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Generate recommendations
    recommendations = []
    if urgency_level == "EMERGENT":
        recommendations.append("Go to emergency department immediately")
        recommendations.append("Call emergency services if needed")
    elif urgency_level == "URGENT":
        recommendations.append("Seek medical attention within 1 hour")
        recommendations.append("Consider visiting emergency department")
    elif urgency_level == "SEMI_URGENT":
        recommendations.append("Schedule appointment within 4-6 hours")
        recommendations.append("Visit urgent care if available")
    else:
        recommendations.append("Schedule appointment with primary care")
        recommendations.append("Consider telemedicine consultation")
    
    # Add specialty-specific recommendations
    if sorted_specialties:
        top_specialty = sorted_specialties[0][0]
        if top_specialty == "cardiology":
            recommendations.append("Cardiology consultation recommended")
        elif top_specialty == "orthopedics":
            recommendations.append("X-ray or imaging may be needed")
        elif top_specialty == "oncology":
            recommendations.append("Oncology consultation recommended")
        elif top_specialty == "maternity":
            recommendations.append("Obstetrics/gynecology consultation recommended")
    
    # Age-specific adjustments
    if patient_age is not None:
        if patient_age < 5:
            recommendations.append("Pediatric specialist recommended for young children")
        elif patient_age > 65:
            recommendations.append("Consider geriatric assessment")
    
    return {
        "symptoms": symptoms,
        "specialties": [
            {"name": spec, "confidence": round(score, 2)}
            for spec, score in sorted_specialties[:5]  # Top 5 specialties
        ],
        "urgency": {
            "level": urgency_level,
            "score": urgency_score,
            "description": urgency_description,
        },
        "recommendations": recommendations,
        "red_flags": [flag for flag in RED_FLAGS if flag in text.lower()],
        "metadata": {
            "input_text": text,
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "symptoms_found": len(symptoms),
        }
    }


def get_specialty_capabilities() -> Dict[str, List[str]]:
    """Map specialties to facility capabilities for hospital matching."""
    return {
        "cardiology": ["cardiology", "emergency", "surgery"],
        "orthopedics": ["orthopedics", "surgery", "radiology"],
        "ophthalmology": ["ophthalmology", "surgery"],
        "dental": ["dental"],
        "maternity": ["maternity", "nicu", "surgery"],
        "pediatrics": ["pediatrics", "emergency"],
        "oncology": ["oncology", "surgery", "radiology", "laboratory"],
        "dialysis": ["dialysis", "laboratory"],
        "emergency": ["emergency", "surgery", "icu"],
        "neurology": ["neurology", "radiology", "icu"],
        "pulmonology": ["pulmonology", "radiology", "laboratory"],
        "gastroenterology": ["gastroenterology", "laboratory", "surgery"],
        "dermatology": ["dermatology"],
        "general": ["pharmacy", "laboratory"],
        "infectious": ["laboratory", "pharmacy"],
        "surgery": ["surgery", "icu"],
        "radiology": ["radiology"],
        "laboratory": ["laboratory"],
        "pharmacy": ["pharmacy"],
        "icu": ["icu", "emergency"],
        "nicu": ["nicu"],
    }