"""FastAPI Router for Part 5 MVP: Google Photos Memory Retrieval Assistant.

Exposes REST endpoints for:
- POST /api/mvp/extract-cues: AI & fallback memory cue extraction
- POST /api/mvp/search: Multi-cue candidate retrieval and scoring
- POST /api/mvp/refine: Iterative refinement and compound re-scoring
- GET  /api/mvp/dataset: Complete representative photo catalog
- POST /api/mvp/log-session: Session telemetry logging
- GET  /api/mvp/telemetry: Telemetry audit & evaluation logs
- GET  /api/mvp/health: MVP subsystem health check
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import json
import sqlite3

from src.models.mvp import (
    CueExtractionRequest,
    CueExtractionResponse,
    SearchRequest,
    SearchResponse,
    RefineRequest,
    RefineResponse,
    SessionTelemetry,
    RepresentativePhoto,
)
from src.ai.cue_extractor import extract_memory_cues
from src.retrieval.scoring import MemoryRetrievalEngine
from src.data.representative_dataset import get_representative_dataset
from src.config.settings import settings
from src.config.logger import logger


router = APIRouter(prefix="/api/mvp", tags=["Part 5: Memory Retrieval Assistant MVP"])

# Singleton retrieval engine instance over the 40-record dataset
engine = MemoryRetrievalEngine()

# In-memory telemetry cache for real-time evaluation
IN_MEMORY_SESSIONS: List[SessionTelemetry] = []


def get_telemetry_db():
    """Returns SQLite connection for telemetry logging."""
    db_path = Path(settings.DATA_ANALYSIS_DIR) / "discovery.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mvp_telemetry (
            session_id TEXT PRIMARY KEY,
            task_id TEXT,
            initial_query TEXT,
            extracted_cues TEXT,
            retrieval_attempts INTEGER,
            refinements_count INTEGER,
            candidate_count INTEGER,
            timeline_available INTEGER,
            user_selected_result INTEGER,
            selected_photo_id TEXT,
            final_outcome TEXT,
            completion_time_seconds REAL,
            seq_score INTEGER,
            abandonment_reason TEXT,
            timestamp TEXT
        )
        """
    )
    conn.commit()
    return conn


# ==============================================================================
# ENDPOINT IMPLEMENTATIONS
# ==============================================================================

@router.get("/health", summary="MVP Subsystem Health Check")
def mvp_health() -> Dict[str, Any]:
    """Returns the health status and dataset readiness of the MVP assistant."""
    dataset = get_representative_dataset()
    return {
        "status": "healthy",
        "service": "Google Photos Memory Retrieval Assistant MVP",
        "dataset_records_count": len(dataset),
        "groq_configured": bool(settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("gsk_your")),
        "active_sessions_logged": len(IN_MEMORY_SESSIONS),
    }


@router.post("/extract-cues", response_model=CueExtractionResponse, summary="Extract Memory Cues from Freeform Text")
def extract_cues_endpoint(req: CueExtractionRequest) -> CueExtractionResponse:
    """Parses natural-language memory into structured 8-dimensional retrieval cues."""
    try:
        response = extract_memory_cues(req.query_text)
        return response
    except Exception as e:
        logger.error(f"Error extracting memory cues: {e}")
        raise HTTPException(status_code=500, detail=f"Cue extraction failed: {str(e)}")


@router.post("/search", response_model=SearchResponse, summary="Search Representative Photo Dataset")
def search_endpoint(req: SearchRequest) -> SearchResponse:
    """Scores and ranks representative photos based on extracted memory cues."""
    try:
        results = engine.search(
            cues=req.cues,
            rejected_ids=req.rejected_ids,
        )
        return results
    except Exception as e:
        logger.error(f"Error performing multi-cue search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/refine", response_model=RefineResponse, summary="Iterative Search Refinement")
def refine_endpoint(req: RefineRequest) -> RefineResponse:
    """Merges new memory clues into working context and re-scores candidate pool."""
    try:
        refined = engine.refine(
            previous_cues=req.previous_cues,
            new_clue_text=req.new_clue_text,
            selected_chip=req.selected_chip,
            rejected_photo_ids=req.rejected_photo_ids,
            active_task_id=req.active_task_id,
        )
        return refined
    except Exception as e:
        logger.error(f"Error during search refinement: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


@router.get("/dataset", response_model=List[RepresentativePhoto], summary="Get Representative Photo Catalog")
def get_dataset_endpoint() -> List[RepresentativePhoto]:
    """Returns the full 40-record representative photo dataset for audit and verification."""
    return get_representative_dataset()


@router.post("/log-session", summary="Log Retrieval Session Telemetry")
def log_session_endpoint(telemetry: SessionTelemetry) -> Dict[str, Any]:
    """Logs evaluation session telemetry to in-memory store and SQLite database."""
    try:
        # Cache in memory
        IN_MEMORY_SESSIONS.append(telemetry)

        # Persist to SQLite
        conn = get_telemetry_db()
        conn.execute(
            """
            INSERT OR REPLACE INTO mvp_telemetry (
                session_id, task_id, initial_query, extracted_cues, retrieval_attempts,
                refinements_count, candidate_count, timeline_available, user_selected_result,
                selected_photo_id, final_outcome, completion_time_seconds, seq_score,
                abandonment_reason, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telemetry.session_id,
                telemetry.task_id,
                telemetry.initial_query,
                json.dumps(telemetry.extracted_cues),
                telemetry.retrieval_attempts,
                telemetry.refinements_count,
                telemetry.candidate_count,
                1 if telemetry.timeline_available else 0,
                1 if telemetry.user_selected_result else 0,
                telemetry.selected_photo_id,
                telemetry.final_outcome,
                telemetry.completion_time_seconds,
                telemetry.seq_score,
                telemetry.abandonment_reason,
                telemetry.timestamp,
            ),
        )
        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Session telemetry successfully recorded.",
            "session_id": telemetry.session_id,
            "final_outcome": telemetry.final_outcome,
        }
    except Exception as e:
        logger.error(f"Error recording telemetry session: {e}")
        # Even if SQLite write fails, in-memory is captured
        return {"status": "partial_success", "session_id": telemetry.session_id, "error": str(e)}


@router.get("/telemetry", summary="Retrieve Logged Evaluation Sessions")
def get_telemetry_endpoint() -> List[SessionTelemetry]:
    """Retrieves all logged retrieval sessions for Part 6 validation analysis."""
    return IN_MEMORY_SESSIONS
