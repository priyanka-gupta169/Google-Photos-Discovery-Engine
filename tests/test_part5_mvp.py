"""Comprehensive Automated Test Suite for Part 5 MVP: Google Photos Memory Retrieval Assistant.

Verifies:
1. Cue extraction (AI & fallback)
2. Fallback cue extraction heuristics
3. Fuzzy temporal interpretation without exact calendar dates
4. Multi-cue hybrid scoring & candidate ranking
5. Distractor & collision handling
6. Iterative refinement with negative penalty on rejected candidates
7. Successful retrieval resolution
8. Session abandonment handling
9. Telemetry logging & persistence
10. End-to-end API contracts (/api/mvp/*)
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.mvp import MemoryCues, RepresentativePhoto, SearchRequest, RefineRequest, SessionTelemetry
from src.ai.cue_extractor import extract_memory_cues, extract_cues_deterministic
from src.retrieval.scoring import MemoryRetrievalEngine
from src.data.representative_dataset import get_representative_dataset, get_photo_by_id


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return MemoryRetrievalEngine()


# ==============================================================================
# 1. CUE EXTRACTION & DETERMINISTIC FALLBACK TESTS
# ==============================================================================

def test_cue_extraction_fallback_travel():
    """Tests deterministic extraction on a vague travel memory query."""
    query = "Trip to Goa with Rohan around 3 years back at a beach sunset"
    cues, refinements = extract_cues_deterministic(query)

    assert "Rohan" in cues.companions
    assert cues.location == "Goa"
    assert cues.normalized_year == 2023  # 2026 - 3
    assert "sunset" in [v.lower() for v in cues.visual_attributes] or cues.activity == "Sunset"
    assert isinstance(refinements, list)


def test_cue_extraction_fallback_marksheet():
    """Tests deterministic extraction on a utility document memory query."""
    query = "I need to find my university marksheet or degree certificate from college around 2022"
    cues, refinements = extract_cues_deterministic(query)

    assert cues.normalized_year == 2022
    assert cues.text_ocr is not None
    assert "marksheet" in cues.text_ocr or "marksheet" in cues.objects


def test_cue_extraction_fallback_ramp_walk():
    """Tests deterministic extraction on visual ambiguity memory query."""
    query = "Me and Maya doing a ramp walk on stage wearing a black and gold dress around college days"
    cues, refinements = extract_cues_deterministic(query)

    assert "Maya" in cues.companions
    assert cues.activity == "Ramp Walk"
    assert any("black and gold" in vis.lower() for vis in cues.visual_attributes)
    assert cues.normalized_year == 2022  # College normalization


def test_extract_memory_cues_public_function():
    """Tests extract_memory_cues handles empty and valid inputs gracefully."""
    empty_res = extract_memory_cues("")
    assert empty_res.status == "success"
    assert len(empty_res.cues.companions) == 0

    valid_res = extract_memory_cues("Family vacation in Kerala backwaters houseboat during monsoon 2024")
    assert valid_res.cues.location == "Kerala"
    assert valid_res.cues.normalized_year == 2024
    assert valid_res.cues.season == "Monsoon"


# ==============================================================================
# 2. REPRESENTATIVE DATASET INTEGRITY
# ==============================================================================

def test_representative_dataset_size_and_schema():
    """Tests that the controlled representative dataset contains exactly 40 valid assets."""
    dataset = get_representative_dataset()
    assert len(dataset) == 40

    task_1_targets = [p for p in dataset if p.ground_truth_task_id == "TASK-1"]
    task_2_targets = [p for p in dataset if p.ground_truth_task_id == "TASK-2"]
    task_3_targets = [p for p in dataset if p.ground_truth_task_id == "TASK-3"]

    assert len(task_1_targets) == 1
    assert task_1_targets[0].id == "PHOTO-007"

    assert len(task_2_targets) == 1
    assert task_2_targets[0].id == "PHOTO-031"

    assert len(task_3_targets) == 1
    assert task_3_targets[0].id == "PHOTO-023"

    for photo in dataset:
        assert photo.is_prototype_asset is True
        assert photo.id.startswith("PHOTO-")
        assert len(photo.title) > 0


# ==============================================================================
# 3. MULTI-CUE RETRIEVAL & SCORING TESTS
# ==============================================================================

def test_task_1_fuzzy_travel_retrieval(engine):
    """Tests Task 1: Locating Goa beach sunset with Rohan (~3 years ago)."""
    cues = MemoryCues(
        approximate_time="around 3 years ago",
        normalized_year=2023,
        year_tolerance=1,
        companions=["Rohan"],
        location="Goa",
        activity="Sunset",
        visual_attributes=["beach", "sunset", "outdoors"],
    )

    results = engine.search(cues)
    assert results.total_candidates > 0

    top_candidate = results.results[0]
    assert top_candidate.photo.id == "PHOTO-007"  # Target photo!
    assert top_candidate.confidence_level == "HIGH_CONFIDENCE"
    assert any("Rohan" in reason for reason in top_candidate.match_reasons)
    assert any("Goa" in reason for reason in top_candidate.match_reasons)


def test_task_2_utility_document_retrieval(engine):
    """Tests Task 2: Locating university marksheet from ~2022."""
    cues = MemoryCues(
        approximate_time="around 2022",
        normalized_year=2022,
        year_tolerance=1,
        objects=["Marksheet"],
        visual_attributes=["marksheet", "document scan"],
        text_ocr="marksheet grade sheet exam degree",
    )

    results = engine.search(cues)
    assert results.total_candidates > 0

    top_candidate = results.results[0]
    assert top_candidate.photo.id == "PHOTO-031"  # Target degree marksheet!
    assert any("Document Text Match" in reason or "Marksheet" in reason for reason in top_candidate.match_reasons)


def test_task_3_visual_collision_and_refinement(engine):
    """Tests Task 3: Disambiguating college ramp walk vs. annual dinner in same black and gold dress."""
    # 1. Initial vague cue matches both ramp walk (PHOTO-023) and dinner (PHOTO-037)
    initial_cues = MemoryCues(
        approximate_time="college days",
        normalized_year=2022,
        year_tolerance=1,
        visual_attributes=["black and gold dress"],
    )

    initial_search = engine.search(initial_cues)
    candidate_ids = [c.photo.id for c in initial_search.results[:5]]
    assert "PHOTO-023" in candidate_ids
    assert "PHOTO-037" in candidate_ids

    # 2. Refinement: User indicates it was on stage during a ramp walk, and rejects the dinner photo
    refine_res = engine.refine(
        previous_cues=initial_cues,
        new_clue_text="It was a ramp walk on stage under spotlights with Maya",
        rejected_photo_ids=["PHOTO-037"],
    )

    assert refine_res.results[0].photo.id == "PHOTO-023"  # Ramp walk now top!
    # Verified: Rejected photo is excluded or dropped to bottom
    new_candidate_ids = [c.photo.id for c in refine_res.results]
    assert "PHOTO-037" not in new_candidate_ids


# ==============================================================================
# 4. API CONTRACT & INTEGRATION TESTS
# ==============================================================================

def test_api_mvp_health(client):
    """Tests /api/mvp/health returns healthy status and 40 records."""
    res = client.get("/api/mvp/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["dataset_records_count"] == 40


def test_api_mvp_dataset(client):
    """Tests /api/mvp/dataset returns all 40 representative assets."""
    res = client.get("/api/mvp/dataset")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 40
    assert data[0]["is_prototype_asset"] is True


def test_api_mvp_extract_cues(client):
    """Tests /api/mvp/extract-cues endpoint."""
    res = client.post("/api/mvp/extract-cues", json={"query_text": "trip to goa with rohan around 3 years back"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "Rohan" in data["cues"]["companions"]
    assert data["cues"]["location"] == "Goa"


def test_api_mvp_search(client):
    """Tests /api/mvp/search endpoint."""
    res = client.post(
        "/api/mvp/search",
        json={
            "cues": {
                "approximate_time": "~2023",
                "normalized_year": 2023,
                "companions": ["Rohan"],
                "location": "Goa",
                "visual_attributes": ["beach"],
            }
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_candidates"] > 0
    assert data["results"][0]["photo"]["id"] == "PHOTO-007"


def test_api_mvp_refine(client):
    """Tests /api/mvp/refine endpoint."""
    res = client.post(
        "/api/mvp/refine",
        json={
            "previous_cues": {
                "approximate_time": "~2022",
                "normalized_year": 2022,
                "visual_attributes": ["black and gold dress"],
            },
            "new_clue_text": "On stage ramp walk with Maya",
            "rejected_photo_ids": ["PHOTO-037"],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["results"][0]["photo"]["id"] == "PHOTO-023"


def test_api_mvp_telemetry_logging_success_and_abandonment(client):
    """Tests /api/mvp/log-session records both successful retrieval and abandonment."""
    # 1. Log Successful Session
    success_payload = {
        "session_id": "test-session-001",
        "task_id": "TASK-1",
        "initial_query": "trip to goa with rohan around 3 years back",
        "extracted_cues": {"companions": ["Rohan"], "location": "Goa"},
        "retrieval_attempts": 2,
        "refinements_count": 1,
        "candidate_count": 3,
        "timeline_available": False,
        "user_selected_result": True,
        "selected_photo_id": "PHOTO-007",
        "final_outcome": "SUCCESS",
        "completion_time_seconds": 18.5,
        "seq_score": 6,
    }
    res_success = client.post("/api/mvp/log-session", json=success_payload)
    assert res_success.status_code == 200
    assert res_success.json()["status"] == "success"

    # 2. Log Abandonment Session
    abandon_payload = {
        "session_id": "test-session-002",
        "task_id": "FREEFORM",
        "initial_query": "looking for an obscure paper document",
        "extracted_cues": {"objects": ["document"]},
        "retrieval_attempts": 4,
        "refinements_count": 3,
        "candidate_count": 0,
        "timeline_available": False,
        "user_selected_result": False,
        "final_outcome": "ABANDONED",
        "completion_time_seconds": 45.2,
        "abandonment_reason": "Results were too broad after 3 refinements",
    }
    res_abandon = client.post("/api/mvp/log-session", json=abandon_payload)
    assert res_abandon.status_code == 200
    assert res_abandon.json()["status"] == "success"

    # 3. Retrieve Telemetry Audit
    res_audit = client.get("/api/mvp/telemetry")
    assert res_audit.status_code == 200
    sessions = res_audit.json()
    session_ids = [s["session_id"] for s in sessions]
    assert "test-session-001" in session_ids
    assert "test-session-002" in session_ids
