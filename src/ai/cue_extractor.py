"""AI-Powered and Deterministic Fallback Memory Cue Extractor for Part 5 MVP.

Implements:
1. LLM-based extraction via Groq API (LLaMA-3.3-70B) when configured.
2. Robust deterministic rule-based fallback parser guaranteeing zero downtime.
3. Fuzzy temporal normalization (e.g., 'about 3 years back' -> ~2023) without forcing exact dates.
4. Dynamic refinement prompt suggestions for missing dimensions.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.models.mvp import MemoryCues, CueExtractionResponse
from src.config.settings import settings
from src.config.logger import logger


# Reference Anchor Year for relative temporal calculations (2026 as per project timeline)
REFERENCE_YEAR = 2026


# ==============================================================================
# DETERMINISTIC FALLBACK EXTRACTION LOGIC
# ==============================================================================

KNOWN_PEOPLE = ["rohan", "kabir", "sneha", "maya", "ananya", "priya", "parents", "sister", "cousins", "friends", "family", "colleagues"]
KNOWN_LOCATIONS = ["goa", "manali", "kerala", "jaipur", "pondicherry", "ladakh", "rishikesh", "ooty", "bangalore", "delhi", "mumbai", "beach", "cafe", "auditorium", "palace", "rooftop", "cliff", "park", "resort", "amphitheater", "mountain", "mountains", "hills", "lake", "river"]
KNOWN_ACTIVITIES = ["sunset", "ramp walk", "fashion show", "trekking", "dinner", "picnic", "birthday", "cake cutting", "diwali", "navratri", "garba", "dandiya", "party", "graduation", "gaming", "concert", "dance", "rafting", "houseboat", "marksheet", "prescription", "receipt", "ticket"]
KNOWN_OBJECTS = ["dog", "puppy", "pet", "marksheet", "transcript", "receipt", "ticket", "bill", "guitar", "cake", "diyas", "prescription", "contract", "trophy", "bike", "motorcycle", "laptop"]
KNOWN_VISUALS = [
    "black and gold", "black and gold dress", "black dress", "golden hour", "snow", "white water", "blue lake",
    "yellow wall", "stage lights", "spotlight", "neon lights", "rain", "window", "outdoors", "indoor",
    "formal", "casual", "sunglasses", "jacket", "mountains", "mountain", "dog", "dandiya sticks"
]


def extract_cues_deterministic(query_text: str) -> Tuple[MemoryCues, List[str]]:
    """Deterministic rule-based extractor using NLP heuristics, regex, and taxonomy lookups."""
    text_lower = query_text.lower()
    
    # 1. Temporal Extraction & Normalization
    approx_time = None
    normalized_year = None
    year_tolerance = 1
    season = None

    # Check for direct 4-digit year mentions (e.g., 2021, 2022, 2023, 2024)
    year_match = re.search(r"\b(201\d|202\d)\b", text_lower)
    if year_match:
        normalized_year = int(year_match.group(1))
        approx_time = f"Around {normalized_year}"
    else:
        # Relative temporal expressions (e.g., '3 years ago', '4 years back', 'three years back')
        rel_match = re.search(r"(\d+|one|two|three|four|five|six)\s+(years|year)\s+(ago|back|prior)", text_lower)
        word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
        if rel_match:
            raw_num = rel_match.group(1)
            num_years = word_to_num.get(raw_num, int(raw_num) if raw_num.isdigit() else 3)
            normalized_year = REFERENCE_YEAR - num_years
            approx_time = f"About {num_years} years ago (~{normalized_year})"
        elif "college" in text_lower or "university" in text_lower:
            normalized_year = 2022
            year_tolerance = 2
            approx_time = "College years (~2021-2023)"
        elif "recent" in text_lower or "last year" in text_lower:
            normalized_year = 2024
            approx_time = "Recent (~2024)"

    # Season detection
    for s in ["winter", "monsoon", "summer", "autumn", "spring"]:
        if s in text_lower:
            season = s.capitalize()
            break

    # 2. Companions
    companions = []
    for p in KNOWN_PEOPLE:
        if re.search(rf"\b{p}\b", text_lower):
            companions.append(p.capitalize())

    # 3. Location
    location = None
    for loc in KNOWN_LOCATIONS:
        if re.search(rf"\b{loc}\b", text_lower):
            location = loc.capitalize()
            break

    # 4. Activity
    activity = None
    for act in KNOWN_ACTIVITIES:
        if re.search(rf"\b{act}\b", text_lower):
            if act == "navratri":
                activity = "Garba / Dandiya (Navratri)"
            else:
                activity = act.title()
            break

    # 5. Objects
    objects = []
    for obj in KNOWN_OBJECTS:
        if re.search(rf"\b{obj}\b", text_lower):
            objects.append(obj.capitalize())

    # 6. Visual Attributes
    visuals = []
    for vis in KNOWN_VISUALS:
        if vis in text_lower:
            visuals.append(vis)

    # 7. Text / OCR
    ocr_tokens = []
    academic_keywords = ["marksheet", "transcript", "cgpa", "grade", "sheet", "certificate", "semester", "roll", "exam", "result", "degree", "bachelor"]
    utility_keywords = ["receipt", "bill", "electricity", "transaction", "paid", "amount", "consumer"]
    travel_keywords = ["ticket", "flight", "boarding", "indigo", "irctc", "train", "seat", "booking", "pnr"]
    medical_keywords = ["prescription", "doctor", "clinic", "rx", "medicine", "paracetamol"]

    for kw in academic_keywords + utility_keywords + travel_keywords + medical_keywords:
        if kw in text_lower:
            ocr_tokens.append(kw)
    
    sem_match = re.search(r"(?:semester|sem)\s*(\d+|vi|iv|ii)", text_lower)
    if sem_match:
        ocr_tokens.append(f"semester {sem_match.group(1)}")
    
    text_ocr = " ".join(dict.fromkeys(ocr_tokens)) if ocr_tokens else None

    # 8. Uncertainty
    uncertainty = None
    if any(h in text_lower for h in ["maybe", "probably", "not sure", "don't remember", "rough", "around", "approx"]):
        uncertainty = "User expressed uncertainty about exact details"

    cues = MemoryCues(
        approximate_time=approx_time,
        normalized_year=normalized_year,
        year_tolerance=year_tolerance,
        season=season,
        companions=companions,
        location=location,
        activity=activity,
        objects=objects,
        visual_attributes=visuals,
        text_ocr=text_ocr,
        uncertainty=uncertainty,
    )

    # Generate Refinement Suggestions based on missing dimensions
    refinements = []
    if not companions and not text_ocr:
        refinements.append("Add a person: Who was with you?")
    if not location and not text_ocr:
        refinements.append("Specify setting: Where was this taken (beach, cafe, indoor)?")
    if not visuals:
        refinements.append("Describe clothing or visual colors")
    if not season and not normalized_year:
        refinements.append("Approximate time: Season or years ago?")

    return cues, refinements[:3]


# ==============================================================================
# LLM EXTRACTION VIA GROQ
# ==============================================================================

CUE_EXTRACTION_SYSTEM_PROMPT = """You are an AI assistant specialized in human episodic memory retrieval for personal photo archives.
Your task is to parse a user's informal, fragmented memory description into structured retrieval cues without hallucinating exact dates.

Extract the following JSON fields:
1. approximate_time: string describing relative time (e.g., "around 3 years back", "college days")
2. normalized_year: integer estimated year (relative to 2026, e.g. 3 years ago = 2023) or null if unknown
3. year_tolerance: integer window (default 1)
4. season: string ("Winter", "Summer", "Monsoon", "Autumn", "Spring") or null
5. companions: list of strings (names or roles of people mentioned, e.g. ["Rohan"])
6. location: string describing place or setting (e.g. "Goa, Beach", "Old Manali Cafe")
7. activity: string describing occasion or event (e.g. "Sunset watching", "Ramp walk")
8. objects: list of strings (e.g. ["marksheet", "cake", "guitar"])
9. visual_attributes: list of strings (e.g. ["black and gold dress", "stage lights", "sunset"])
10. text_ocr: string of any visible printed text clues or null
11. uncertainty: string noting user doubts (e.g. "not sure about year") or null
12. suggested_refinements: list of 2-3 short prompt questions to help the user narrow down the search

Return ONLY valid JSON matching this schema with no markdown code fences or conversational text.
"""


def extract_cues_llm(query_text: str) -> Optional[Tuple[MemoryCues, List[str]]]:
    """Extracts memory cues using Groq API (LLaMA-3.3-70B)."""
    api_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
    if not api_key or api_key.startswith("gsk_your") or api_key == "disabled":
        return None

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        models_to_try = [settings.GROQ_MODEL, "llama-3.1-8b-instant", "llama3-70b-8192"]
        response = None
        last_error = None
        for m in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": CUE_EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": f"User Memory Description: \"{query_text}\""},
                    ],
                    temperature=0.1,
                    max_tokens=600,
                    response_format={"type": "json_object"},
                )
                if response and response.choices:
                    break
            except Exception as e:
                last_error = e
                continue
        
        if not response or not response.choices:
            logger.warning(f"Groq API cue extraction failed on all candidate models ({last_error}), falling back to deterministic extraction.")
            return None

        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)

        cues = MemoryCues(
            approximate_time=data.get("approximate_time"),
            normalized_year=data.get("normalized_year"),
            year_tolerance=data.get("year_tolerance", 1),
            season=data.get("season"),
            companions=data.get("companions", []),
            location=data.get("location"),
            activity=data.get("activity"),
            objects=data.get("objects", []),
            visual_attributes=data.get("visual_attributes", []),
            text_ocr=data.get("text_ocr"),
            uncertainty=data.get("uncertainty"),
        )
        suggestions = data.get("suggested_refinements", [])
        return cues, suggestions
    except Exception as e:
        logger.warning(f"Groq API cue extraction failed or rate limited ({e}), falling back to deterministic extraction.")
        return None


# ==============================================================================
# MAIN PUBLIC INTERFACE
# ==============================================================================

def extract_memory_cues(query_text: str) -> CueExtractionResponse:
    """Primary entrypoint: attempts Groq LLM extraction, falling back cleanly to deterministic parser."""
    clean_text = query_text.strip()
    if not clean_text:
        return CueExtractionResponse(
            query_text=clean_text,
            cues=MemoryCues(),
            suggested_refinements=["Describe what you remember about the moment"],
            extraction_source="deterministic_fallback",
        )

    # 1. Attempt LLM extraction if configured
    llm_result = extract_cues_llm(clean_text)
    if llm_result:
        cues, suggestions = llm_result
        return CueExtractionResponse(
            query_text=clean_text,
            cues=cues,
            suggested_refinements=suggestions,
            extraction_source="groq_llm",
        )

    # 2. Fall back to deterministic extraction
    fallback_cues, fallback_suggestions = extract_cues_deterministic(clean_text)
    return CueExtractionResponse(
        query_text=clean_text,
        cues=fallback_cues,
        suggested_refinements=fallback_suggestions,
        extraction_source="deterministic_fallback",
    )
