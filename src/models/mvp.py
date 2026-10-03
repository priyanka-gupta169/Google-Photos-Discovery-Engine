"""Pydantic Models for Part 5 AI-Native MVP: Google Photos Memory Retrieval Assistant.

Defines schemas for:
- Memory cue extraction
- Representative photo dataset records
- Multi-cue hybrid search requests and responses
- Iterative refinement dialogues and candidate re-ranking
- Session telemetry logging and task completion
"""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone


# ==============================================================================
# MEMORY CUE TAXONOMY (8 Dimensions)
# ==============================================================================

class MemoryCues(BaseModel):
    """Structured representation of human episodic memory cues."""
    approximate_time: Optional[str] = Field(
        None, description="Fuzzy or relative temporal cue (e.g. 'about 3 years back', 'college days', 'summer 2022')"
    )
    normalized_year: Optional[int] = Field(
        None, description="Normalized anchor year if inferable without forcing exact calendar date"
    )
    year_tolerance: int = Field(
        1, description="Acceptable temporal window tolerance in years"
    )
    season: Optional[str] = Field(
        None, description="Season or time of year (e.g. 'winter', 'monsoon', 'summer')"
    )
    companions: List[str] = Field(
        default_factory=list, description="Names or roles of people present (e.g. ['Rohan', 'friend', 'sister'])"
    )
    location: Optional[str] = Field(
        None, description="Geographic or spatial setting (e.g. 'Goa', 'beach', 'cafe', 'campus')"
    )
    activity: Optional[str] = Field(
        None, description="Episodic event or activity (e.g. 'sunset watching', 'ramp walk', 'dinner')"
    )
    objects: List[str] = Field(
        default_factory=list, description="Prominent physical items or documents (e.g. ['marksheet', 'guitar', 'ticket'])"
    )
    visual_attributes: List[str] = Field(
        default_factory=list, description="Distinctive visual cues (e.g. ['black and gold dress', 'golden hour', 'stage lights'])"
    )
    text_ocr: Optional[str] = Field(
        None, description="Visible printed or handwritten text on documents/screenshots"
    )
    uncertainty: Optional[str] = Field(
        None, description="Linguistic hedges indicating user doubt (e.g. 'maybe 2022 or 2023', 'not sure about location')"
    )


# ==============================================================================
# REPRESENTATIVE PHOTO DATASET SCHEMA
# ==============================================================================

class RepresentativePhoto(BaseModel):
    """Schema for a controlled representative photo asset in the prototype dataset."""
    id: str = Field(..., description="Unique photo identifier (e.g. PHOTO-001)")
    title: str = Field(..., description="Human-readable title describing the moment")
    category: Literal["Travel", "Social & Family", "Distinctive Event", "Utility & Document", "Visual Collision"] = Field(
        ..., description="Photo category"
    )
    approx_year: int = Field(..., description="Calendar year photo was taken")
    season: Optional[str] = Field(None, description="Season of capture")
    people: List[str] = Field(default_factory=list, description="Tagged people/companions")
    location: str = Field(..., description="Setting or place")
    activity: str = Field(..., description="Main activity or occasion")
    visual_tags: List[str] = Field(default_factory=list, description="Visual and aesthetic tags")
    text_ocr: Optional[str] = Field(None, description="OCR text if document or screenshot")
    thumbnail_url: str = Field(..., description="Path or URL to photo thumbnail")
    description: str = Field(..., description="Detailed description of the visual scene")
    ground_truth_task_id: Optional[str] = Field(
        None, description="Associated evaluation task ID if ground truth target (e.g. TASK-1)"
    )
    is_distractor: bool = Field(
        False, description="Whether this photo is an intentional distractor for a task"
    )
    is_prototype_asset: bool = Field(
        True, description="Invariant: always True to mark representative prototype asset"
    )


# ==============================================================================
# SEARCH & RETRIEVAL CONTRACTS
# ==============================================================================

class CueExtractionRequest(BaseModel):
    """User input to extract memory cues."""
    query_text: str = Field(..., description="Natural language memory description")


class CueExtractionResponse(BaseModel):
    """Structured extraction output from AI or fallback."""
    status: str = "success"
    query_text: str
    cues: MemoryCues
    suggested_refinements: List[str] = Field(
        default_factory=list, description="Intelligent prompt suggestions for missing dimensions"
    )
    extraction_source: Literal["groq_llm", "deterministic_fallback"] = "deterministic_fallback"


class ScoredCandidate(BaseModel):
    """A representative photo scored against active memory cues."""
    photo: RepresentativePhoto
    score: float = Field(..., description="Composite match score (0.0 to 10.0+)")
    match_reasons: List[str] = Field(
        default_factory=list, description="Human-understandable bullet points explaining why it matched"
    )
    event_cluster: str = Field(..., description="Episodic event grouping (e.g. 'Goa Vacation (~2023)')")
    confidence_level: Literal["HIGH_CONFIDENCE", "EXPLORATORY", "LOW_MATCH"] = "EXPLORATORY"


class SearchRequest(BaseModel):
    """Request to search candidate photos using extracted cues."""
    cues: MemoryCues
    active_task_id: Optional[str] = None
    query_text: Optional[str] = None
    rejected_ids: List[str] = Field(default_factory=list, description="IDs of photos explicitly rejected by user")


class SearchResponse(BaseModel):
    """Ranked candidate results returned to user."""
    total_candidates: int
    results: List[ScoredCandidate]
    active_cues: MemoryCues
    event_clusters: List[str] = Field(default_factory=list)


class RefineRequest(BaseModel):
    """Request to refine an existing search session."""
    previous_cues: MemoryCues
    new_clue_text: str = Field(..., description="Additional natural language memory detail")
    selected_chip: Optional[str] = Field(None, description="Optional clicked facet chip")
    rejected_photo_ids: List[str] = Field(default_factory=list, description="Photos marked as 'Not this'")
    active_task_id: Optional[str] = None


class RefineResponse(BaseModel):
    """Response containing updated cues and re-ranked candidate pool."""
    status: str = "success"
    system_message: str
    updated_cues: MemoryCues
    total_candidates: int
    results: List[ScoredCandidate]
    suggested_refinements: List[str] = Field(default_factory=list)


# ==============================================================================
# TELEMETRY & LOGGING CONTRACTS
# ==============================================================================

class SessionTelemetry(BaseModel):
    """Telemetry captured during a prototype retrieval session."""
    session_id: str
    task_id: Optional[str] = None
    initial_query: str
    extracted_cues: Dict[str, Any]
    retrieval_attempts: int = 1
    refinements_count: int = 0
    candidate_count: int = 0
    timeline_available: bool = False
    user_selected_result: bool = False
    selected_photo_id: Optional[str] = None
    final_outcome: Literal["SUCCESS", "ABANDONED", "IN_PROGRESS"] = "IN_PROGRESS"
    completion_time_seconds: float = 0.0
    seq_score: Optional[int] = Field(None, description="Single-Ease Question score (1-7)")
    abandonment_reason: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LogSessionRequest(SessionTelemetry):
    """Request payload to log completed or abandoned session."""
    pass
