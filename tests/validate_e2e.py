"""End-to-End Validation Script for Part 5 MVP Tasks.

Validates:
Task 1: Fuzzy travel memory (Rohan, Anjuna beach, sunset, ~3 years ago -> PHOTO-007)
Task 2: Utility document / screenshot / ticket (semester 6 marksheet 2022 -> PHOTO-031)
Task 3: Visual ambiguity across similar events (yellow dress, dancing with Priya -> PHOTO-023 disambiguated from PHOTO-037)
Followed by session telemetry logging and verification.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.api.main import app
import json

def run_validation():
    client = TestClient(app)
    print("=" * 60)
    print("STARTING PART 5 MVP END-TO-END VALIDATION")
    print("=" * 60)

    # -------------------------------------------------------------
    # TASK 1: FUZZY TRAVEL MEMORY
    # -------------------------------------------------------------
    print("\n--- TASK 1: Fuzzy Travel Memory ---")
    query1 = "I am looking for a photo with Rohan at Anjuna beach around sunset about 3 years ago"
    print(f"Memory Input: '{query1}'")
    
    r1_extract = client.post("/api/mvp/extract-cues", json={"query_text": query1})
    assert r1_extract.status_code == 200, f"Extraction failed: {r1_extract.text}"
    ext1 = r1_extract.json()
    cues1 = ext1["cues"]
    print("Extracted Cues:")
    for k, v in cues1.items():
        if v:
            print(f"  [{k}]: {v}")
    
    r1_search = client.post("/api/mvp/search", json={"cues": cues1, "active_task_id": "TASK-1"})
    assert r1_search.status_code == 200, f"Search failed: {r1_search.text}"
    res1 = r1_search.json()
    candidates1 = res1["results"]
    assert len(candidates1) > 0, "No candidates returned"
    
    top1 = candidates1[0]
    print(f"\nTop Candidate: {top1['photo']['id']} - {top1['photo']['title']}")
    print(f"Match Score: {top1['score']} ({top1['confidence_level']})")
    print("Match Rationale:")
    for r in top1["match_reasons"]:
        safe_r = r.encode("ascii", "replace").decode("ascii")
        print(f"  {safe_r}")
    
    assert top1["photo"]["id"] == "PHOTO-007", f"Expected PHOTO-007, got {top1['photo']['id']}"
    print(">>> TASK 1 PASSED: Ground truth PHOTO-007 retrieved at Rank 1.")

    # -------------------------------------------------------------
    # TASK 2: UTILITY DOCUMENT / SCREENSHOT
    # -------------------------------------------------------------
    print("\n--- TASK 2: Utility Document (Semester 6 Marksheet) ---")
    query2 = "Looking for a document screenshot of my semester 6 marksheet or grade sheet with roll number from college around 2022"
    print(f"Memory Input: '{query2}'")
    
    r2_extract = client.post("/api/mvp/extract-cues", json={"query_text": query2})
    assert r2_extract.status_code == 200, f"Extraction failed: {r2_extract.text}"
    ext2 = r2_extract.json()
    cues2 = ext2["cues"]
    print("Extracted Cues:")
    for k, v in cues2.items():
        if v:
            print(f"  [{k}]: {v}")
    
    r2_search = client.post("/api/mvp/search", json={"cues": cues2, "active_task_id": "TASK-2"})
    assert r2_search.status_code == 200
    res2 = r2_search.json()
    candidates2 = res2["results"]
    assert len(candidates2) > 0
    
    top2 = candidates2[0]
    print(f"\nTop Candidate: {top2['photo']['id']} - {top2['photo']['title']}")
    print(f"Match Score: {top2['score']} ({top2['confidence_level']})")
    print("Match Rationale:")
    for r in top2["match_reasons"]:
        safe_r = r.encode("ascii", "replace").decode("ascii")
        print(f"  {safe_r}")
    
    assert top2["photo"]["id"] == "PHOTO-031", f"Expected PHOTO-031, got {top2['photo']['id']}"
    print(">>> TASK 2 PASSED: Ground truth PHOTO-031 retrieved at Rank 1.")

    # -------------------------------------------------------------
    # TASK 3: VISUAL AMBIGUITY & REFINEMENT
    # -------------------------------------------------------------
    print("\n--- TASK 3: Visual Ambiguity Across Similar Events ---")
    query3 = "Me wearing a black and gold dress around 2022 during college days"
    print(f"Memory Input: '{query3}'")
    
    r3_extract = client.post("/api/mvp/extract-cues", json={"query_text": query3})
    assert r3_extract.status_code == 200
    ext3 = r3_extract.json()
    cues3 = ext3["cues"]
    
    r3_search = client.post("/api/mvp/search", json={"cues": cues3, "active_task_id": "TASK-3"})
    assert r3_search.status_code == 200
    res3 = r3_search.json()
    
    print("\nInitial Candidates (Both PHOTO-023 and distractor PHOTO-037 in pool):")
    initial_ids = [c["photo"]["id"] for c in res3["results"]]
    for c in res3["results"][:4]:
        print(f"  [{c['photo']['id']}] {c['photo']['title']} - Score: {c['score']}")
    
    assert "PHOTO-023" in initial_ids, "Target PHOTO-023 should be in initial candidates"
    assert "PHOTO-037" in initial_ids, "Collision distractor PHOTO-037 should be in initial candidates"
    
    # User notices PHOTO-037 (Formal Dinner in same black & gold dress) is NOT the photo,
    # adds additional clue about ramp walk on stage under spotlights with Maya, and marks PHOTO-037 as 'Not this'
    print("\nUser provides Refinement: Rejects PHOTO-037 (Annual Dinner), adds clue: 'It was the fashion show ramp walk on stage under spotlights with Maya'")
    r3_refine = client.post("/api/mvp/refine", json={
        "previous_cues": cues3,
        "new_clue_text": "It was the fashion show ramp walk on auditorium stage under spotlights with Maya",
        "rejected_photo_ids": ["PHOTO-037"],
        "active_task_id": "TASK-3"
    })
    assert r3_refine.status_code == 200
    res3_refined = r3_refine.json()
    
    print("\nRefined Top 3 Candidates (After Refinement):")
    for c in res3_refined["results"][:3]:
        safe_reasons = ", ".join(c["match_reasons"]).encode("ascii", "replace").decode("ascii")
        print(f"  [{c['photo']['id']}] {c['photo']['title']} - Score: {c['score']}")
        print(f"    Reasons: {safe_reasons}")
    
    top3 = res3_refined["results"][0]
    assert top3["photo"]["id"] == "PHOTO-023", f"Expected PHOTO-023, got {top3['photo']['id']}"
    
    # Verify PHOTO-037 was penalized
    rejected_matches = [c for c in res3_refined["results"] if c["photo"]["id"] == "PHOTO-037"]
    if rejected_matches:
        print(f"Penalized Distractor PHOTO-037 Score: {rejected_matches[0]['score']}")
        assert rejected_matches[0]["score"] < top3["score"]
    
    print(">>> TASK 3 PASSED: Distractor resolved, PHOTO-023 ranked #1 after refinement.")

    # -------------------------------------------------------------
    # TELEMETRY LOGGING
    # -------------------------------------------------------------
    print("\n--- Telemetry Logging Validation ---")
    log_payload = {
        "session_id": "sess-val-e2e-001",
        "task_id": "TASK-1",
        "initial_query": query1,
        "extracted_cues": cues1,
        "retrieval_attempts": 1,
        "refinements_count": 0,
        "candidate_count": len(candidates1),
        "timeline_available": True,
        "user_selected_result": True,
        "selected_photo_id": "PHOTO-007",
        "final_outcome": "SUCCESS",
        "completion_time_seconds": 18.2,
        "seq_score": 6,
        "abandonment_reason": None
    }
    r_log = client.post("/api/mvp/log-session", json=log_payload)
    assert r_log.status_code == 200, f"Logging failed: {r_log.text}"
    print(f"Log Session Response: {r_log.json()}")

    # Check aggregation endpoint
    r_summary = client.get("/api/mvp/telemetry")
    assert r_summary.status_code == 200
    sessions = r_summary.json()
    assert isinstance(sessions, list)
    print(f"\nTelemetry Sessions Captured: {len(sessions)}")
    last_sess = sessions[-1]
    print(f"  Last Session ID: {last_sess['session_id']}")
    print(f"  Task ID: {last_sess['task_id']}")
    print(f"  Outcome: {last_sess['final_outcome']}")
    print(f"  Selected Photo: {last_sess['selected_photo_id']}")
    print(f"  Completion Time: {last_sess['completion_time_seconds']}s")
    print(f"  SEQ Score: {last_sess['seq_score']}")

    print("\n" + "=" * 60)
    print("ALL 3 END-TO-END TASKS & TELEMETRY VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_validation()
